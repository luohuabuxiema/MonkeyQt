# -*- coding: utf-8 -*-
"""Quick test for the enable_titlebar_extras API without YOLO dependencies."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QStackedWidget, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from monkeyqt import MkMenu, MkWindow, MkMessage, use_theme, MkSwitch, MkSlider, MkAvatar
from monkeyqt.core.icons import MkPhosphorIcon


class TestApp(MkWindow):
    def __init__(self):
        super().__init__(
            use_custom_title_bar=True,
            preset="default",
            sidebar_full_height=True,
        )

        self.titlebar._height = 48
        self.titlebar._border_bottom = "none"
        self.titlebar.apply_theme_colors()
        self.titlebar.rebuild_layout()
        self.update_style()

        self.setWindowTitle("标题栏头像 + 前进后退测试")
        self.resize(1200, 800)

        # --- 主布局 ---
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- 侧边栏 ---
        self.sidebar = MkMenu(title="导航测试", collapse_mode="hamburger")
        self.sidebar.set_border_right("none")
        self.sidebar.add_item("home", "首页", icon="house")
        self.sidebar.add_item("data", "数据分析", icon="chart-bar")
        self.sidebar.add_item("settings", "历史记录", icon="gear")
        self.main_layout.addWidget(self.sidebar)

        # --- 右侧内容区 ---
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(20, 20, 20, 20)
        self.right_layout.setSpacing(20)

        self.content_area = QStackedWidget()

        self.page_home = self._create_page("🏠 首页控制台", "#409eff")
        self.page_data = self._create_page("📊 数据分析面板", "#67c23a")
        self.page_settings = self._create_page("⚙️ 历史记录", "#e6a23c")
        self.page_profile = self._create_profile_page()
        self.page_app_settings = self._create_settings_page()

        self.page_home.setObjectName("home")
        self.page_data.setObjectName("data")
        self.page_settings.setObjectName("settings")
        self.page_profile.setObjectName("profile")
        self.page_app_settings.setObjectName("app_settings")

        self.content_area.addWidget(self.page_home)
        self.content_area.addWidget(self.page_data)
        self.content_area.addWidget(self.page_settings)
        self.content_area.addWidget(self.page_profile)
        self.content_area.addWidget(self.page_app_settings)

        self.right_layout.addWidget(self.content_area, stretch=1)
        self.main_layout.addWidget(self.right_widget, stretch=1)

        self.sidebar.itemClicked.connect(self.on_menu_clicked)
        self.setCentralWidget(self.central_widget)

        # --- 一行代码启用 ---
        self.enable_titlebar_extras(
            avatar=True,
            history_nav=True,
            user_name="落花不写码",
            subtitle="PySide6 组件开发者",
            avatar_size=32,
            nav_icon_only=True,
            avatar_actions=[
                {"id": "profile", "text": "个人主页", "icon": "user"},
                {"id": "settings", "text": "设置", "icon": "gear"},
                {"id": "logout", "text": "退出登录", "icon": "sign-out", "separator_before": True},
            ],
        )

        if self.titlebar_avatar:
            self.titlebar_avatar.actionTriggered.connect(self._on_avatar_action)

        # 绑定历史导航变化信号，同步侧边栏选中状态
        if self.titlebar_history_nav:
            self.titlebar_history_nav.pageChanged.connect(self._on_page_changed)

        self.sidebar.set_active("home")

    def on_menu_clicked(self, item_id):
        if self.titlebar_history_nav:
            self.titlebar_history_nav.navigate(item_id)

    def _on_page_changed(self, page_id):
        """当历史页面（前进/后退）切换时，同步高亮侧边栏对应的菜单项"""
        found = False
        for item in self.sidebar._all_items:
            if item.item_id == page_id:
                item.setChecked(True)
                for other in self.sidebar._all_items:
                    if other != item:
                        other.setChecked(False)
                found = True
                break
        if not found:
            # 说明跳转到了非侧边栏页面（如个人主页、系统设置等），清除侧边栏所有的选中高亮
            for item in self.sidebar._all_items:
                item.setChecked(False)

    def _on_avatar_action(self, action_id):
        if action_id == "profile":
            if self.titlebar_history_nav:
                self.titlebar_history_nav.navigate("profile")
        elif action_id == "settings":
            if self.titlebar_history_nav:
                self.titlebar_history_nav.navigate("app_settings")
        elif action_id == "logout":
            MkMessage.success(self, "账号已安全登出！")

    def _create_page(self, text, color):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(text)
        label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page

    def _create_profile_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(20)

        # 用户信息
        user_card = QWidget()
        user_layout = QHBoxLayout(user_card)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(20)

        large_avatar = MkAvatar(text="落花", size=80, shape="circle")
        user_layout.addWidget(large_avatar)

        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(6)

        name_lbl = QLabel("落花不写码")
        name_lbl.setStyleSheet("font-size: 22px; font-weight: bold;")
        meta_lbl = QLabel("42 个项目    1.2K Star    68 种主题")
        meta_lbl.setStyleSheet("font-size: 12px; color: #8e8e8e;")
        bio_lbl = QLabel("PySide6 / MonkeyQt 组件开发者 · 学习新思想，争做新青年")
        bio_lbl.setStyleSheet("font-size: 13px; color: #666666;")

        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tag_location = QLabel("📍 广西 · 南宁")
        tag_location.setStyleSheet(
            "color: #5b8ff9; background-color: rgba(91, 143, 249, 0.1);"
            "padding: 3px 10px; border-radius: 4px; font-size: 11px;"
        )
        tag_school = QLabel("🎓 吗喽大学")
        tag_school.setStyleSheet(
            "color: #61c454; background-color: rgba(97, 196, 84, 0.1);"
            "padding: 3px 10px; border-radius: 4px; font-size: 11px;"
        )
        tags_layout.addWidget(tag_location)
        tags_layout.addWidget(tag_school)
        tags_layout.addStretch()

        info_layout.addWidget(name_lbl)
        info_layout.addWidget(meta_lbl)
        info_layout.addWidget(bio_lbl)
        info_layout.addLayout(tags_layout)

        user_layout.addWidget(info_widget, stretch=1)
        layout.addWidget(user_card)

        # 统计卡片
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        stats_data = [
            ("🔧", "组件数量", "36 个", "#409EFF"),
            ("🎨", "主题风格", "68 种", "#67C23A"),
            ("⭐", "GitHub Star", "1,247", "#E6A23C"),
            ("📦", "版本号", "v0.1.1", "#F56C6C"),
        ]
        for emoji, title, value, color in stats_data:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid #e8e8e8;
                    border-radius: 8px;
                    border-left: 3px solid {color};
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 12, 16, 12)
            header = QLabel(f"{emoji}  {title}")
            header.setStyleSheet("font-size: 12px; color: #999999;")
            value_lbl = QLabel(value)
            value_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
            card_layout.addWidget(header)
            card_layout.addWidget(value_lbl)
            stats_layout.addWidget(card)

        layout.addLayout(stats_layout)

        # 最近项目
        projects_title = QLabel("最近项目")
        projects_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(projects_title)

        grid = QGridLayout()
        grid.setSpacing(14)
        projects = [
            ("MonkeyQt 组件库", "PySide6 现代化 UI 组件", "chart-bar", "#409EFF"),
            ("YOLO 目标检测", "基于 YOLOv8 的实时检测系统", "eye", "#67C23A"),
            ("主题引擎", "68 种 UI 风格动态切换", "paint-brush", "#E6A23C"),
        ]
        for idx, (title, desc, icon, color) in enumerate(projects):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid #e8e8e8;
                    border-radius: 8px;
                }}
                QFrame:hover {{ border-color: {color}; }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 16, 16, 16)
            card_layout.setSpacing(8)
            icon_lbl = QLabel()
            icon_lbl.setPixmap(MkPhosphorIcon.get_pixmap(icon, color, 28))
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("font-size: 12px; color: #999999;")
            desc_lbl.setWordWrap(True)
            card_layout.addWidget(icon_lbl)
            card_layout.addWidget(title_lbl)
            card_layout.addWidget(desc_lbl)
            card_layout.addStretch()
            grid.addWidget(card, 0, idx)

        layout.addLayout(grid)
        layout.addStretch()
        return page

    def _create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(20)

        title = QLabel("系统设置")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 8px;
            }
            QLabel { font-size: 13px; border: none; background: transparent; }
        """)
        frame_layout = QVBoxLayout(settings_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(24)

        for label_text, widget_cls, kwargs in [
            ("自动保存检测结果", MkSwitch, {"checked": True}),
            ("深色模式", MkSwitch, {"checked": False}),
            ("界面动画效果", MkSwitch, {"checked": True}),
        ]:
            opt_layout = QHBoxLayout()
            opt_lbl = QLabel(label_text)
            opt_widget = widget_cls(**kwargs)
            opt_layout.addWidget(opt_lbl)
            opt_layout.addStretch()
            opt_layout.addWidget(opt_widget)
            frame_layout.addLayout(opt_layout)

        opt_layout = QHBoxLayout()
        opt_lbl = QLabel("默认置信度阈值")
        opt_slider = MkSlider(Qt.Horizontal)
        opt_slider.setRange(0, 100)
        opt_slider.setValue(25)
        opt_slider.setFixedWidth(150)
        opt_layout.addWidget(opt_lbl)
        opt_layout.addStretch()
        opt_layout.addWidget(opt_slider)
        frame_layout.addLayout(opt_layout)

        layout.addWidget(settings_frame)

        desc = QLabel("说明：以上选项将在下次启动时生效。")
        desc.setStyleSheet("color: #999999; font-size: 12px; font-style: italic;")
        layout.addWidget(desc)
        layout.addStretch()
        return page


if __name__ == "__main__":
    app = QApplication(sys.argv)
    use_theme("HUD 科幻界面")
    window = TestApp()
    window.show()
    sys.exit(app.exec())
