# -*- coding: utf-8 -*-
"""MkThemeSelector - compact switcher for MonkeyQt default + 67 UI styles."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox

from ..engine import ThemeEngine
from ..names import DEFAULT_THEME_CN_NAME, theme_display_name


class MkThemeSelector(QComboBox):
    """A small combobox that switches between built-in MonkeyQt styling and 67 themes."""

    themeSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mkThemeSelector")
        self.setMinimumHeight(30)
        self.setFixedWidth(245)

        for name in ThemeEngine.list_themes():
            self.addItem(theme_display_name(name), name)
            self.setItemData(self.count() - 1, name, Qt.ItemDataRole.ToolTipRole)

        self.currentIndexChanged.connect(self._on_index_changed)
        ThemeEngine.instance().themeChanged.connect(self._sync_from_engine)
        self._apply_selector_style()

    def _on_index_changed(self, index: int):
        value = self.itemData(index)
        if value:
            ThemeEngine.set_theme(value)
            self.themeSelected.emit(value)
        self._apply_selector_style()

    def _sync_from_engine(self, theme_name: str):
        for i in range(self.count()):
            if self.itemData(i) == theme_name:
                self.blockSignals(True)
                self.setCurrentIndex(i)
                self.blockSignals(False)
                break
        self._apply_selector_style()

    def _apply_selector_style(self):
        t = ThemeEngine
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        border = t.get("--glass-border", t.get("--border", "#CBD5E1")) if t.is_glass() else t.get("--border", "#CBD5E1")
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        muted = t.get("--text-muted", "#64748B")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        family = "Consolas" if t.is_pixel() else '"Segoe UI", "Microsoft YaHei"'
        self.setStyleSheet(f"""
            QComboBox#mkThemeSelector {{
                background: {surface};
                color: {fg};
                border: {border_rule};
                border-radius: {radius};
                padding: 4px 28px 4px 10px;
                font-family: {family};
                font-size: 12px;
                font-weight: 700;
            }}
            QComboBox#mkThemeSelector:hover {{
                border-color: {t.get("--primary", "#409EFF")};
            }}
            QComboBox#mkThemeSelector::drop-down {{
                border: none;
                width: 26px;
            }}
            QComboBox#mkThemeSelector QAbstractItemView {{
                background: {surface};
                color: {fg};
                border: {border_rule};
                border-radius: {radius};
                padding: 4px;
                outline: none;
                selection-background-color: {t.get("--primary", "#409EFF")};
            }}
            QComboBox#mkThemeSelector QAbstractItemView::item {{
                min-height: 26px;
                padding: 4px 8px;
            }}
            QComboBox#mkThemeSelector QAbstractItemView::item:hover {{
                color: {fg};
            }}
            QComboBox#mkThemeSelector:disabled {{
                color: {muted};
            }}
        """)
