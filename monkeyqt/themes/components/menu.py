# -*- coding: utf-8 -*-
"""ThemedMenu — vertical themed side navigation."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ..engine import ThemeEngine
from ..style_utils import readable_text


class _MenuItem(QPushButton):
    def __init__(self, item_id, text, icon="", parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self._text = text
        self._icon = icon
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(14, 0, 14, 0)
        self.layout.setSpacing(10)
        self.icon_label = QLabel(icon or "•")
        self.icon_label.setFixedWidth(20)
        self.text_label = QLabel(text)
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)
        self.layout.addStretch()
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.toggled.connect(lambda checked: self.set_theme_style())
        self.set_theme_style()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        surface_muted = t.get("--surface-muted", "#F1F5F9")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        active_fg = readable_text(primary)
        item_fg = active_fg if self.isChecked() else fg
        item_bg = primary if self.isChecked() else "transparent"
        family = "Consolas" if t.is_pixel() else '"Segoe UI", "Microsoft YaHei"'
        self.setStyleSheet(f"""
            QPushButton {{
                background: {item_bg};
                border: none;
                border-radius: {radius};
                padding: 0;
            }}
            QPushButton:hover {{
                background: {primary if self.isChecked() else surface_muted};
            }}
            QLabel {{
                background: transparent;
                color: {item_fg if self.isChecked() else muted};
                font-family: {family};
                font-size: 13px;
                font-weight: 800;
            }}
        """)
        self.text_label.setStyleSheet(f"background: transparent; color: {item_fg}; font-family: {family}; font-size: 13px; font-weight: 800;")
        self.icon_label.setStyleSheet(f"background: transparent; color: {item_fg if self.isChecked() else muted}; font-size: 15px; font-weight: 900;")


class ThemedMenu(QFrame):
    """A simple themed sidebar menu."""

    itemClicked = Signal(str)

    def __init__(self, title="Navigation", parent=None):
        super().__init__(parent)
        self.setObjectName("themedMenu")
        self.setFixedWidth(220)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 12, 10, 12)
        self.layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("themedMenuTitle")
        self.layout.addWidget(self.title_label)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self._on_clicked)
        self.items_layout = QVBoxLayout()
        self.items_layout.setContentsMargins(0, 4, 0, 0)
        self.items_layout.setSpacing(5)
        self.layout.addLayout(self.items_layout)
        self.layout.addStretch()

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def add_item(self, item_id: str, text: str, icon: str = ""):
        item = _MenuItem(item_id, text, icon)
        self.button_group.addButton(item)
        self.items_layout.addWidget(item)
        return item

    def set_active(self, item_id: str):
        for btn in self.button_group.buttons():
            if btn.item_id == item_id:
                btn.setChecked(True)
                btn.set_theme_style()
                break

    def _on_clicked(self, btn):
        self.itemClicked.emit(btn.item_id)

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        if t.is_glow():
            surface = "#10121C"
            fg = "#E5F6FF"
        self.setStyleSheet(f"""
            QFrame#themedMenu {{
                background: {surface};
                border: {border_rule};
                border-radius: {radius};
            }}
            QLabel#themedMenuTitle {{
                background: transparent;
                color: {fg};
                font-size: 14px;
                font-weight: 900;
                padding: 4px 4px 8px 4px;
            }}
        """)
        self.title_label.setToolTip(muted)
        for item in self.button_group.buttons():
            item.set_theme_style()
