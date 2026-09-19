# -*- coding: utf-8 -*-
"""MkThemeSelector - compact switcher for MonkeyQt's 68 UI themes."""

import time
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox

from ..engine import ThemeEngine
from ..manager import use_theme
from ..names import DEFAULT_THEME_CN_NAME, theme_display_name
from monkeyqt.components.form.combobox import MkDropdownPopup


class MkThemeSelector(QComboBox):
    """A compact combobox that switches between the 68 MonkeyQt themes."""

    themeSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mkThemeSelector")
        self.setFixedHeight(30)
        self.setFixedWidth(245)
        self.setMaxVisibleItems(12)
        self._last_close_time = 0.0

        for name in ThemeEngine.list_themes():
            self.addItem(theme_display_name(name), name)

        self._popup_widget = MkDropdownPopup(self)

        self.currentIndexChanged.connect(self._on_index_changed)
        ThemeEngine.instance().themeChanged.connect(self._sync_from_engine)
        self._apply_selector_style()

    def showPopup(self):
        if time.time() - getattr(self, "_last_close_time", 0) < 0.25:
            return
        if self.count() == 0:
            return
        if not hasattr(self, "_popup_widget") or self._popup_widget is None:
            self._popup_widget = MkDropdownPopup(self)
        if self._popup_widget.view is not None:
            self._popup_widget.view.doItemsLayout()
        self._popup_widget.show_at_combo()

    def hidePopup(self):
        if hasattr(self, "_popup_widget") and self._popup_widget is not None:
            self._popup_widget.hide()
        super().hidePopup()

    def hideEvent(self, event):
        if hasattr(self, "_popup_widget") and self._popup_widget is not None:
            self._popup_widget.hide()
        super().hideEvent(event)

    def _on_index_changed(self, index: int):
        value = self.itemData(index)
        if value:
            use_theme(value)
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
        hover_border = t.get("--input-hover-border", "rgba(255, 255, 255, 0.40)" if t.is_dark() else "#94A3B8")
        focus_border = t.get("--input-focus-border", "#FFFFFF" if t.is_dark() else "#0F172A")
        self.setStyleSheet(f"""
            QComboBox#mkThemeSelector {{
                background: {surface};
                color: {fg};
                border: {border_rule};
                border-radius: {radius};
                padding: 0px 28px 0px 10px;
                font-family: {family};
                font-size: 12px;
                font-weight: 700;
                min-height: 28px;
                max-height: 30px;
            }}
            QComboBox#mkThemeSelector:hover {{
                border-color: {hover_border};
            }}
            QComboBox#mkThemeSelector:focus,
            QComboBox#mkThemeSelector:on {{
                border-color: {focus_border};
            }}
            QComboBox#mkThemeSelector::drop-down {{
                border: none;
                width: 26px;
            }}
            QComboBox#mkThemeSelector:disabled {{
                color: {muted};
            }}
        """)
        if hasattr(self, "_popup_widget") and self._popup_widget is not None:
            self._popup_widget.update_theme_style()

