"""
MonkeyQt Icons Comprehensive Demo
Demonstrates direct class imports, chainable method calls, 6 styles, duotone colors, and PhIconWidget.
"""

import sys
import pathlib

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QGridLayout, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor

from monkeyqt_icons import (
    Ph, PhHouse, PhGear, PhHeart, PhUser, PhBell, PhMagnifyingGlass,
    PhLightning, PhPlanet, PhSparkle, PhCheckCircle, PhXCircle, PhIconWidget
)


class IconsDemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MonkeyQt Icons (Phosphor v2.1.1) Demo")
        self.resize(960, 680)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title Layout with PhSparkle icon component
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        title_icon = PhSparkle.widget(size=28, color="#2563eb", weight="fill")
        title_label = QLabel("MonkeyQt Icons 演示 (1:1 复刻 Phosphor 图标)")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e293b;")
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Section 1: Front-end style direct imports & Chainable methods
        sec1_layout = QHBoxLayout()
        sec1_layout.setSpacing(8)
        sec1_icon = PhLightning.widget(size=20, color="#4f46e5", weight="fill")
        sec1_title = QLabel("1. 前端风格直导图标类 & 链式方法调用演示:")
        sec1_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #334155;")
        sec1_layout.addWidget(sec1_icon)
        sec1_layout.addWidget(sec1_title)
        sec1_layout.addStretch()
        layout.addLayout(sec1_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # Buttons with icons created via chainable static methods
        b1 = QPushButton("  首页 (Duotone 双色)")
        b1.setIcon(PhHouse.duotone(color="#2563eb", secondary_color="#93c5fd", size=24))
        b1.setIconSize(QSize(24, 24))

        b2 = QPushButton("  设置 (Fill 填充)")
        b2.setIcon(PhGear.fill(color="#dc2626", size=24))
        b2.setIconSize(QSize(24, 24))

        b3 = QPushButton("  收藏 (Regular 常规)")
        b3.setIcon(PhHeart.regular(color="#db2777", size=24))
        b3.setIconSize(QSize(24, 24))

        b4 = QPushButton("  用户 (Bold 粗体)")
        b4.setIcon(PhUser.bold(color="#059669", size=24))
        b4.setIconSize(QSize(24, 24))

        b5 = QPushButton("  通知 (Light 细线)")
        b5.setIcon(PhBell.light(color="#d97706", size=24))
        b5.setIconSize(QSize(24, 24))

        for b in [b1, b2, b3, b4, b5]:
            b.setStyleSheet("padding: 8px 16px; font-size: 13px; border-radius: 6px; background: #f8fafc; border: 1px solid #cbd5e1;")
            btn_layout.addWidget(b)

        layout.addLayout(btn_layout)

        # Section 2: 6 Styles Comparison
        sec2_layout = QHBoxLayout()
        sec2_layout.setSpacing(8)
        sec2_icon = PhPlanet.widget(size=20, color="#4f46e5", weight="fill")
        sec2_title = QLabel("2. 同一图标的 6 种外观风格对比 (PhPlanet):")
        sec2_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #334155;")
        sec2_layout.addWidget(sec2_icon)
        sec2_layout.addWidget(sec2_title)
        sec2_layout.addStretch()
        layout.addLayout(sec2_layout)

        styles_layout = QHBoxLayout()
        styles = [
            ("Regular", PhPlanet.regular(color="#4f46e5", size=32)),
            ("Bold", PhPlanet.bold(color="#4f46e5", size=32)),
            ("Fill", PhPlanet.fill(color="#4f46e5", size=32)),
            ("Light", PhPlanet.light(color="#4f46e5", size=32)),
            ("Thin", PhPlanet.thin(color="#4f46e5", size=32)),
            ("Duotone", PhPlanet.duotone(color="#4f46e5", secondary_color="#c7d2fe", size=32)),
        ]
        for style_name, icon in styles:
            card = QFrame()
            card.setStyleSheet("background: #f1f5f9; border-radius: 8px; padding: 10px;")
            c_layout = QVBoxLayout(card)
            c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_icon = QLabel()
            lbl_icon.setPixmap(icon.pixmap(32, 32))
            lbl_text = QLabel(style_name)
            lbl_text.setStyleSheet("font-size: 12px; color: #475569; font-weight: bold;")
            c_layout.addWidget(lbl_icon, alignment=Qt.AlignmentFlag.AlignCenter)
            c_layout.addWidget(lbl_text, alignment=Qt.AlignmentFlag.AlignCenter)
            styles_layout.addWidget(card)

        layout.addLayout(styles_layout)

        # Section 3: Interactive Search Grid
        sec3_layout = QHBoxLayout()
        sec3_layout.setSpacing(8)
        sec3_icon = PhMagnifyingGlass.widget(size=20, color="#0284c7", weight="bold")
        sec3_title = QLabel("3. 动态搜索 & 交互式 Widget 控件库 (1,512 图标即时检索):")
        sec3_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #334155;")
        sec3_layout.addWidget(sec3_icon)
        sec3_layout.addWidget(sec3_title)
        sec3_layout.addStretch()
        layout.addLayout(sec3_layout)

        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        # Add PhMagnifyingGlass icon directly inside QLineEdit leading position
        search_input.addAction(
            PhMagnifyingGlass.regular(color="#64748b", size=18),
            QLineEdit.ActionPosition.LeadingPosition
        )
        search_input.setPlaceholderText("输入关键词搜索（例如：user, heart, arrow, mail, chat...）")
        search_input.setStyleSheet("padding: 8px 12px 8px 30px; font-size: 13px; border-radius: 6px; border: 1px solid #94a3b8;")
        search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(search_input)
        layout.addLayout(search_layout)

        # Scroll area for icons grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #e2e8f0; border-radius: 8px; background: white; }")

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(12)
        scroll.setWidget(self.grid_widget)

        layout.addWidget(scroll)

        # Initial populate
        self.populate_grid("star")

    def on_search(self, text):
        query = text.strip() if text.strip() else "star"
        self.populate_grid(query)

    def populate_grid(self, query):
        # Clear existing
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        results = Ph.search(query)[:36] # Show first 36
        cols = 6

        for idx, item in enumerate(results):
            name = item["name"]
            pascal = item["pascal_name"]

            card = QFrame()
            card.setStyleSheet("QFrame { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; } QFrame:hover { background: #eff6ff; border-color: #3b82f6; }")
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(8, 8, 8, 8)
            c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Use PhIconWidget
            icon_w = PhIconWidget(
                icon=name,
                size=28,
                color="#1e293b",
                weight="duotone",
                secondary_color="#60a5fa",
                hover_color="#2563eb"
            )
            lbl_name = QLabel(pascal)
            lbl_name.setStyleSheet("font-size: 10px; color: #64748b;")
            lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

            c_layout.addWidget(icon_w, alignment=Qt.AlignmentFlag.AlignCenter)
            c_layout.addWidget(lbl_name, alignment=Qt.AlignmentFlag.AlignCenter)

            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(card, row, col)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IconsDemoWindow()
    window.show()
    sys.exit(app.exec())
