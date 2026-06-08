# -*- coding: utf-8 -*-
"""ThemedTopbar — horizontal themed navigation."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy

from ..engine import ThemeEngine
from ..style_utils import readable_text


class _TopbarItem(QPushButton):
    def __init__(self, item_id, text, parent=None):
        super().__init__(text, parent)
        self.item_id = item_id
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(76)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        surface_muted = t.get("--surface-muted", "#F1F5F9")
        family = "Consolas" if t.is_pixel() else '"Segoe UI", "Microsoft YaHei"'
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-bottom: 3px solid transparent;
                color: {muted};
                padding: 0 16px;
                font-family: {family};
                font-size: 13px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                color: {fg};
                background: {surface_muted};
            }}
            QPushButton:checked {{
                color: {primary};
                border-bottom-color: {primary};
            }}
        """)


class ThemedTopbar(QFrame):
    """A themed top navigation bar with logo and exclusive items."""

    itemClicked = Signal(str)

    def __init__(self, logo_text="MonkeyQt", parent=None):
        super().__init__(parent)
        self.setObjectName("themedTopbar")
        self.setFixedHeight(58)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(18, 0, 18, 0)
        self.layout.setSpacing(8)

        self.logo_label = QLabel(logo_text)
        self.logo_label.setObjectName("themedTopbarLogo")
        self.layout.addWidget(self.logo_label)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self._on_clicked)
        self.items_layout = QHBoxLayout()
        self.items_layout.setContentsMargins(12, 0, 0, 0)
        self.items_layout.setSpacing(0)
        self.layout.addLayout(self.items_layout)
        self.layout.addStretch()

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def add_item(self, item_id: str, text: str):
        btn = _TopbarItem(item_id, text)
        self.button_group.addButton(btn)
        self.items_layout.addWidget(btn)
        return btn

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
        primary = t.get("--primary", "#409EFF")
        bg = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        if t.is_glow():
            bg = "#10121C"
            fg = "#E5F6FF"
        self.setStyleSheet(f"""
            QFrame#themedTopbar {{
                background: {bg};
                border: {border_rule};
                border-radius: {radius};
            }}
            QLabel#themedTopbarLogo {{
                background: transparent;
                color: {fg};
                font-size: 18px;
                font-weight: 900;
                padding-right: 18px;
            }}
        """)
        for btn in self.button_group.buttons():
            btn.set_theme_style()
