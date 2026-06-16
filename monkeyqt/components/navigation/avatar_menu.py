# -*- coding: utf-8 -*-
"""Clickable avatar with a configurable account menu."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QMenu

from monkeyqt.components.data.avatar import MkAvatar
from monkeyqt.core.icons import MkPhosphorIcon


class MkAvatarMenu(MkAvatar):
    """MkAvatar that opens a palette-aware action menu."""

    clicked = Signal()
    actionTriggered = Signal(str)

    def __init__(
        self,
        text: str = "",
        image_path: str = "",
        shape: str = "circle",
        size: int = 32,
        user_name: str = "",
        subtitle: str = "",
        actions: Iterable[dict] | None = None,
        parent=None,
    ):
        super().__init__(text, image_path, shape, size, parent)
        self.user_name = user_name
        self.subtitle = subtitle
        self._actions: list[dict] = list(actions or [])
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_actions(self, actions: Iterable[dict]) -> None:
        self._actions = list(actions)

    def add_action(
        self,
        action_id: str,
        text: str,
        callback: Callable | None = None,
        icon: str = "",
        separator_before: bool = False,
        enabled: bool = True,
    ) -> None:
        self._actions.append(
            {
                "id": action_id,
                "text": text,
                "callback": callback,
                "icon": icon,
                "separator_before": separator_before,
                "enabled": enabled,
            }
        )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            self.show_menu()
            event.accept()
            return
        super().mousePressEvent(event)

    def show_menu(self) -> None:
        menu = QMenu(self)
        palette = self.palette()
        base = palette.color(QPalette.ColorRole.Base).name()
        text = palette.color(QPalette.ColorRole.Text).name()
        border = palette.color(QPalette.ColorRole.Mid).name()
        hover = palette.color(QPalette.ColorRole.Highlight).name()
        hover_text = palette.color(QPalette.ColorRole.HighlightedText).name()
        muted = palette.color(QPalette.ColorRole.PlaceholderText).name()
        menu.setStyleSheet(
            f"""
            QMenu {{
                background-color: {base};
                color: {text};
                border: 1px solid {border};
                border-radius: 7px;
                padding: 6px;
            }}
            QMenu::item {{
                min-width: 150px;
                padding: 7px 24px 7px 10px;
                border-radius: 5px;
            }}
            QMenu::item:selected {{
                background-color: {hover};
                color: {hover_text};
            }}
            QMenu::item:disabled {{ color: {muted}; }}
            QMenu::separator {{
                height: 1px;
                background: {border};
                margin: 5px 7px;
            }}
            """
        )

        if self.user_name:
            header = menu.addAction(self.user_name)
            header.setEnabled(False)
        if self.subtitle:
            subtitle = menu.addAction(self.subtitle)
            subtitle.setEnabled(False)
        if self.user_name or self.subtitle:
            menu.addSeparator()

        icon_color = palette.color(QPalette.ColorRole.Text).name()
        for config in self._actions:
            if config.get("separator_before"):
                menu.addSeparator()
            action = menu.addAction(str(config.get("text", "")))
            action.setEnabled(bool(config.get("enabled", True)))
            icon_name = str(config.get("icon", ""))
            if icon_name:
                action.setIcon(MkPhosphorIcon.get_icon(icon_name, icon_color, size=16))

            action_id = str(config.get("id", ""))
            callback = config.get("callback")
            action.triggered.connect(
                lambda _checked=False, aid=action_id, cb=callback: self._trigger_action(
                    aid, cb
                )
            )

        position = self.mapToGlobal(self.rect().bottomRight())
        menu.popup(position)

    def _trigger_action(self, action_id: str, callback) -> None:
        self.actionTriggered.emit(action_id)
        if callable(callback):
            callback()
