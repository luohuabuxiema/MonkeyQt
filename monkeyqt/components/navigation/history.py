# -*- coding: utf-8 -*-
"""Animated stacked pages and reusable back/forward navigation."""

from __future__ import annotations

from monkeyqt.themes.engine import ThemeEngine as _MkThemeEngine
from PySide6.QtCore import (
    QEvent,
    QTimer,
    QEasingCurve,
    QPoint,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QPalette, QPainter, QColor
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QStackedWidget, QWidget, QSizePolicy

from monkeyqt.core.icons import MkPhosphorIcon


class MkAnimatedStackedWidget(QStackedWidget):
    """QStackedWidget with a compact horizontal slide transition."""

    animationFinished = Signal(int)

    def __init__(self, parent=None, animation_duration: int = 200):
        super().__init__(parent)
        self._animation_duration = max(0, int(animation_duration))
        self._animation_group = None
        self._is_animating = False
        self._anim_target_index = None
        self._anim_current_widget = None
        self._anim_next_widget = None

    def set_animation_duration(self, duration: int) -> None:
        self._animation_duration = max(0, int(duration))

    def set_transition_enabled(self, enabled: bool) -> None:
        """Allow heavy pages/reduced-motion preferences to use immediate switching."""
        self._transition_enabled = bool(enabled)
        if not enabled and self._is_animating:
            self._interrupt_and_finish_animation()

    def is_animating(self) -> bool:
        return self._is_animating

    def _interrupt_and_finish_animation(self) -> None:
        """立即快速终结正在运行的旧动画，复位控件并直接就位，绝不吞掉用户的任何一次新点击。"""
        if self._animation_group is not None:
            group = self._animation_group
            self._animation_group = None
            try:
                group.stop()
            except Exception:
                pass

        if self._anim_target_index is not None and 0 <= self._anim_target_index < self.count():
            target_idx = self._anim_target_index
            self._anim_target_index = None
            self.setCurrentIndex(target_idx)

        if self._anim_next_widget is not None:
            self._anim_next_widget.move(0, 0)
            self._anim_next_widget = None

        if self._anim_current_widget is not None:
            self._anim_current_widget.move(0, 0)
            if self._anim_current_widget is not self.currentWidget():
                self._anim_current_widget.hide()
            self._anim_current_widget = None

        self._is_animating = False

    def slide_to(self, index: int, direction: str | None = None) -> bool:
        if index < 0 or index >= self.count():
            return False

        # 如果当前正在播放动画，立即快速收尾旧动画，复位旧视图，绝不吞掉新点击
        if self._is_animating:
            self._interrupt_and_finish_animation()

        current_index = self.currentIndex()
        if current_index == index:
            return False

        if not getattr(self, "_transition_enabled", True) or self._animation_duration <= 0 or self.width() <= 1:
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
        self._anim_target_index = index
        self._anim_current_widget = current_widget
        self._anim_next_widget = next_widget

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
        if self._animation_group is not None:
            self.setCurrentIndex(index)
            current_widget.move(0, 0)
            next_widget.move(0, 0)
            if current_widget is not next_widget:
                current_widget.hide()
        self._is_animating = False
        self._animation_group = None
        self._anim_target_index = None
        self._anim_current_widget = None
        self._anim_next_widget = None
        self.animationFinished.emit(index)


from ..layout.widget import MkQWidget


class MkHistoryNavButton(QPushButton):
    """Clean, high-performance navigation button for back/forward page history.

    Prevents Qt's built-in disabled icon double-bleaching and eliminates
    unwanted hover backgrounds on disabled states.
    """

    def __init__(self, icon_name: str, tooltip: str = "", parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        if tooltip:
            self.setToolTip(tooltip)
        self.setFixedSize(QSize(28, 28))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._update_cursor()

    def set_icon_name(self, icon_name: str):
        self._icon_name = icon_name
        self.update()

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self._update_cursor()
        self.update()

    def _update_cursor(self):
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if self.isEnabled() else Qt.CursorShape.ArrowCursor
        )

    def enterEvent(self, event):
        super().enterEvent(event)
        if self.isEnabled():
            self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self.isEnabled():
            self.update()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.isEnabled():
            self.update()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.isEnabled():
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        is_dark = _MkThemeEngine.is_dark() if hasattr(_MkThemeEngine, "is_dark") else False

        # 1. Subtle rounded hover/pressed background (ONLY when enabled)
        if self.isEnabled():
            if self.isDown():
                bg = QColor(255, 255, 255, 45) if is_dark else QColor(0, 0, 0, 26)
                painter.setBrush(bg)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 5, 5)
            elif self.underMouse():
                bg = QColor(255, 255, 255, 22) if is_dark else QColor(0, 0, 0, 15)
                painter.setBrush(bg)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 5, 5)

        # 2. Phosphor Icon with distinct active vs disabled contrast
        if self.isEnabled():
            fg_color = _MkThemeEngine.get("--fg", "#F8FAFC" if is_dark else "#0F172A")
        else:
            fg_color = "#52525B" if is_dark else "#94A3B8"

        pm = MkPhosphorIcon.get_pixmap(self._icon_name, fg_color, 16)
        x = (self.width() - 16) // 2
        y = (self.height() - 16) // 2
        painter.drawPixmap(x, y, pm)


