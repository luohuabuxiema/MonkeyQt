# -*- coding: utf-8 -*-
"""ThemedMessage — inline/toast-like themed message card."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from ..engine import ThemeEngine


_MESSAGE = {
    "info": ("i", "#3B82F6"),
    "success": ("✓", "#22C55E"),
    "warning": ("!", "#F59E0B"),
    "error": ("×", "#EF4444"),
}


class ThemedMessage(QFrame):
    """A compact message surface useful as toast content or inline status."""

    closed = Signal()

    def __init__(self, text="", msg_type="info", parent=None):
        super().__init__(parent)
        self.setObjectName("themedMessage")
        self._text = text
        self._msg_type = msg_type if msg_type in _MESSAGE else "info"
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(14, 10, 14, 10)
        self.layout.setSpacing(10)
        self.icon_label = QLabel()
        self.icon_label.setFixedWidth(18)
        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label, 1)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        icon, accent = _MESSAGE[self._msg_type]
        self.icon_label.setText(icon)
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        self.setStyleSheet(f"""
            QFrame#themedMessage {{
                background: {surface};
                border: {border_rule};
                border-left: 4px solid {accent};
                border-radius: {radius};
            }}
            QLabel {{
                background: transparent;
                color: {fg};
                font-size: 13px;
                font-weight: 600;
            }}
        """)
        self.icon_label.setStyleSheet(f"background: transparent; color: {accent}; font-weight: 900; font-size: 15px;")
