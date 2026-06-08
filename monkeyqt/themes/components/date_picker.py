# -*- coding: utf-8 -*-
"""ThemedDatePicker — theme-aware date edit."""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit

from ..engine import ThemeEngine
from ..style_utils import readable_text


class ThemedDatePicker(QDateEdit):
    """A themed QDateEdit using Qt's built-in popup calendar."""

    def __init__(self, date: QDate | None = None, parent=None):
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setDisplayFormat("yyyy-MM-dd")
        self.setDate(date or QDate.currentDate())
        self.setMinimumHeight(38)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        surface_muted = t.get("--surface-muted", "#F1F5F9")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        active_fg = readable_text(primary)
        family = "Consolas" if t.is_pixel() else '"Segoe UI", "Microsoft YaHei"'

        self.setStyleSheet(f"""
            QDateEdit {{
                background: {surface};
                color: {fg};
                border: {border_rule};
                border-radius: {radius};
                padding: 7px 10px;
                font-family: {family};
                font-size: 13px;
                selection-background-color: {primary};
                selection-color: {active_fg};
            }}
            QDateEdit:hover, QDateEdit:focus {{
                border-color: {primary};
            }}
            QDateEdit::drop-down {{
                width: 28px;
                border: none;
            }}
            QDateEdit::down-arrow {{
                image: none;
                width: 0;
                height: 0;
            }}
            QCalendarWidget QWidget {{
                background: {surface};
                color: {fg};
                alternate-background-color: {surface};
                font-family: {family};
            }}
            QCalendarWidget QToolButton {{
                background: transparent;
                color: {fg};
                border: none;
                border-radius: {radius};
                padding: 5px;
                font-weight: 700;
            }}
            QCalendarWidget QToolButton:hover {{
                background: {surface_muted};
                color: {primary};
            }}
            QCalendarWidget QMenu {{
                background: {surface};
                color: {fg};
                border: {border_rule};
            }}
            QCalendarWidget QSpinBox {{
                background: {surface};
                color: {fg};
                border: 1px solid {border};
                border-radius: {radius};
                padding: 2px 4px;
            }}
            QCalendarWidget QAbstractItemView {{
                background: {surface};
                color: {fg};
                selection-background-color: {primary};
                selection-color: {active_fg};
                outline: none;
            }}
            QCalendarWidget QHeaderView::section {{
                background: {surface_muted};
                color: {muted};
                border: none;
                padding: 4px;
                font-weight: 700;
            }}
        """)
