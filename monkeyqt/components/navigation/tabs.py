from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QButtonGroup
from PySide6.QtCore import Qt, Signal
from monkeyqt.themes.engine import ThemeEngine

class MkTabButton(QPushButton):
    """标签页的单个标签按钮，自适应当前主题的高对比度下划线切换"""
    def __init__(self, tab_id, title, parent=None):
        super().__init__(title, parent)
        self.tab_id = tab_id
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        ThemeEngine.instance().themeChanged.connect(self.update_theme_style)
        self.update_theme_style()

    def update_theme_style(self):
        t = ThemeEngine
        is_dark = t.is_dark()
        muted = t.get("--text-muted", "#64748B")
        primary = t.get("--primary", "#409EFF")

        if t.is_glow() or t.is_brutal() or t.is_pixel():
            active_color = primary
            hover_color = primary
        elif is_dark:
            active_color = "#FFFFFF"
            hover_color = "#E2E8F0"
        else:
            active_color = "#0F172A"
            hover_color = "#334155"

        self.setStyleSheet(f"""
            MkTabButton {{
                border: none;
                border-bottom: 2px solid transparent;
                background: transparent;
                color: {muted};
                font-size: 14px;
                font-weight: 500;
                padding: 10px 18px;
                outline: none;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            }}
            MkTabButton:hover {{
                color: {hover_color};
            }}
            MkTabButton:checked {{
                color: {active_color};
                border-bottom: 2px solid {active_color};
                font-weight: 700;
            }}
        """)

from ..layout.widget import MkQWidget

class MkTabs(MkQWidget):
    """
    MkTabs 标签页组件
    用于平级区域大块内容的的收纳和展现，全量适配 68 种主题风格。
    """
    tabChanged = Signal(str) # 切换标签时发射 tab_id

    def __init__(self, parent=None):
        super().__init__(parent, layout="v", margins=0, spacing=15)
        self._layout = self.inner_layout

        # 1. 顶部的标签头区域
        self.header_widget = MkQWidget(role="transparent", layout="h", margins=0, spacing=0)
        self.header_layout = self.header_widget.inner_layout
        self.header_layout.addStretch() # 靠左对齐

        self._layout.addWidget(self.header_widget)

        # 管理标签按钮的互斥
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self._on_tab_clicked)

        # 2. 下方的内容区域
        self.content_area = QStackedWidget()
        self._layout.addWidget(self.content_area, stretch=1)

        self._tabs = {} # tab_id -> widget

        self.update_theme_style()

    def on_theme_changed(self, theme_name: str = ""):
        self.update_theme_style()

    def update_theme_style(self):
        t = ThemeEngine
        border = t.get("--border", "#E2E8F0")
        self.header_widget.setStyleSheet(f"""
            QWidget {{
                border-bottom: 1px solid {border};
                background: transparent;
            }}
        """)

    def add_tab(self, tab_id: str, title: str, widget: QWidget):
        """添加一个新标签页"""
        # 添加头部按钮
        btn = MkTabButton(tab_id, title)
        self.button_group.addButton(btn)
        self.header_layout.insertWidget(self.header_layout.count() - 1, btn)

        # 添加内容
        self.content_area.addWidget(widget)
        self._tabs[tab_id] = widget

        # 如果是第一个标签，默认选中
        if len(self._tabs) == 1:
            btn.setChecked(True)
            self.content_area.setCurrentWidget(widget)

    def _on_tab_clicked(self, btn):
        tab_id = btn.tab_id
        widget = self._tabs.get(tab_id)
        if widget:
            self.content_area.setCurrentWidget(widget)
            self.tabChanged.emit(tab_id)

    def set_active(self, tab_id: str):
        """代码切换标签"""
        for btn in self.button_group.buttons():
            if btn.tab_id == tab_id:
                btn.setChecked(True)
                self._on_tab_clicked(btn)
                break
