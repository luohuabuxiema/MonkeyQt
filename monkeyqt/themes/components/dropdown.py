# -*- coding: utf-8 -*-
"""ThemedDropdown — theme-aware dropdown menu button."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QMenu, QPushButton

from ..engine import ThemeEngine
from ..style_utils import qcolor, readable_text


class ThemedDropdown(QPushButton):
    """A themed menu button with itemClicked ids."""

    itemClicked = Signal(str)

    def __init__(self, text="Dropdown", parent=None):
        super().__init__(text, parent)
        self.menu = QMenu(self)
        self.setMenu(self.menu)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def add_item(self, text, item_id=""):
        item_id = item_id or text
        action = self.menu.addAction(text)
        action.setData(item_id)
        action.triggered.connect(lambda checked=False, value=item_id: self.itemClicked.emit(value))
        return action

    def add_separator(self):
        self.menu.addSeparator()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        surface_muted = t.get("--surface-muted", "#F1F5F9")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        active_fg = readable_text(primary)
        family = "Consolas" if t.is_pixel() else '"Segoe UI", "Microsoft YaHei"'
        weight = "900" if t.is_brutal() else "700"

        self.setStyleSheet(f"""
            QPushButton {{
                background: {surface};
                border: {border_rule};
                border-radius: {radius};
                color: {fg};
                padding: 7px 30px 7px 14px;
                font-family: {family};
                font-size: 13px;
                font-weight: {weight};
            }}
            QPushButton:hover {{
                color: {primary};
                border-color: {primary};
                background: {surface_muted};
            }}
            QPushButton::menu-indicator {{
                image: none;
                width: 0;
            }}
        """)
        self.menu.setStyleSheet(f"""
            QMenu {{
                background: {surface};
                color: {fg};
                border: {border_rule};
                border-radius: {radius};
                padding: 5px;
                font-family: {family};
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 8px 24px 8px 12px;
                border-radius: {radius};
            }}
            QMenu::item:selected {{
                background: {primary};
                color: {active_fg};
            }}
            QMenu::separator {{
                height: 1px;
                background: {border};
                margin: 5px 7px;
            }}
        """)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        t = ThemeEngine
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = qcolor(t.get("--primary", "#409EFF"))
        painter.setPen(QPen(color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        cx = self.width() - 17
        cy = self.height() // 2 + 1
        painter.drawLine(cx - 4, cy - 3, cx, cy + 2)
        painter.drawLine(cx, cy + 2, cx + 4, cy - 3)
        painter.end()
