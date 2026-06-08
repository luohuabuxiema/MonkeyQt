# -*- coding: utf-8 -*-
"""ThemedForm — small themed form layout helpers."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFormLayout, QLabel, QVBoxLayout, QWidget

from ..engine import ThemeEngine


class ThemedForm(QWidget):
    """A compact form container with themed labels and helper text."""

    def __init__(self, title="", description="", parent=None):
        super().__init__(parent)
        self._title = title
        self._description = description

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setVisible(bool(title))
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.layout.addWidget(self.title_label)

        self.description_label = QLabel(description)
        self.description_label.setWordWrap(True)
        self.description_label.setVisible(bool(description))
        self.layout.addWidget(self.description_label)

        self.form_layout = QFormLayout()
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(10)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.layout.addLayout(self.form_layout)

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def add_row(self, label: str, field: QWidget):
        self.form_layout.addRow(label, field)
        self.set_theme_style()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        family = "Consolas" if t.is_pixel() else '"Segoe UI", "Microsoft YaHei"'
        self.setStyleSheet(f"""
            ThemedForm, QLabel {{
                background: transparent;
                color: {fg};
                font-family: {family};
            }}
            QLabel {{
                font-size: 13px;
            }}
        """)
        self.title_label.setStyleSheet(f"background: transparent; color: {fg}; font-weight: 800; font-size: 15px;")
        self.description_label.setStyleSheet(f"background: transparent; color: {muted}; font-size: 12px;")
