# -*- coding: utf-8 -*-
"""Animated stacked pages and reusable back/forward navigation."""

from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QStackedWidget, QWidget

from monkeyqt.core.icons import MkPhosphorIcon


class MkAnimatedStackedWidget(QStackedWidget):
    """QStackedWidget with a compact horizontal slide transition."""

    animationFinished = Signal(int)

    def __init__(self, parent=None, animation_duration: int = 280):
        super().__init__(parent)
        self._animation_duration = max(0, int(animation_duration))
        self._animation_group = None
        self._is_animating = False

    def set_animation_duration(self, duration: int) -> None:
        self._animation_duration = max(0, int(duration))

    def is_animating(self) -> bool:
        return self._is_animating

    def slide_to(self, index: int, direction: str | None = None) -> bool:
        if self._is_animating or index < 0 or index >= self.count():
            return False

        current_index = self.currentIndex()
        if current_index == index:
            return False

        if self._animation_duration <= 0 or self.width() <= 1:
            self.setCurrentIndex(index)
            self.animationFinished.emit(index)
            return True

        forward = direction not in {"back", "backward", "left", "previous"}
        offset = self.width() if forward else -self.width()
        current_widget = self.currentWidget()
        next_widget = self.widget(index)
        if current_widget is None or next_widget is None:
            self.setCurrentIndex(index)
            self.animationFinished.emit(index)
            return True

        self._is_animating = True
        next_widget.setGeometry(self.rect())
        next_widget.move(offset, 0)
        next_widget.show()
        next_widget.raise_()

        current_animation = QPropertyAnimation(current_widget, b"pos", self)
        current_animation.setDuration(self._animation_duration)
        current_animation.setStartValue(QPoint(0, 0))
        current_animation.setEndValue(QPoint(-offset, 0))
        current_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        next_animation = QPropertyAnimation(next_widget, b"pos", self)
        next_animation.setDuration(self._animation_duration)
        next_animation.setStartValue(QPoint(offset, 0))
        next_animation.setEndValue(QPoint(0, 0))
        next_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(current_animation)
        group.addAnimation(next_animation)
        group.finished.connect(
            lambda: self._finish_transition(index, current_widget, next_widget)
        )
        self._animation_group = group
        group.start()
        return True

    def slideInIdx(self, index: int, direction: str | None = None) -> bool:
        """Compatibility alias for older MonkeyQt demos."""
        return self.slide_to(index, direction)

    def _finish_transition(self, index, current_widget, next_widget) -> None:
        self.setCurrentIndex(index)
        current_widget.move(0, 0)
        next_widget.move(0, 0)
        if current_widget is not next_widget:
            current_widget.hide()
        self._is_animating = False
        self._animation_group = None
        self.animationFinished.emit(index)


class MkHistoryNavigation(QWidget):
    """Back/forward buttons with browser-like page history."""

    pageChanged = Signal(str)
    historyChanged = Signal(bool, bool)

    def __init__(
        self,
        stack: QStackedWidget,
        pages: dict[str, int | QWidget],
        initial_page: str | None = None,
        animation_duration: int = 280,
        parent=None,
    ):
        super().__init__(parent)
        self.stack = stack
        self.pages = dict(pages)
        self._history: list[str] = []
        self._history_index = -1

        if isinstance(stack, MkAnimatedStackedWidget):
            stack.set_animation_duration(animation_duration)
            stack.animationFinished.connect(lambda _index: self._update_buttons())

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.back_button = self._make_button("返回")
        self.forward_button = self._make_button("前进")
        layout.addWidget(self.back_button)
        layout.addWidget(self.forward_button)

        self.back_button.clicked.connect(self.back)
        self.forward_button.clicked.connect(self.forward)

        initial = initial_page or self._page_for_index(stack.currentIndex())
        if initial in self.pages:
            self._history = [initial]
            self._history_index = 0
            target = self._resolve_page_index(initial)
            if target >= 0:
                self.stack.setCurrentIndex(target)

        self._update_buttons()

    def _make_button(self, tooltip: str) -> QPushButton:
        button = QPushButton(self)
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedSize(QSize(30, 30))
        button.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover { background: palette(midlight); }
            QPushButton:pressed { background: palette(mid); }
            QPushButton:disabled { background: transparent; }
            """
        )
        return button

    def navigate(
        self,
        page_id: str,
        record_history: bool = True,
        direction: str | None = None,
    ) -> bool:
        if self._is_busy():
            return False

        current_page = self.current_page()
        if current_page == page_id:
            self._update_buttons()
            return False

        moved = self._move_stack(page_id, direction or "forward")
        if moved:
            if record_history:
                self._history = self._history[: self._history_index + 1]
                self._history.append(page_id)
                self._history_index = len(self._history) - 1
            self._update_buttons()
            self.pageChanged.emit(page_id)
        return moved

    def back(self) -> bool:
        if not self.can_go_back() or self._is_busy():
            return False
        target_history_index = self._history_index - 1
        page_id = self._history[target_history_index]
        moved = self._move_stack(page_id, "back")
        if moved:
            self._history_index = target_history_index
            self._update_buttons()
            self.pageChanged.emit(page_id)
        return moved

    def forward(self) -> bool:
        if not self.can_go_forward() or self._is_busy():
            return False
        target_history_index = self._history_index + 1
        page_id = self._history[target_history_index]
        moved = self._move_stack(page_id, "forward")
        if moved:
            self._history_index = target_history_index
            self._update_buttons()
            self.pageChanged.emit(page_id)
        return moved

    def current_page(self) -> str | None:
        return self._page_for_index(self.stack.currentIndex())

    def can_go_back(self) -> bool:
        return self._history_index > 0

    def can_go_forward(self) -> bool:
        return 0 <= self._history_index < len(self._history) - 1

    def _resolve_page_index(self, page_id: str) -> int:
        page = self.pages.get(page_id)
        if isinstance(page, QWidget):
            return self.stack.indexOf(page)
        return int(page) if isinstance(page, int) else -1

    def _page_for_index(self, index: int) -> str | None:
        for page_id, page in self.pages.items():
            page_index = self.stack.indexOf(page) if isinstance(page, QWidget) else page
            if page_index == index:
                return page_id
        return None

    def _move_stack(self, page_id: str, direction: str) -> bool:
        target_index = self._resolve_page_index(page_id)
        if target_index < 0 or self._is_busy():
            return False

        if isinstance(self.stack, MkAnimatedStackedWidget):
            moved = self.stack.slide_to(target_index, direction)
        else:
            self.stack.setCurrentIndex(target_index)
            moved = True

        if moved:
            self._update_buttons()
        return moved

    def _is_busy(self) -> bool:
        return (
            isinstance(self.stack, MkAnimatedStackedWidget)
            and self.stack.is_animating()
        )

    def _update_buttons(self) -> None:
        busy = self._is_busy()
        can_back = self.can_go_back() and not busy
        can_forward = self.can_go_forward() and not busy
        self.back_button.setEnabled(can_back)
        self.forward_button.setEnabled(can_forward)

        palette = self.palette()
        normal = palette.color(QPalette.ColorRole.WindowText).name()
        active = palette.color(QPalette.ColorRole.Highlight).name()
        disabled = palette.color(QPalette.ColorRole.PlaceholderText).name()
        self.back_button.setIcon(
            MkPhosphorIcon.get_icon(
                "caret-left", active if can_back else disabled, normal, 18
            )
        )
        self.forward_button.setIcon(
            MkPhosphorIcon.get_icon(
                "caret-right", active if can_forward else disabled, normal, 18
            )
        )
        self.historyChanged.emit(can_back, can_forward)

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        self._update_buttons()
