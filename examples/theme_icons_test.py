# -*- coding: utf-8 -*-
"""
@File    : theme_icons_test.py
@Desc    : Interactive test for MonkeyQt Icons dynamic theme adaptation (Light vs Dark Mode)
"""

import sys
import pathlib

# Ensure parent directory is in sys.path
# ROOT = pathlib.Path(__file__).parent.parent
# sys.path.insert(0, str(ROOT / "monkeyqt-icons"))
# sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

from monkeyqt import use_theme, MkWindow, MkButton, MkSwitch
from monkeyqt_icons import (
    PhHouse, PhGear, PhHeart, PhUser, PhBell, PhLightning,
    PhPlanet, PhSparkle, PhCheckCircle, PhXCircle, PhIconWidget, Ph
)


class ThemeIconTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MonkeyQt Icons - 主题自适应测试")
        self.resize(750, 520)

        self.is_dark_mode = False

        # Central Widget & Main Layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 1. Header Bar with Theme Switcher
        header_layout = QHBoxLayout()
        title_label = QLabel("🎨 图标主题自适应测试 (Theme Adaptation Test)")
        title_font = QFont("Microsoft YaHei", 14, QFont.Weight.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.theme_btn = QPushButton("🌙 切换到暗黑模式")
        self.theme_btn.setFixedHeight(36)
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)

        main_layout.addLayout(header_layout)

        # 2. Status Label
        self.status_label = QLabel("当前主题: 默认浅色模式 (Default Light)")
        self.status_label.setStyleSheet("color: #64748B; font-size: 13px;")
        main_layout.addWidget(self.status_label)

        # 3. Card 1: QIcon/QPixmap in Qt PushButtons (自动自适应深浅色)
        card1 = QFrame()
        card1.setProperty("mkPanel", "true")
        card1_layout = QVBoxLayout(card1)
        card1_layout.setContentsMargins(16, 16, 16, 16)
        card1_layout.setSpacing(12)

        card1_title = QLabel("1. 带有 QIcon 的按钮 (默认未指定颜色，自动随主题深浅色切换)")
        card1_title.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        card1_layout.addWidget(card1_title)

        btn_grid = QHBoxLayout()
        btn_grid.setSpacing(12)

        # Button 1: PhHouse (MkButton with icon parameter in init)
        self.btn_home = MkButton(" 首页", icon=PhHouse.regular(size=20))
        btn_grid.addWidget(self.btn_home)

        # Button 2: PhGear
        self.btn_setting = MkButton(" 设置", icon=PhGear.bold(size=20))
        btn_grid.addWidget(self.btn_setting)

        # Button 3: PhBell (Duotone with primary token)
        self.btn_bell = MkButton(" 消息通知", icon=PhBell.duotone(color="primary", secondary_color="muted", size=20))
        btn_grid.addWidget(self.btn_bell)

        # Button 4: Fixed Custom Red (不随主题变化的固定颜色)
        self.btn_fixed = MkButton(" 固定红色图标", icon=PhHeart.fill(color="#ef4444", size=20))
        btn_grid.addWidget(self.btn_fixed)

        card1_layout.addLayout(btn_grid)
        main_layout.addWidget(card1)

        # 4. Card 2: Standalone PhIconWidget (实时监听 themeChanged 广播)
        card2 = QFrame()
        card2.setProperty("mkPanel", "true")
        card2_layout = QVBoxLayout(card2)
        card2_layout.setContentsMargins(16, 16, 16, 16)
        card2_layout.setSpacing(12)

        card2_title = QLabel("2. 独立 PhIconWidget 动态悬停控件 (无感广播重新绘制)")
        card2_title.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        card2_layout.addWidget(card2_title)

        widget_box = QHBoxLayout()
        widget_box.setSpacing(20)

        # Create PhIconWidgets
        self.w_user = PhIconWidget(icon="user", size=32, hover_color="#3b82f6")
        self.w_heart = PhIconWidget(icon="heart", weight="duotone", size=32, color="primary", hover_color="#ef4444")
        self.w_sparkle = PhIconWidget(icon="sparkle", weight="fill", size=32, hover_color="#eab308")
        self.w_check = PhIconWidget(icon="check-circle", weight="bold", size=32, color="primary")

        widget_box.addWidget(self.w_user)
        widget_box.addWidget(self.w_heart)
        widget_box.addWidget(self.w_sparkle)
        widget_box.addWidget(self.w_check)
        widget_box.addStretch()

        card2_layout.addLayout(widget_box)
        main_layout.addWidget(card2)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        theme_name = "HUD 科幻界面" if self.is_dark_mode else "新拟物化"

        # Apply global MonkeyQt theme - MkButton and PhIconWidget auto-update!
        use_theme(theme_name)

        # Update UI state text
        if self.is_dark_mode:
            self.theme_btn.setText("☀️ 切换到亮色模式")
            self.status_label.setText("当前主题: 暗黑模式 (Dark Mode / OLED) — MkButton 图标全自动重绘为亮白色/高亮蓝")
        else:
            self.theme_btn.setText("🌙 切换到暗黑模式")
            self.status_label.setText("当前主题: 默认浅色模式 (Default Light) — MkButton 图标全自动重绘为深色前景色")


def main():
    app = QApplication(sys.argv)
    
    # Initialize default theme
    use_theme("粗野主义")

    window = ThemeIconTestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
