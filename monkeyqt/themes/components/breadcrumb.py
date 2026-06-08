# -*- coding: utf-8 -*-
"""ThemedBreadcrumb — theme-aware breadcrumb navigation."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from ..engine import ThemeEngine


class _BreadcrumbButton(QPushButton):
    def __init__(self, item_id: str, text: str, current=False, parent=None):
        super().__init__(text, parent)
        self.item_id = item_id
        self.current = current
        self.setCursor(Qt.CursorShape.ArrowCursor if current else Qt.CursorShape.PointingHandCursor)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        color = fg if self.current else muted
        hover = fg if self.current else primary
        font_weight = "900" if t.is_brutal() else ("800" if self.current else "700")
        family = "Consolas" if t.is_pixel() else '"Segoe UI", "Microsoft YaHei"'
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {color};
                padding: 0;
                font-family: {family};
                font-size: 13px;
                font-weight: {font_weight};
            }}
            QPushButton:hover {{
                color: {hover};
            }}
        """)


class ThemedBreadcrumb(QWidget):
    """A simple breadcrumb with clickable ancestors and themed separators."""

    itemClicked = Signal(str)

    def __init__(self, separator="/", parent=None):
        super().__init__(parent)
        self.separator_text = separator
        self._items_data = []
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.layout.addStretch()
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def set_items(self, items: list):
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self._items_data = items
        total = len(items)
        for i, data in enumerate(items):
            current = i == total - 1
            btn = _BreadcrumbButton(data.get("id", data.get("text", "")), data.get("text", ""), current)
            if not current:
                btn.clicked.connect(lambda checked=False, item_id=btn.item_id: self.itemClicked.emit(item_id))
            self.layout.insertWidget(self.layout.count() - 1, btn)

            if not current:
                sep = QLabel(self.separator_text)
                sep.setObjectName("breadcrumbSeparator")
                self.layout.insertWidget(self.layout.count() - 1, sep)
        self.set_theme_style()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        muted = t.get("--text-muted", "#94A3B8")
        family = "Consolas" if t.is_pixel() else '"Segoe UI", "Microsoft YaHei"'
        self.setStyleSheet(f"""
            QLabel#breadcrumbSeparator {{
                background: transparent;
                color: {muted};
                font-family: {family};
                font-size: 13px;
                font-weight: 800;
            }}
        """)
        for btn in self.findChildren(_BreadcrumbButton):
            btn.set_theme_style()
