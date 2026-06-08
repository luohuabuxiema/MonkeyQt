# -*- coding: utf-8 -*-
"""ThemedMultiComboBox — checklist popup multi-select."""

import time

from PySide6.QtCore import QEvent, QPoint, Qt, Signal
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from .checkbox import ThemedCheckBox
from ..engine import ThemeEngine
from ..style_utils import qcolor, readable_text


class _MultiComboPopup(QFrame):
    def __init__(self, parent_combo):
        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.parent_combo = parent_combo
        self.setObjectName("themedMultiComboPopup")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(2, 2, 2, 2)
        self.content_layout.setSpacing(2)
        self.content_layout.addStretch()
        self.scroll.setWidget(self.content)
        self.layout.addWidget(self.scroll)
        self.items = []
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def add_item(self, text, data):
        checkbox = ThemedCheckBox(text, self.content)
        checkbox.stateChanged.connect(self.parent_combo._on_item_state_changed)
        row = QWidget(self.content)
        row.setObjectName("themedMultiComboRow")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(8, 4, 8, 4)
        row_layout.addWidget(checkbox)
        self.content_layout.insertWidget(self.content_layout.count() - 1, row)
        row.installEventFilter(self)
        self.items.append((data, text, checkbox, row))
        self.set_theme_style()

    def clear(self):
        for _, _, _, row in self.items:
            row.deleteLater()
        self.items.clear()

    def show_popup(self):
        if not self.items:
            return
        height = min(230, len(self.items) * 34 + 14)
        pos = self.parent_combo.mapToGlobal(QPoint(0, self.parent_combo.height()))
        self.setGeometry(pos.x(), pos.y() + 4, self.parent_combo.width(), height)
        self.show()
        self.raise_()

    def hideEvent(self, event):
        self.parent_combo._last_close_time = time.time()
        self.parent_combo.setProperty("focused", "false")
        self.parent_combo.set_theme_style()
        super().hideEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            for _, _, checkbox, row in self.items:
                if obj == row:
                    checkbox.toggle()
                    return True
        return super().eventFilter(obj, event)

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        surface_muted = t.get("--surface-muted", "#F1F5F9")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        self.setStyleSheet(f"""
            QFrame#themedMultiComboPopup {{
                background: {surface};
                color: {fg};
                border: {border_rule};
                border-radius: {radius};
            }}
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QWidget#themedMultiComboRow {{
                background: transparent;
                border-radius: {radius};
            }}
            QWidget#themedMultiComboRow:hover {{
                background: {surface_muted};
            }}
        """)


class ThemedMultiComboBox(QFrame):
    """A themed multi-select dropdown with checkbox rows."""

    selectionChanged = Signal(list)

    def __init__(self, placeholder="选择多个选项", parent=None):
        super().__init__(parent)
        self.setObjectName("themedMultiCombo")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self._placeholder = placeholder
        self._last_close_time = 0
        self.setProperty("focused", "false")

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(11, 2, 30, 2)
        self.layout.setSpacing(0)
        self.text_label = QLabel(placeholder)
        self.text_label.setObjectName("themedMultiComboText")
        self.text_label.setWordWrap(False)
        self.layout.addWidget(self.text_label)

        self.popup = _MultiComboPopup(self)
        self.text_label.installEventFilter(self)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def addItem(self, text, data=None):
        self.popup.add_item(text, text if data is None else data)
        self._update_text()

    def addItems(self, items):
        for item in items:
            if isinstance(item, tuple) and len(item) == 2:
                self.addItem(item[0], item[1])
            else:
                self.addItem(str(item), item)

    def clear(self):
        self.popup.clear()
        self._update_text()

    def get_checked_data(self):
        return [data for data, _, checkbox, _ in self.popup.items if checkbox.isChecked()]

    def get_checked_texts(self):
        return [text for _, text, checkbox, _ in self.popup.items if checkbox.isChecked()]

    def setCheckedData(self, values):
        values = set(values)
        for data, _, checkbox, _ in self.popup.items:
            checkbox.blockSignals(True)
            checkbox.setChecked(data in values)
            checkbox.blockSignals(False)
        self._update_text()
        self.selectionChanged.emit(self.get_checked_data())

    def _on_item_state_changed(self):
        self._update_text()
        self.selectionChanged.emit(self.get_checked_data())

    def _update_text(self):
        texts = self.get_checked_texts()
        self.text_label.setText(", ".join(texts) if texts else self._placeholder)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self._handle_click()
            return True
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_click()
        else:
            super().mousePressEvent(event)

    def _handle_click(self):
        if time.time() - self._last_close_time < 0.15:
            return
        self.setProperty("focused", "true")
        self.set_theme_style()
        self.popup.show_popup()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        active_border = primary if self.property("focused") == "true" else border
        self.setStyleSheet(f"""
            QFrame#themedMultiCombo {{
                background: {surface};
                color: {fg};
                border: {border_rule};
                border-color: {active_border};
                border-radius: {radius};
                min-height: 34px;
            }}
            QLabel#themedMultiComboText {{
                background: transparent;
                color: {fg if self.get_checked_texts() else muted};
                font-size: 13px;
                font-weight: 600;
            }}
        """)
        self.popup.set_theme_style()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(qcolor(ThemeEngine.get("--primary", "#409EFF")), 1.7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        cx = self.width() - 17
        cy = self.height() // 2 + 1
        painter.drawLine(cx - 4, cy - 3, cx, cy + 2)
        painter.drawLine(cx, cy + 2, cx + 4, cy - 3)
        painter.end()
