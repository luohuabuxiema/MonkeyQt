# -*- coding: utf-8 -*-
"""
@File ：navigation_demo.py
@Desc ：MonkeyQt Custom Title Bar Navigation & Personal Center Demo
       - Left Sidebar (Full Height)
       - Title Bar Custom Widgets (Forward/Backward buttons, Search input, User Avatar)
       - Avatar Dropdown Menu (Profile, Settings)
       - Multi-page history navigation tracking (Forward/Backward logic)
"""
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QStackedWidget, QPushButton, QLineEdit, QMenu, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QSize, QPoint
from PySide6.QtGui import QFont, QCursor, QColor, QPixmap, QIcon

# Insert parent path to import monkeyqt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from monkeyqt import (
    MkWindow, MkMenu, MkAvatar, MkButton, MkSwitch, MkSlider, MkMessage
)
from monkeyqt.core.icons import MkPhosphorIcon


class ClickableAvatar(MkAvatar):
    """可点击的头像组件"""
    clicked = Signal()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()
        else:
            super().mousePressEvent(event)


class NavigationWindow(MkWindow):
    def __init__(self):
        # 使用自定义标题栏，且预设风格为 "soda" (汽水音乐风格，黑色半透明无框)
        super().__init__(use_custom_title_bar=True, preset="soda")
        self.setWindowTitle("汽水音乐 - MonkeyQt 导航与个人中心演示")
        self.resize(1000, 700)
        
        # 启用侧边栏占满整个窗口高度（左侧侧边栏直通顶部，右侧内容区带独立标题栏）
        self.set_sidebar_full_height(True)
        
        # 导航历史状态记录
        self.navigation_history = []
        self.history_index = -1
        
        self.init_ui()
        self.init_navigation()

    def init_ui(self):
        # 1. 侧边栏初始化
        self.sidebar = MkMenu(title="汽水音乐", icon="play")
        # 修改侧边栏样式为极暗风格，匹配汽水音乐
        self.sidebar.inner_frame.setStyleSheet("""
            QFrame#SidebarInnerFrame {
                background-color: #121212;
                border-right: 1px solid #1a1a1a;
            }
        """)
        self.sidebar.title_label.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        self.sidebar.setStyleSheet("""
            QLabel {
                color: #8e8e8e;
            }
            MkMenuItem {
                background: transparent;
            }
            MkMenuItem QPushButton {
                background: transparent;
            }
        """)
        
        # 添加侧边栏项
        self.sidebar.add_item("recommend", "推荐", "house")
        self.sidebar.add_item("listen", "听歌模式", "speaker-high")
        self.sidebar.add_item("profile", "个人主页", "user")
        self.sidebar.add_item("settings", "设置", "gear")
        
        # 2. 右侧主体容器
        self.central_widget = QWidget()
        self.central_widget.setObjectName("GalleryCentralWidget")
        self.central_widget.setStyleSheet("background-color: #0d0d0d;")
        
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 右侧页堆栈容器
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("GalleryContentArea")
        self.content_area.setContentsMargins(30, 20, 30, 30)
        
        # 初始化子页面
        self.page_recommend = self.create_recommend_page()
        self.page_listen = self.create_listen_page()
        self.page_profile = self.create_profile_page()
        self.page_settings = self.create_settings_page()
        
        self.content_area.addWidget(self.page_recommend)
        self.content_area.addWidget(self.page_listen)
        self.content_area.addWidget(self.page_profile)
        self.content_area.addWidget(self.page_settings)
        
        main_layout.addWidget(self.content_area, stretch=1)
        
        # 绑定侧边栏切换事件
        self.sidebar.itemClicked.connect(self.on_sidebar_clicked)
        
        # 设置窗口的中心 Widget（这会把 sidebar 提到左边，内容放到右侧 content host 里）
        self.setCentralWidget(self.central_widget)
        
        # 3. 自定义标题栏 (右侧内容区上方的 Header)
        # soda 预设默认在 center_layout 里添加了 search_input 占位，我们先清空重新布局
        while self.titlebar.center_layout.count():
            item = self.titlebar.center_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.titlebar.center_layout.setContentsMargins(10, 0, 10, 0)
        self.titlebar.center_layout.setSpacing(12)
        
        # 前进后退按钮
        self.btn_back = QPushButton()
        self.btn_back.setFixedSize(28, 28)
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setIcon(MkPhosphorIcon.get_icon("caret-left", "#ffffff", "#8e8e8e", 14))
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 0.02);
                opacity: 0.3;
            }
        """)
        self.btn_back.clicked.connect(self.go_back)
        
        self.btn_forward = QPushButton()
        self.btn_forward.setFixedSize(28, 28)
        self.btn_forward.setCursor(Qt.PointingHandCursor)
        self.btn_forward.setIcon(MkPhosphorIcon.get_icon("caret-right", "#ffffff", "#8e8e8e", 14))
        self.btn_forward.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 0.02);
                opacity: 0.3;
            }
        """)
        self.btn_forward.clicked.connect(self.go_forward)
        
        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 歌手、歌曲或专辑名")
        self.search_input.setFixedWidth(200)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 14px;
                padding: 4px 12px 4px 28px;
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.12);
            }
        """)
        
        # 模拟 AI 写歌标签按钮
        self.btn_ai = QPushButton("♫ AI写歌")
        self.btn_ai.setStyleSheet("""
            QPushButton {
                background-color: #fe3c5a;
                border: none;
                border-radius: 14px;
                color: #ffffff;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #ff5672;
            }
        """)
        self.btn_ai.clicked.connect(lambda: MkMessage.info(self, "AI 创作灵感功能正在内测中..."))
        
        # 标题栏右上角用户头像 (ClickableAvatar)
        # 尝试使用现有的素材图，若无则显示默认文字
        base_dir = os.path.dirname(os.path.abspath(__file__))
        avatar_path = os.path.join(base_dir, "..", "gallery", "assets", "after.png")
        if not os.path.exists(avatar_path):
            avatar_path = ""
            
        self.avatar = ClickableAvatar(text="Me", image_path=avatar_path, size=28, shape="circle")
        self.avatar.setCursor(Qt.PointingHandCursor)
        self.avatar.clicked.connect(self.show_avatar_menu)
        
        # 头像点击菜单
        self.avatar_menu = QMenu(self)
        self.avatar_menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                border: 1px solid #2d2d2d;
                border-radius: 6px;
                padding: 4px 0px;
            }
            QMenu::item {
                color: #cccccc;
                font-size: 13px;
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 0.08);
                color: #ffffff;
            }
        """)
        
        act_profile = self.avatar_menu.addAction("个人主页")
        act_settings = self.avatar_menu.addAction("设置")
        self.avatar_menu.addSeparator()
        act_logout = self.avatar_menu.addAction("退出登录")
        
        act_profile.triggered.connect(lambda: self.navigate_to("profile"))
        act_settings.triggered.connect(lambda: self.navigate_to("settings"))
        act_logout.triggered.connect(lambda: MkMessage.success(self, "账号已安全登出！"))

        # 将这些组件添加到标题栏的 center_layout
        self.titlebar.center_layout.addWidget(self.btn_back)
        self.titlebar.center_layout.addWidget(self.btn_forward)
        self.titlebar.center_layout.addSpacing(10)
        self.titlebar.center_layout.addWidget(self.search_input)
        self.titlebar.center_layout.addStretch()
        self.titlebar.center_layout.addWidget(self.btn_ai)
        self.titlebar.center_layout.addWidget(self.avatar)
        self.titlebar.center_layout.addSpacing(10)

    # ──────────── 页面创建逻辑 ────────────
    
    def create_recommend_page(self) -> QWidget:
        """推荐页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        title = QLabel("个性推荐")
        title.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # 放置 6 个推荐歌单盒子
        cards_data = [
            ("为你推荐的宝藏小语种", "#ff7a00"),
            ("精选硬核说唱：炸街专属", "#00a896"),
            ("舒缓白噪音：今夜好眠", "#4f46e5"),
            ("80年代华语怀旧经典金曲", "#fe3c5a"),
            ("适合写代码的纯音乐合集", "#059669"),
            ("午后提神：动感电子乐", "#db2777"),
        ]
        
        for idx, (name, color) in enumerate(cards_data):
            card = QFrame()
            card.setFixedSize(140, 180)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 12, 12, 12)
            
            icon_lbl = QLabel()
            icon_lbl.setPixmap(MkPhosphorIcon.get_pixmap("play", "#ffffff", 24))
            icon_lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)
            
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: bold;")
            name_lbl.setWordWrap(True)
            
            card_layout.addWidget(icon_lbl)
            card_layout.addStretch()
            card_layout.addWidget(name_lbl)
            
            row = idx // 3
            col = idx % 3
            grid.addWidget(card, row, col)
            
        layout.addLayout(grid)
        layout.addStretch()
        return page

    def create_listen_page(self) -> QWidget:
        """听歌模式页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        title = QLabel("听歌模式")
        title.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # 显示模拟唱片
        disc_frame = QFrame()
        disc_frame.setFixedSize(240, 240)
        disc_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 8px solid #333333;
                border-radius: 120px;
            }
        """)
        disc_layout = QVBoxLayout(disc_frame)
        
        inner_disc = QFrame()
        inner_disc.setFixedSize(100, 100)
        inner_disc.setStyleSheet("""
            QFrame {
                background-color: #fe3c5a;
                border-radius: 50px;
            }
        """)
        inner_disc_layout = QVBoxLayout(inner_disc)
        
        note_lbl = QLabel("♫")
        note_lbl.setStyleSheet("color: #ffffff; font-size: 28px;")
        note_lbl.setAlignment(Qt.AlignCenter)
        inner_disc_layout.addWidget(note_lbl)
        
        disc_layout.addWidget(inner_disc, alignment=Qt.AlignCenter)
        layout.addWidget(disc_frame, alignment=Qt.AlignCenter)
        
        lyrics = QLabel("Let it be, let it be...\nWhisper words of wisdom, let it be.")
        lyrics.setStyleSheet("color: #8e8e8e; font-size: 14px; font-style: italic; line-height: 24px;")
        lyrics.setAlignment(Qt.AlignCenter)
        layout.addWidget(lyrics)
        
        layout.addStretch()
        return page

    def create_profile_page(self) -> QWidget:
        """个人主页 (高保真还原第一张截图)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # 头部用户信息卡片
        user_card = QWidget()
        user_layout = QHBoxLayout(user_card)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(20)
        
        # 大头像
        base_dir = os.path.dirname(os.path.abspath(__file__))
        avatar_path = os.path.join(base_dir, "..", "gallery", "assets", "after.png")
        if not os.path.exists(avatar_path):
            avatar_path = ""
        large_avatar = MkAvatar(text="Me", image_path=avatar_path, size=80, shape="circle")
        user_layout.addWidget(large_avatar)
        
        # 用户详细信息
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(6)
        
        name_lbl = QLabel("Let it be")
        name_lbl.setStyleSheet("color: #ffffff; font-size: 22px; font-weight: bold;")
        
        meta_lbl = QLabel("11 关注    24.8K 粉丝    0 获赞")
        meta_lbl.setStyleSheet("color: #8e8e8e; font-size: 12px;")
        
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        
        tag_gender = QLabel("♂ 广西 · 南宁 · 青秀")
        tag_gender.setStyleSheet("color: #b0c4de; background-color: rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        tag_school = QLabel("吗喽大学")
        tag_school.setStyleSheet("color: #cccccc; background-color: rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        tags_layout.addWidget(tag_gender)
        tags_layout.addWidget(tag_school)
        tags_layout.addStretch()
        
        info_layout.addWidget(name_lbl)
        info_layout.addWidget(meta_lbl)
        info_layout.addLayout(tags_layout)
        
        user_layout.addWidget(info_widget, stretch=1)
        
        # 会员中心按钮
        vip_btn = QPushButton("会员中心")
        vip_btn.setFixedSize(80, 30)
        vip_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 15px;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        user_layout.addWidget(vip_btn, alignment=Qt.AlignTop)
        
        layout.addWidget(user_card)
        
        # 歌单分类标题
        playlist_title = QLabel("创建的歌单")
        playlist_title.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(playlist_title)
        
        # 歌单列表 (Grid)
        grid = QGridLayout()
        grid.setSpacing(15)
        
        playlists = [
            ("我喜欢的音乐", "heart", "#fe3c5a"),
            ("抖音收藏的音乐", "play", "#00f2fe"),
            ("哥哥爱复古", "music-notes", "#ffa500")
        ]
        
        for idx, (title, icon, color) in enumerate(playlists):
            playlist_card = QFrame()
            playlist_card.setFixedSize(140, 180)
            playlist_card.setStyleSheet("""
                QFrame {
                    background-color: #181818;
                    border: 1px solid #2a2a2a;
                    border-radius: 6px;
                }
                QFrame:hover {
                    border-color: #444444;
                }
            """)
            card_layout = QVBoxLayout(playlist_card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            
            # 封面大图区 (圆角单色背景，加居中图标)
            cover_lbl = QLabel()
            cover_lbl.setFixedSize(120, 120)
            cover_lbl.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            cover_lbl.setPixmap(MkPhosphorIcon.get_pixmap("play" if icon=="play" else "eye", "#ffffff", 32))
            cover_lbl.setAlignment(Qt.AlignCenter)
            
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: bold; margin-top: 6px;")
            title_lbl.setWordWrap(True)
            
            card_layout.addWidget(cover_lbl)
            card_layout.addWidget(title_lbl)
            card_layout.addStretch()
            
            grid.addWidget(playlist_card, 0, idx)
            
        layout.addLayout(grid)
        layout.addStretch()
        return page

    def create_settings_page(self) -> QWidget:
        """设置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        title = QLabel("系统设置")
        title.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # 选项框容器
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #121212;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
            }
            QLabel {
                color: #cccccc;
                font-size: 13px;
                background: transparent;
            }
        """)
        
        frame_layout = QVBoxLayout(settings_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(24)
        
        # 1. 独立音质设置
        opt_layout1 = QHBoxLayout()
        opt_lbl1 = QLabel("无损超高音质")
        opt_switch1 = MkSwitch(checked=True)
        opt_layout1.addWidget(opt_lbl1)
        opt_layout1.addStretch()
        opt_layout1.addWidget(opt_switch1)
        frame_layout.addLayout(opt_layout1)
        
        # 2. 界面过渡效果
        opt_layout2 = QHBoxLayout()
        opt_lbl2 = QLabel("音量均衡")
        opt_slider = MkSlider(Qt.Horizontal)
        opt_slider.setRange(0, 100)
        opt_slider.setValue(60)
        opt_slider.setFixedWidth(150)
        opt_layout2.addWidget(opt_lbl2)
        opt_layout2.addStretch()
        opt_layout2.addWidget(opt_slider)
        frame_layout.addLayout(opt_layout2)
        
        # 3. 独立下载配置
        opt_layout3 = QHBoxLayout()
        opt_lbl3 = QLabel("退出时清除缓存")
        opt_switch3 = MkSwitch(checked=False)
        opt_layout3.addWidget(opt_lbl3)
        opt_layout3.addStretch()
        opt_layout3.addWidget(opt_switch3)
        frame_layout.addLayout(opt_layout3)
        
        layout.addWidget(settings_frame)
        
        # 说明文字
        desc = QLabel("说明：此处的选项已适配并启用了暗色模式下的 UI 样式。")
        desc.setStyleSheet("color: #8e8e8e; font-size: 12px; font-style: italic;")
        layout.addWidget(desc)
        
        layout.addStretch()
        return page

    # ──────────── 页面跳转与历史导航核心逻辑 ────────────
    
    def init_navigation(self):
        # 初始定位在推荐页面
        self.navigate_to("recommend", record_history=True)

    def on_sidebar_clicked(self, item_id):
        # 排除折叠项
        if item_id == "collapse":
            return
        self.navigate_to(item_id, record_history=True)

    def navigate_to(self, page_name: str, record_history=True):
        # 映射 page_name 对应的 widget 和 sidebar active_id
        page_widgets = {
            "recommend": self.page_recommend,
            "listen": self.page_listen,
            "profile": self.page_profile,
            "settings": self.page_settings,
        }
        
        target_widget = page_widgets.get(page_name)
        if not target_widget:
            return
            
        if record_history:
            # 如果是主动跳转，截断历史记录并存入新记录
            if self.history_index < len(self.navigation_history) - 1:
                self.navigation_history = self.navigation_history[:self.history_index + 1]
            self.navigation_history.append(page_name)
            self.history_index += 1
            
        # 设置当前显示的页面 Widget
        self.content_area.setCurrentWidget(target_widget)
        
        # 同步侧边栏菜单的高亮选中状态 ( blockSignals 避免循环触发 )
        self.sidebar.itemClicked.disconnect(self.on_sidebar_clicked)
        self.sidebar.set_active(page_name)
        self.sidebar.itemClicked.connect(self.on_sidebar_clicked)
        
        # 刷新前进后退按钮状态
        self.update_nav_buttons()

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            page_name = self.navigation_history[self.history_index]
            self.navigate_to(page_name, record_history=False)

    def go_forward(self):
        if self.history_index < len(self.navigation_history) - 1:
            self.history_index += 1
            page_name = self.navigation_history[self.history_index]
            self.navigate_to(page_name, record_history=False)

    def update_nav_buttons(self):
        # 前进后退按钮的启用状态
        self.btn_back.setEnabled(self.history_index > 0)
        self.btn_forward.setEnabled(self.history_index < len(self.navigation_history) - 1)

    def show_avatar_menu(self):
        # 弹出菜单在头像下方对齐
        pos = self.avatar.mapToGlobal(QPoint(0, self.avatar.height() + 4))
        self.avatar_menu.exec(pos)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NavigationWindow()
    window.show()
    sys.exit(app.exec())