class MkHistoryNavigation(MkQWidget):
    """Back/forward buttons with browser-like page history."""

    pageChanged = Signal(str)
    historyChanged = Signal(bool, bool)

    def __init__(
        self,
        stack: QStackedWidget,
        pages: dict[str, int | QWidget],
        initial_page: str | None = None,
        animation_duration: int = 280,
        icon_only: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
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

        self.back_button = self._make_button("返回", "caret-left")
        self.forward_button = self._make_button("前进", "caret-right")
        layout.addWidget(self.back_button)
        layout.addWidget(self.forward_button)

        self.back_button.clicked.connect(self.back)
        self.forward_button.clicked.connect(self.forward)

        try:
            _MkThemeEngine.instance().themeChanged.connect(self._on_theme_changed)
        except Exception:
            pass

        initial = initial_page or self._page_for_index(stack.currentIndex())
        if initial in self.pages:
            self._history = [initial]
            self._history_index = 0
            target = self._resolve_page_index(initial)
            if target >= 0:
                self.stack.setCurrentIndex(target)

        self._update_buttons()

    def _make_button(self, tooltip: str, icon_name: str = "caret-left") -> MkHistoryNavButton:
        return MkHistoryNavButton(icon_name, tooltip, self)

    def navigate(
        self,
        page_id: str,
        record_history: bool = True,
        direction: str | None = None,
    ) -> bool:
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
        if not self.can_go_back():
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
        if not self.can_go_forward():
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
        # Logical navigation changes when requested, not at animation completion.
        target = getattr(self.stack, "_anim_target_index", None)
        return self._page_for_index(target if target is not None else self.stack.currentIndex())

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
        if target_index < 0:
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
        return False

    def _update_buttons(self) -> None:
        can_back = self.can_go_back()
        can_forward = self.can_go_forward()
        self.back_button.setEnabled(can_back)
        self.forward_button.setEnabled(can_forward)
        self.historyChanged.emit(can_back, can_forward)

    def _on_theme_changed(self, theme_name: str = "") -> None:
        self.back_button.update()
        self.forward_button.update()

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() in (QEvent.Type.PaletteChange, QEvent.Type.ApplicationPaletteChange):
            if not getattr(self, "_palette_refresh_pending", False):
                self._palette_refresh_pending = True
                QTimer.singleShot(0, self._refresh_palette_buttons)

    def _refresh_palette_buttons(self):
        self._palette_refresh_pending = False
        self._on_theme_changed()
