import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit, QSizePolicy
from PySide6.QtCore import Qt, Signal, Property
from PySide6.QtGui import QIntValidator

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import readable_text
from ..layout.widget import MkQWidget


class MkPagination(MkQWidget):
    """
    分页器 (Pagination) 组件
    自适应 68 种主题风格的高清矢量翻页组件，暗色/亮色自动采用现代高对比度 ChatGPT/Ultralytics 胶囊样式。
    """
    pageChanged = Signal(int)

    def __init__(self, total=0, page_size=10, current=1, parent=None):
        super().__init__(parent)
        self._total = total
        self._page_size = page_size
        self._current_page = current
        self._total_pages = max(1, (self._total + self._page_size - 1) // self._page_size)

        self._setup_ui()
        self.set_theme_style()
        self._update_ui()

    def on_theme_changed(self, theme_name: str = ""):
        self.set_theme_style()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        is_dark = t.is_dark()
        fg = t.get("--fg", "#1E293B")
        surface = t.get("--surface", "#FFFFFF")
        surface_muted = t.get("--surface-muted", "#F8FAFC")
        border = t.get("--border", "#E2E8F0")
        muted = t.get("--text-muted", "#64748B")
        primary = t.get("--primary", "#409EFF")

        disabled_fg = t.get("--text-disabled", "#52525B" if is_dark else "#A1A1AA")

        if t.is_glow() or t.is_brutal() or t.is_pixel():
            active_bg = primary
            active_fg = readable_text(primary)
            active_border = primary
            hover_fg = primary
            hover_bg = surface_muted
        elif is_dark:
            active_bg = "#27272A"
            active_fg = "#FFFFFF"
            active_border = "rgba(255, 255, 255, 0.12)"
            hover_fg = "#FFFFFF"
            hover_bg = "rgba(255, 255, 255, 0.08)"
        else:
            active_bg = "#0F172A"
            active_fg = "#FFFFFF"
            active_border = "#0F172A"
            hover_fg = "#0F172A"
            hover_bg = "rgba(0, 0, 0, 0.05)"

        focus_border = t.get("--input-focus-border", "#FFFFFF" if is_dark else "#0F172A")
        hover_border = t.get("--input-hover-border", "rgba(255, 255, 255, 0.40)" if is_dark else "#94A3B8")

        self.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid transparent;
                background-color: transparent;
                color: {fg};
                min-width: 32px;
                min-height: 32px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                outline: none;
            }}
            QPushButton:hover {{
                color: {hover_fg};
                background-color: {hover_bg};
            }}
            QPushButton:disabled {{
                color: {disabled_fg};
                background-color: transparent;
                border: 1px solid transparent;
            }}
            QPushButton[class="active"] {{
                background-color: {active_bg};
                color: {active_fg};
                border: 1px solid {active_border};
                font-weight: 600;
            }}
            QPushButton[class="active"]:hover {{
                background-color: {active_bg};
                color: {active_fg};
            }}
            QLabel {{
                color: {disabled_fg};
                font-size: 13px;
                margin: 0 4px;
                background: transparent;
                border: none;
            }}
            QLineEdit {{
                border: 1px solid {border};
                border-radius: 6px;
                color: {fg};
                background-color: {surface};
                min-width: 40px;
                max-width: 40px;
                min-height: 26px;
                max-height: 28px;
                text-align: center;
                padding: 0 4px;
            }}
            QLineEdit:hover {{
                border-color: {hover_border};
            }}
            QLineEdit:focus {{
                border-color: {focus_border};
            }}
        """)

    def _setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 2, 0, 2)
        self.layout.setSpacing(4)
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Total label
        self.total_label = QLabel(f"共计 {self._total}")
        self.layout.addWidget(self.total_label)

        # Buttons layout
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(4)
        self.layout.addLayout(self.buttons_layout)

        # Jump layout
        self.jump_layout = QHBoxLayout()
        self.jump_layout.setSpacing(4)
        self.jump_layout.addWidget(QLabel("页"))
        
        self.jump_input = QLineEdit(str(self._current_page))
        self.jump_input.setValidator(QIntValidator(1, 9999))
        self.jump_input.setAlignment(Qt.AlignCenter)
        self.jump_input.returnPressed.connect(self._on_jump)
        self.jump_layout.addWidget(self.jump_input)

        self.layout.addLayout(self.jump_layout)

    def _update_ui(self):
        # Clear existing buttons
        while self.buttons_layout.count():
            item = self.buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._total_pages = max(1, (self._total + self._page_size - 1) // self._page_size)
        self.total_label.setText(f"共计 {self._total}")
        self.jump_input.setText(str(self._current_page))

        # Prev button
        prev_btn = QPushButton("◀")
        prev_btn.setCursor(Qt.PointingHandCursor)
        prev_btn.setEnabled(self._current_page > 1)
        prev_btn.clicked.connect(lambda: self.set_current_page(self._current_page - 1))
        self.buttons_layout.addWidget(prev_btn)

        # Page buttons logic (simplified for now, showing max 7 buttons)
        pages = self._get_page_list()
        for p in pages:
            if p == "...":
                btn = QPushButton("...")
                btn.setEnabled(False)
            else:
                btn = QPushButton(str(p))
                btn.setCursor(Qt.PointingHandCursor)
                if p == self._current_page:
                    btn.setProperty("class", "active")
                btn.clicked.connect(lambda *args, page=p: self.set_current_page(page))
            self.buttons_layout.addWidget(btn)

        # Next button
        next_btn = QPushButton("▶")
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.setEnabled(self._current_page < self._total_pages)
        next_btn.clicked.connect(lambda: self.set_current_page(self._current_page + 1))
        self.buttons_layout.addWidget(next_btn)

    def _get_page_list(self):
        # Always show 1, last, and around current
        if self._total_pages <= 7:
            return list(range(1, self._total_pages + 1))
        
        pages = [1]
        if self._current_page > 3:
            pages.append("...")
        
        start = max(2, self._current_page - 1)
        end = min(self._total_pages - 1, self._current_page + 1)
        
        # Adjust if current page is near the edges
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
            page = int(text)
            self.set_current_page(page)

    def set_current_page(self, page):
        page = max(1, min(page, self._total_pages))
        if self._current_page != page:
            self._current_page = page
            self._update_ui()
            self.pageChanged.emit(self._current_page)

    def set_total(self, total):
        self._total = max(0, total)
        self._update_ui()

    def set_page_size(self, size):
        self._page_size = max(1, size)
        self._update_ui()

    @Property(int)
    def current_page(self):
        return self._current_page

    @Property(int)
    def total(self):
        return self._total
