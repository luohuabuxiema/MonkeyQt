# -*- coding: utf-8 -*-
"""ThemedTable — theme-aware QTableWidget."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

from ..engine import ThemeEngine
from ..style_utils import readable_text


class ThemedTable(QTableWidget):
    """A styled table widget with convenience header/data setters."""

    def __init__(self, rows=0, columns=0, parent=None):
        super().__init__(rows, columns, parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setShowGrid(False)
        self.setAlternatingRowColors(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setMinimumHeight(180)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def set_headers(self, headers):
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def set_data(self, data):
        self.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.setItem(row_idx, col_idx, item)

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        surface_muted = t.get("--surface-muted", "#F1F5F9")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        active_fg = readable_text(primary)
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        grid_rule = "#000000" if t.is_brutal() or t.is_pixel() else border
        family = "Consolas" if t.is_pixel() else '"Segoe UI", "Microsoft YaHei"'
        weight = "900" if t.is_brutal() else "700"

        if t.is_glow():
            surface = "#10121C"
            surface_muted = "#182033"
            fg = "#E5F6FF"

        self.setStyleSheet(f"""
            QTableWidget {{
                background: {surface};
                color: {fg};
                border: {border_rule};
                border-radius: {radius};
                gridline-color: transparent;
                font-family: {family};
                font-size: 13px;
                outline: none;
                selection-background-color: {primary};
                selection-color: {active_fg};
            }}
            QHeaderView::section {{
                background: {surface_muted};
                color: {muted if not t.is_brutal() else '#000000'};
                border: none;
                border-bottom: 1px solid {grid_rule};
                padding: 10px 9px;
                font-weight: {weight};
            }}
            QTableWidget::item {{
                border-bottom: 1px solid {grid_rule};
                padding: 8px 9px;
            }}
            QTableWidget::item:hover {{
                background: {surface_muted};
            }}
            QTableWidget::item:selected {{
                background: {primary};
                color: {active_fg};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 9px;
                margin: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {muted};
                border-radius: 4px;
                min-height: 26px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
                border: none;
            }}
        """)
        self.viewport().update()
