# -*- coding: utf-8 -*-
"""Profile page widget with mock data."""

import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PySide6.QtCore import Qt
from monkeyqt import MkAvatar
from monkeyqt.core.icons import MkPhosphorIcon

class ProfilePageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(20)

        # --- 用户信息头部卡片 ---
        user_card = QWidget()
        user_layout = QHBoxLayout(user_card)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(20)

        # 大头像
        avatar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_avatar.png")
        self.large_avatar = MkAvatar(
            text="落花",
            image_path=avatar_path if os.path.exists(avatar_path) else "",
            size=80,
            shape="circle",
        )
        user_layout.addWidget(self.large_avatar)

        # 用户详细信息
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(6)

        self.name_lbl = QLabel("落花不写码")
        self.name_lbl.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.meta_lbl = QLabel("42 个项目    1.2K Star    68 种主题")
        self.meta_lbl.setStyleSheet("font-size: 12px; color: #8e8e8e;")

        self.bio_lbl = QLabel("PySide6 / MonkeyQt 组件开发者 · 学习新思想，争做新青年")
        self.bio_lbl.setStyleSheet("font-size: 13px; color: #666666;")

        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)
        tags_layout.setContentsMargins(0, 0, 0, 0)

        self.tag_location = QLabel("📍 广西 · 南宁")
        self.tag_location.setStyleSheet(
            "color: #5b8ff9; background-color: rgba(91, 143, 249, 0.1);"
            "padding: 3px 10px; border-radius: 4px; font-size: 11px;"
        )
        self.tag_school = QLabel("🎓 吗喽大学")
        self.tag_school.setStyleSheet(
            "color: #61c454; background-color: rgba(97, 196, 84, 0.1);"
            "padding: 3px 10px; border-radius: 4px; font-size: 11px;"
        )
        tags_layout.addWidget(self.tag_location)
        tags_layout.addWidget(self.tag_school)
        tags_layout.addStretch()

        info_layout.addWidget(self.name_lbl)
        info_layout.addWidget(self.meta_lbl)
        info_layout.addWidget(self.bio_lbl)
        info_layout.addLayout(tags_layout)

        user_layout.addWidget(info_widget, stretch=1)
        layout.addWidget(user_card)

        # --- 统计数据卡片行 ---
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

        # --- 最近项目列表 ---
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
                QFrame:hover {{
                    border-color: {color};
                }}
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
