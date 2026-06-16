# -*- coding: utf-8 -*-
"""ThemedHistoryNavigation — back/forward buttons with 68-theme support."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QStackedWidget

from monkeyqt.components.navigation.history import MkAnimatedStackedWidget, MkHistoryNavigation
from monkeyqt.core.icons import MkPhosphorIcon
from ..engine import ThemeEngine
from ..style_utils import qcolor, readable_text


class ThemedHistoryNavigation(MkHistoryNavigation):
    """MkHistoryNavigation with automatic 68-theme adaptation.

    Usage::

        nav = ThemedHistoryNavigation(stack, pages, initial_page="home")
        # That's it — styles update automatically when the theme changes.
    """

    def __init__(
        self,
        stack: QStackedWidget,
        pages: dict[str, int | object],
        initial_page: str | None = None,
        animation_duration: int = 280,
        icon_only: bool = False,
        parent=None,
    ):
        self._icon_only = icon_only
        super().__init__(stack, pages, initial_page, animation_duration, parent)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    @property
    def icon_only(self) -> bool:
        """Whether the buttons are rendered as icon-only (transparent backgrounds)."""
        return self._icon_only

    @icon_only.setter
    def icon_only(self, val: bool) -> None:
        if self._icon_only != val:
            self._icon_only = val
            self.set_theme_style()


    def _make_button(self, tooltip: str) -> QPushButton:
        """Override to create theme-aware buttons."""
        button = QPushButton(self)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedSize(QSize(30, 30))
        # Styling is applied via set_theme_style, not inline QSS
        return button

    def set_theme_style(self, style_name: str = None) -> None:
        """Refresh button styles from current ThemeEngine tokens."""
        t = ThemeEngine

        surface = t.get("--surface", "#FFFFFF")
        surface_muted = t.get("--surface-muted", "#F1F5F9")
        border = t.get("--border", "#E2E8F0")
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--fg", "#1E293B")

        # Detect the chrome/titlebar surface for correct contrast
        chrome_surface = t.get("--titlebar-bg", t.get("--sidebar-bg", surface))

        if self._icon_only:
            hover_bg = "transparent"
            pressed_bg = "transparent"
            radius = "0px"
        elif t.is_glass():
            hover_bg = "rgba(255, 255, 255, 0.12)" if t.is_dark() else "rgba(0, 0, 0, 0.06)"
            pressed_bg = "rgba(255, 255, 255, 0.18)" if t.is_dark() else "rgba(0, 0, 0, 0.10)"
            radius = "6px"
        elif t.is_brutal() or t.is_pixel():
            hover_bg = surface_muted
            pressed_bg = border
            radius = "0px"
        elif t.is_glow():
            glow_muted = f"rgba({qcolor(primary).red()}, {qcolor(primary).green()}, {qcolor(primary).blue()}, 0.15)"
            hover_bg = glow_muted
            pressed_bg = f"rgba({qcolor(primary).red()}, {qcolor(primary).green()}, {qcolor(primary).blue()}, 0.25)"
            radius = "6px"
        elif t.is_neumorphic():
            hover_bg = surface_muted
            pressed_bg = border
            radius = "8px"
        else:
            hover_bg = surface_muted
            pressed_bg = border
            radius = "6px"

        btn_qss = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: {radius};
                padding: 5px;
            }}
            QPushButton:hover {{
                background: {hover_bg};
            }}
            QPushButton:pressed {{
                background: {pressed_bg};
            }}
            QPushButton:disabled {{
                background: transparent;
            }}
        """

        self.back_button.setStyleSheet(btn_qss)
        self.forward_button.setStyleSheet(btn_qss)

        self._update_buttons()

    def _update_buttons(self) -> None:
        """Override to use ThemeEngine tokens for icon colors."""
        busy = self._is_busy()
        can_back = self.can_go_back() and not busy
        can_forward = self.can_go_forward() and not busy
        self.back_button.setEnabled(can_back)
        self.forward_button.setEnabled(can_forward)

        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")

        # Use theme-aware text color for the chrome area
        if t.is_glass():
            text_color = t.get("--glass-text", fg)
        else:
            text_color = fg

        active_color = primary
        disabled_color = muted

        self.back_button.setIcon(
            MkPhosphorIcon.get_icon(
                "caret-left",
                active_color if can_back else disabled_color,
                text_color,
                18,
            )
        )
        self.forward_button.setIcon(
            MkPhosphorIcon.get_icon(
                "caret-right",
                active_color if can_forward else disabled_color,
                text_color,
                18,
            )
        )
        self.historyChanged.emit(can_back, can_forward)

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        self._update_buttons()
