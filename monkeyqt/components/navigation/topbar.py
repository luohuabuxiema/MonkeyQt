from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QButtonGroup, QSizePolicy, QWidget
from PySide6.QtCore import Qt, Signal
from monkeyqt.themes.engine import ThemeEngine

class MkTopbarItem(QPushButton):
    """顶部导航栏菜单项"""
    def __init__(self, item_id, text, parent=None):
        super().__init__(text, parent)
        self.item_id = item_id
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 允许按钮在垂直方向上充满父容器，这样底部边框才会贴紧底边
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(80) # 保证每个菜单项有足够的宽度
        
        ThemeEngine.instance().themeChanged.connect(self.update_theme_style)
        self.update_theme_style()

    def update_theme_style(self, style_name: str = None):
        t = ThemeEngine
        is_dark = t.is_dark()
        fg = t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        primary = t.get("--primary", "#409EFF")
        active_color = primary if (t.is_glow() or t.is_brutal() or t.is_pixel()) else ("#FFFFFF" if is_dark else "#0F172A")
        hover_color = "#FFFFFF" if is_dark else "#0F172A"
        hover_bg = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.04)"

        self.setStyleSheet(f"""
            MkTopbarItem {{
                border: none;
                border-bottom: 2px solid transparent;
                background: transparent;
                color: {muted};
                font-size: 14px;
                font-weight: 500;
                padding: 0 20px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            }}
            MkTopbarItem:hover {{
                color: {hover_color};
                background-color: {hover_bg};
            }}
            MkTopbarItem:checked {{
                color: {active_color};
                border-bottom: 2px solid {active_color};
                font-weight: 700;
            }}
        """)

class MkTopbar(QFrame):
    """
    MkTopbar 顶部导航栏组件
    适用于全站的主导航，全量自适应 68 种主题风格。
    """
    itemClicked = Signal(str)

    def __init__(self, logo_text="LOGO", parent=None):
        super().__init__(parent)
        self.setObjectName("mk-topbar")
        self._logo_text = logo_text
        
        # 锁定导航栏高度，这在桌面端非常常见
        self.setFixedHeight(60)

        # 主布局，横向排列
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 0, 20, 0) # 上下边距为0，让 Item 占满高度
        self.layout.setSpacing(10)

        # 1. 左侧 LOGO
        if logo_text:
            self.logo_label = QLabel(logo_text)
            self.layout.addWidget(self.logo_label)
        else:
            self.logo_label = None

        ThemeEngine.instance().themeChanged.connect(self.update_theme_style)
        self.update_theme_style()

        # 2. 管理所有菜单项的互斥逻辑
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self._on_button_clicked)

        # 3. 菜单项容器
        # 这里专门套一层 Layout，不使用主 layout 的 stretch，防止菜单项被过度拉伸
        self.items_layout = QHBoxLayout()
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(0) # 菜单项之间无缝衔接
        self.layout.addLayout(self.items_layout)

        # 4. 右侧添加弹簧，将所有菜单项向左推
        self.layout.addStretch()

    def add_item(self, item_id: str, text: str) -> MkTopbarItem:
        """动态向导航栏添加一级菜单"""
        btn = MkTopbarItem(item_id, text)
        self.button_group.addButton(btn)
        self.items_layout.addWidget(btn)
        return btn

    def _on_button_clicked(self, btn):
        self.itemClicked.emit(btn.item_id)
        
    def set_active(self, item_id: str):
        """手动设置某个项为高亮状态"""
        for btn in self.button_group.buttons():
            if btn.item_id == item_id:
                btn.setChecked(True)
                break

    def update_theme_style(self, style_name: str = None):
        t = ThemeEngine
        surface = t.get("--surface", "#FFFFFF")
        border = t.get("--border", "#E2E8F0")
        fg = t.get("--fg", "#1E293B")
        self.setStyleSheet(f"""
            #mk-topbar {{
                background-color: {surface};
                border-bottom: 1px solid {border};
            }}
        """)
        if hasattr(self, "logo_label") and self.logo_label:
            self.logo_label.setStyleSheet(f"""
                QLabel {{
                    color: {fg};
                    font-size: 18px;
                    font-weight: 700;
                    letter-spacing: 1px;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
                    padding-right: 24px;
                }}
            """)
