import os
from PySide6.QtWidgets import QPushButton, QMenu, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor

from monkeyqt.themes.engine import ThemeEngine

class MkDropdown(QPushButton):
    """
    下拉菜单 (Dropdown)
    提供点击触发下拉列表的功能，全量适配 68 种主题。
    """
    itemClicked = Signal(str)

    def __init__(self, text="Dropdown", parent=None):
        super().__init__(text, parent)
        self._setup_ui()
        ThemeEngine.instance().themeChanged.connect(self.update_theme_style)
        self.update_theme_style()

    def _setup_ui(self):
        self.setCursor(Qt.PointingHandCursor)
        self.menu = QMenu(self)
        self.menu.setWindowFlags(self.menu.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMenu(self.menu)

    def update_theme_style(self, style_name: str = None):
        t = ThemeEngine
        is_dark = t.is_dark()
        fg = t.get("--fg", "#1E293B")
        surface = t.get("--surface", "#FFFFFF")
        surface_muted = t.get("--surface-muted", "#F8FAFC")
        border = t.get("--border", "#E2E8F0")
        hover_border = t.get("--input-hover-border", "rgba(255, 255, 255, 0.40)" if is_dark else "#94A3B8")
        menu_hover_bg = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.05)"

        self.setStyleSheet(f"""
            MkDropdown {{
                color: {fg};
                background-color: {surface};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 500;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            }}
            MkDropdown:hover {{
                border-color: {hover_border};
                background-color: {surface_muted};
            }}
            MkDropdown::menu-indicator {{
                image: none;
            }}
        """)

        self.menu.setStyleSheet(f"""
            QMenu {{
                background-color: {surface};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 7px 18px;
                font-size: 13px;
                color: {fg};
                border-radius: 4px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            }}
            QMenu::item:selected {{
                background-color: {menu_hover_bg};
                color: {fg};
            }}
        """)

    def add_item(self, text, item_id=""):
        if not item_id:
            item_id = text
        action = self.menu.addAction(text)
        action.setData(item_id)
        action.triggered.connect(lambda checked=False, i=item_id: self.itemClicked.emit(i))
        return action

    def add_separator(self):
        self.menu.addSeparator()
