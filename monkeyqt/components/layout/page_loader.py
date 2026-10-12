"""Reusable page loading states, refresh retention and latest-result delivery."""
from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QStackedWidget, QWidget
from shiboken6 import isValid

from monkeyqt.components.layout.widget import MkQWidget


class MkPageLoader(MkQWidget):
    """Host a lightweight page before loading its data in the thread pool.

    ``on_success`` applies data to widgets on the GUI thread. An ``is_empty``
    predicate can customize the empty state. Workers must not access QWidget.
    Refresh keeps existing content by default. Equal loads replace prior tasks.
    Hiding a page does not cancel it automatically; call cancel() on route exit
    when that is the desired policy. Destruction always suppresses delivery.
    """
    stateChanged = Signal(str)
    loaded = Signal(object)
    loadFailed = Signal(object)
    retryRequested = Signal()

    def __init__(self, content=None, skeleton=None, parent=None, *,
                 loading_delay_ms=150, retain_content=True,
                 empty_text="暂无数据", error_text="加载失败，请重试"):
        from monkeyqt.components.basic.button import MkButton
        from monkeyqt.components.feedback.skeleton import MkSkeleton
        super().__init__(parent, layout="v", margins=0, spacing=8)
        self.setProperty("mk_auto_loading", False)
        self.setProperty("mk_loading_boundary", True)
        self._state = self._settled_state = "idle"
        self._has_content = False
        self._generation = 0
        self._task = None
        self._retry_spec = None
        self._retain_content = bool(retain_content)
        self._loading_delay_ms = max(0, int(loading_delay_ms))
        self._empty_text, self._error_text = empty_text, error_text
        self._result = None
        self._status = QWidget(self)
        status_layout = QHBoxLayout(self._status)
        status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_label = QLabel(self._status)
        self.status_label.setWordWrap(True)
        self.retry_button = MkButton("重试", self._status)
        self.retry_button.clicked.connect(self.retry)
        status_layout.addWidget(self.status_label, 1)
        status_layout.addWidget(self.retry_button)
        self.layout().addWidget(self._status)
        self.stack = QStackedWidget(self)
        self.layout().addWidget(self.stack, 1)
        self.content_widget = content if content is not None else MkQWidget(layout="v", margins=0)
        self.skeleton = skeleton if skeleton is not None else MkSkeleton(source_widget=self.content_widget)
        self._message = QLabel("", self)
        self._message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._message.setWordWrap(True)
        for widget in (self.content_widget, self.skeleton, self._message):
            self.stack.addWidget(widget)
        self.stack.setCurrentWidget(self._message)
        self._status.hide()
        self._delay = QTimer(self)
        self._delay.setSingleShot(True)
        self._delay.timeout.connect(self._show_placeholder)

    @property
    def state(self):
        return self._state

    @property
    def result(self):
        return self._result

    @property
    def task(self):
        return self._task

    def _set_state(self, state):
        if self._state != state:
            self._state = state
            self.stateChanged.emit(state)

    def _show_placeholder(self):
        if self._state == "loading" and not (self._has_content and self._retain_content):
            self.stack.setCurrentWidget(self.skeleton)

    @staticmethod
    def _default_empty(data):
        return data is None or isinstance(data, (list, tuple, dict, set, str, bytes)) and len(data) == 0

    def load(self, worker_fn, *args, on_success=None, on_error=None,
             is_empty=None, pass_cancel_event=False, **kwargs):
        """Return a MkTask. Worker kwargs are forwarded; the newest load wins."""
        self._generation += 1
        generation = self._generation
        self._retry_spec = (worker_fn, args, on_success, on_error, is_empty,
                            pass_cancel_event, dict(kwargs))
        self._delay.stop()
        self.retry_button.hide()
        self.status_label.setToolTip("")
        self.status_label.setText("正在刷新…" if self._has_content else "正在加载…")
        self._status.show()
        if self._has_content and self._retain_content:
            self.stack.setCurrentWidget(self.content_widget)
        else:
            self._message.setText("")
            self.stack.setCurrentWidget(self._message)
        self._set_state("loading")
        if self._loading_delay_ms:
            self._delay.start(self._loading_delay_ms)
        else:
            self._show_placeholder()

        def success(data):
            if generation != self._generation:
                return
            empty = (is_empty or self._default_empty)(data)
            if on_success is not None:
                on_success(data)
            if generation != self._generation:
                return
            self._delay.stop()
            self._result = data
            self._has_content = not empty
            self._settled_state = "empty" if empty else "ready"
            self._status.hide()
            if empty:
                self._message.setText(self._empty_text)
                self.stack.setCurrentWidget(self._message)
            else:
                self.stack.setCurrentWidget(self.content_widget)
            self._set_state(self._settled_state)
            if isValid(self) and generation == self._generation:
                self.loaded.emit(data)

        def failure(error):
            if generation != self._generation:
                return
            self._delay.stop()
            self.status_label.setText(self._error_text)
            self.status_label.setToolTip(str(error))
            self.retry_button.show()
            self._status.show()
            if not (self._has_content and self._retain_content):
                self._message.setText(self._error_text)
                self.stack.setCurrentWidget(self._message)
            self._settled_state = "error"
            self._set_state("error")
            if not isValid(self) or generation != self._generation:
                return
            self.loadFailed.emit(error)
            if on_error is not None and isValid(self) and generation == self._generation:
                on_error(error)

        def cancelled():
            if isValid(self) and generation == self._generation:
                self._delay.stop()
                self._status.hide()
                if self._has_content:
                    self.stack.setCurrentWidget(self.content_widget)
                else:
                    self._message.setText(self._empty_text if self._settled_state == "empty" else "")
                    self.stack.setCurrentWidget(self._message)
                state = "ready" if self._has_content else "empty" if self._settled_state == "empty" else "idle"
                self._set_state(state)

        self._task = self.run_async(worker_fn, *args, on_success=success,
                                    on_error=failure, auto_loading=False,
                                    task_key="page_load", pass_cancel_event=pass_cancel_event,
                                    **kwargs)
        self._task.cancelled.connect(cancelled)
        return self._task

    def cancel(self):
        if self._task is not None:
            self._task.cancel()

    def retry(self):
        if self._retry_spec is None or self._state == "loading":
            return None
        self.retryRequested.emit()
        fn, args, success, error, empty, cooperative, kwargs = self._retry_spec
        return self.load(fn, *args, on_success=success, on_error=error,
                         is_empty=empty, pass_cancel_event=cooperative, **kwargs)
