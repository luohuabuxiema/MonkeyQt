# -*- coding: utf-8 -*-
"""ThemedPagination — theme-aware pagination controls."""

from PySide6.QtCore import Property, Qt, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

from ..engine import ThemeEngine
from ..style_utils import readable_text


class ThemedPagination(QWidget):
    """Element-style pagination with dynamic theme QSS."""

    pageChanged = Signal(int)

    def __init__(self, total=0, page_size=10, current=1, parent=None):
        super().__init__(parent)
        self._total = max(0, int(total))
        self._page_size = max(1, int(page_size))
        self._current_page = max(1, int(current))
        self._total_pages = 1

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.total_label = QLabel()
        self.total_label.setObjectName("paginationTotal")
        self.layout.addWidget(self.total_label)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(4)
        self.layout.addLayout(self.buttons_layout)

        self.layout.addWidget(QLabel("页"))
        self.jump_input = QLineEdit()
        self.jump_input.setObjectName("paginationJump")
        self.jump_input.setFixedWidth(48)
        self.jump_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.jump_input.setValidator(QIntValidator(1, 9999, self))
        self.jump_input.returnPressed.connect(self._on_jump)
        self.layout.addWidget(self.jump_input)
        self.layout.addStretch()

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self._update_ui()
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
        active_fg = readable_text(primary)
        weight = "900" if t.is_brutal() else "700"
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"

        self.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                color: {fg};
                font-size: 13px;
            }}
            QPushButton {{
                background: transparent;
                border: {border_rule if t.is_pixel() else '1px solid transparent'};
                color: {fg};
                min-width: 32px;
                min-height: 32px;
                border-radius: {radius};
                font-size: 13px;
                font-weight: {weight};
                padding: 0 8px;
            }}
            QPushButton:hover {{
                color: {primary};
                background: {surface_muted};
                border-color: {border};
            }}
            QPushButton:disabled {{
                color: {muted};
                background: transparent;
                border-color: transparent;
            }}
            QPushButton[active="true"] {{
                background: {primary};
                color: {active_fg};
                border: {border_rule};
            }}
            QPushButton[active="true"]:hover {{
                color: {active_fg};
            }}
            QLineEdit#paginationJump {{
                background: {surface};
                color: {fg};
                border: {border_rule};
                border-radius: {radius};
                min-height: 28px;
                padding: 0 4px;
            }}
            QLineEdit#paginationJump:focus {{
                border-color: {primary};
            }}
        """)
        for btn in self.findChildren(QPushButton):
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

    def _update_ui(self):
        while self.buttons_layout.count():
            item = self.buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._total_pages = max(1, (self._total + self._page_size - 1) // self._page_size)
        self._current_page = max(1, min(self._current_page, self._total_pages))
        self.total_label.setText(f"共计 {self._total}")
        self.jump_input.setText(str(self._current_page))

        self._add_button("<", self._current_page > 1, lambda: self.set_current_page(self._current_page - 1))
        for page in self._page_list():
            if page == "...":
                self._add_button("...", False, None)
            else:
                self._add_button(str(page), True, lambda page=page: self.set_current_page(page), active=(page == self._current_page))
        self._add_button(">", self._current_page < self._total_pages, lambda: self.set_current_page(self._current_page + 1))
        self.set_theme_style()

    def _add_button(self, text, enabled, callback, active=False):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor if enabled else Qt.CursorShape.ArrowCursor)
        btn.setEnabled(enabled)
        btn.setProperty("active", "true" if active else "false")
        if callback is not None:
            btn.clicked.connect(callback)
        self.buttons_layout.addWidget(btn)

    def _page_list(self):
        if self._total_pages <= 7:
            return list(range(1, self._total_pages + 1))
        pages = [1]
        if self._current_page > 3:
            pages.append("...")
        start = max(2, self._current_page - 1)
        end = min(self._total_pages - 1, self._current_page + 1)
        if self._current_page <= 3:
            end = 4
        if self._current_page >= self._total_pages - 2:
            start = self._total_pages - 3
        pages.extend(range(start, end + 1))
        if self._current_page < self._total_pages - 2:
            pages.append("...")
        pages.append(self._total_pages)
        return pages

    def _on_jump(self):
        text = self.jump_input.text()
        if text.isdigit():
            self.set_current_page(int(text))

    def set_current_page(self, page):
        page = max(1, min(int(page), self._total_pages))
        if self._current_page != page:
            self._current_page = page
            self._update_ui()
            self.pageChanged.emit(self._current_page)

    def set_total(self, total):
        self._total = max(0, int(total))
        self._update_ui()

    def set_page_size(self, size):
        self._page_size = max(1, int(size))
        self._update_ui()

    @Property(int)
    def current_page(self):
        return self._current_page

    @Property(int)
    def total(self):
        return self._total
