# -*- coding: utf-8 -*-
"""ThemedDataTable — table plus footer pagination wrapper."""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .pagination import ThemedPagination
from .table import ThemedTable
from ..engine import ThemeEngine


class ThemedDataTable(QWidget):
    """A lightweight themed data table composition."""

    def __init__(self, columns=None, data=None, page_size=10, parent=None):
        super().__init__(parent)
        self._columns = columns or []
        self._data = data or []
        self._page_size = max(1, int(page_size))
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.table = ThemedTable(0, len(self._columns))
        self.layout.addWidget(self.table)
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        self.summary_label = QLabel()
        footer.addWidget(self.summary_label)
        footer.addStretch()
        self.pagination = ThemedPagination(total=len(self._data), page_size=self._page_size, current=1)
        self.pagination.pageChanged.connect(lambda page: self.refresh_table())
        footer.addWidget(self.pagination)
        self.layout.addLayout(footer)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.refresh_table()
        self.set_theme_style()

    def set_data(self, data):
        self._data = data or []
        self.pagination.set_total(len(self._data))
        self.refresh_table()

    def set_columns(self, columns):
        self._columns = columns or []
        self.refresh_table()

    def refresh_table(self):
        page = self.pagination.current_page
        start = (page - 1) * self._page_size
        chunk = self._data[start:start + self._page_size]
        self.table.set_headers(self._columns)
        self.table.set_data(chunk)
        self.summary_label.setText(f"显示 {len(chunk)} / {len(self._data)} 条")

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        muted = t.get("--text-muted", "#64748B")
        self.summary_label.setStyleSheet(f"background: transparent; color: {muted}; font-size: 12px;")
        self.table.set_theme_style()
        self.pagination.set_theme_style()
