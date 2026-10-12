"""Shared thread-pool tasks with GUI-thread delivery and cooperative cancellation."""
import logging
import threading
import time
import weakref

from PySide6.QtCore import QObject, QRunnable, QThread, QThreadPool, QTimer, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication
from shiboken6 import isValid


# Keep both the receiver and the runnable's signal object alive until delivery.
_ACTIVE_TASKS = set()


class _WorkerSignals(QObject):
    success = Signal(object)
    failure = Signal(object)


class _Worker(QRunnable):
    def __init__(self, fn, args, kwargs, cancel_event):
        super().__init__()
        self.fn, self.args, self.kwargs = fn, args, kwargs
        self.cancel_event = cancel_event
        self.signals = _WorkerSignals()

    def run(self):
        try:
            result = None if self.cancel_event.is_set() else self.fn(*self.args, **self.kwargs)
        except Exception as exc:
            try:
                self.signals.failure.emit(exc)
            except RuntimeError:
                pass
        else:
            try:
                self.signals.success.emit(result)
            except RuntimeError:
                pass


class MkTask(QObject):
    """Task handle. Signals and callbacks run on the GUI thread.

    ``cancel()`` suppresses delivery immediately; it never forcibly stops a thread.
    A cooperative worker can inspect ``cancel_event``. Completed handles remain
    readable while retained by the caller. Create/cancel handles on the GUI thread.
    """

    succeeded = Signal(object)
    failed = Signal(object)
    cancelled = Signal()
    finished = Signal()
    stateChanged = Signal(str)

    def __init__(self, owner, fn, args, kwargs, on_success, on_error,
                 auto_loading, loading_delay_ms, min_loading_ms, task_key,
                 pass_cancel_event):
        super().__init__(QApplication.instance())
        self._owner = weakref.ref(owner)
        self._on_success, self._on_error = on_success, on_error
        self._auto_loading = auto_loading
        self._min_loading_ms = max(0, int(min_loading_ms))
        self._key = task_key
        self._state = "running"
        self._worker_done = False
        self._delivering = False
        self.result = None
        self.error = None
        self.cancel_event = threading.Event()
        self._delay = QTimer(self)
        self._delay.setSingleShot(True)
        self._delay.timeout.connect(self._show_loading)
        self._delivery = QTimer(self)
        self._delivery.setSingleShot(True)
        self._delivery.timeout.connect(self._deliver)
        if pass_cancel_event:
            if "cancel_event" in kwargs:
                raise TypeError("cancel_event is reserved when pass_cancel_event=True")
            kwargs = dict(kwargs, cancel_event=self.cancel_event)
        self._worker = _Worker(fn, args, kwargs, self.cancel_event)
        self._worker.signals.success.connect(self._receive_success, Qt.ConnectionType.QueuedConnection)
        self._worker.signals.failure.connect(self._receive_failure, Qt.ConnectionType.QueuedConnection)
        owner.destroyed.connect(self._owner_destroyed)
        self._loading_delay_ms = max(0, int(loading_delay_ms))

    @property
    def state(self):
        return self._state

    @property
    def done(self):
        return self._state != "running"

    def _live_owner(self):
        owner = self._owner()
        return owner if owner is not None and isValid(owner) else None

    def _start(self):
        _ACTIVE_TASKS.add(self)
        owner = self._live_owner()
        if self._auto_loading:
            pending = getattr(owner, "_mk_loading_tasks", None)
            if pending is None:
                owner._mk_loading_tasks = pending = set()
            pending.add(self)
        if self._key is not None:
            tasks = getattr(owner, "_mk_keyed_tasks", None)
            if tasks is None:
                owner._mk_keyed_tasks = tasks = {}
            previous = tasks.get(self._key)
            tasks[self._key] = self
            # Register the replacement first to avoid a loading-state flash.
            if previous is not None:
                previous.cancel()
        if self._auto_loading:
            if self._loading_delay_ms:
                self._delay.start(self._loading_delay_ms)
            else:
                self._show_loading()
        QThreadPool.globalInstance().start(self._worker)

    @Slot()
    def _show_loading(self):
        owner = self._live_owner()
        if owner is not None and not self.done and not getattr(owner, "_mk_task_loading_visible", False):
            owner._mk_task_loading_visible = True
            owner._mk_task_loading_started = time.monotonic()
            try:
                owner.set_loading(True)
            except Exception:
                logging.exception("MonkeyQt loading presentation failed")

    @Slot(object)
    def _receive_success(self, result):
        self.result = result
        self._received()

    @Slot(object)
    def _receive_failure(self, error):
        self.error = error
        self._received()

    def _received(self):
        self._worker_done = True
        self._delay.stop()
        if self.done:
            self.result = self.error = None
            self._release()
            return
        owner = self._live_owner()
        if owner is None:
            self.cancel()
            return
        remaining = 0
        if self._auto_loading and getattr(owner, "_mk_task_loading_visible", False):
            elapsed = (time.monotonic() - owner._mk_task_loading_started) * 1000
            remaining = max(0, int(self._min_loading_ms - elapsed))
        if remaining:
            self._delivery.start(remaining)
        else:
            self._deliver()

    @Slot()
    def _deliver(self):
        if self.done:
            return
        if self._live_owner() is None:
            self.cancel()
            return
        self._delivering = True
        try:
            if self.error is None and self._on_success is not None:
                try:
                    self._on_success(self.result)
                except Exception as exc:
                    self.error = exc
            if self.done:  # A callback may navigate away or replace this task.
                return
            if self.error is not None:
                if self._on_error is not None:
                    try:
                        self._on_error(self.error)
                    except Exception:
                        logging.exception("MonkeyQt task error callback failed")
                else:
                    logging.error("MonkeyQt task failed: %s", self.error)
            if self.done:
                return
            self._state = "failed" if self.error is not None else "succeeded"
            # Commit content before removing its loading mask.
            self._clear_loading()
            self.stateChanged.emit(self._state)
            if self.error is None:
                self.succeeded.emit(self.result)
            else:
                self.failed.emit(self.error)
            self.finished.emit()
        finally:
            self._delivering = False
            if self.done:
                self._release()

    @Slot()
    def cancel(self):
        if QThread.currentThread() != self.thread():
            raise RuntimeError("MkTask.cancel() must run on the GUI thread")
        if self.done:
            return
        self.cancel_event.set()
        self._delay.stop()
        self._delivery.stop()
        self._state = "cancelled"
        self._on_success = self._on_error = None
        self.result = self.error = None
        self._clear_loading()
        self.stateChanged.emit(self._state)
        self.cancelled.emit()
        self.finished.emit()
        self._release()

    @Slot()
    def _owner_destroyed(self):
        self.cancel()

    def _clear_loading(self):
        owner = self._live_owner()
        if owner is None:
            return
        if self._auto_loading:
            pending = getattr(owner, "_mk_loading_tasks", set())
            pending.discard(self)
            if not pending and getattr(owner, "_mk_task_loading_visible", False):
                owner._mk_task_loading_visible = False
                try:
                    owner.set_loading(False)
                except Exception:
                    logging.exception("MonkeyQt loading cleanup failed")
        tasks = getattr(owner, "_mk_keyed_tasks", {})
        if self._key is not None and tasks.get(self._key) is self:
            tasks.pop(self._key)

    def _release(self):
        if not self.done or not self._worker_done or self._delivering:
            return
        owner = self._live_owner()
        if owner is not None:
            try:
                owner.destroyed.disconnect(self._owner_destroyed)
            except (RuntimeError, TypeError):
                pass
        self._on_success = self._on_error = None
        self._worker = None
        _ACTIVE_TASKS.discard(self)
        self.setParent(None)


def start_task(owner, worker_fn, *args, on_success=None, on_error=None,
               auto_loading=True, loading_delay_ms=150, min_loading_ms=0,
               task_key=None, pass_cancel_event=False, **kwargs):
    """Start a task; equal non-None keys replace previous tasks on this owner."""
    app = QApplication.instance()
    if app is None or QThread.currentThread() != app.thread():
        raise RuntimeError("run_async() must be called on the GUI thread")
    if not callable(worker_fn):
        raise TypeError("worker_fn must be callable")
    if task_key is not None:
        hash(task_key)
    task = MkTask(owner, worker_fn, args, kwargs, on_success, on_error,
                  auto_loading, loading_delay_ms, min_loading_ms, task_key,
                  pass_cancel_event)
    task._start()
    return task
