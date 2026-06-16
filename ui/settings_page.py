# -*- coding: utf-8 -*-
"""Settings page widget."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from monkeyqt import MkSwitch, MkSlider

class SettingsPageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
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
            QLabel {
                font-size: 13px;
                border: none;
                background: transparent;
            }
        """)

        frame_layout = QVBoxLayout(settings_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(24)

        # 设置选项
        opt1_layout = QHBoxLayout()
        opt1_lbl = QLabel("自动保存检测结果")
        self.switch_save_results = MkSwitch(checked=True)
        opt1_layout.addWidget(opt1_lbl)
        opt1_layout.addStretch()
        opt1_layout.addWidget(self.switch_save_results)
        frame_layout.addLayout(opt1_layout)

        opt2_layout = QHBoxLayout()
        opt2_lbl = QLabel("默认置信度阈值")
        self.slider_conf = MkSlider(Qt.Horizontal)
        self.slider_conf.setRange(0, 100)
        self.slider_conf.setValue(25)
        self.slider_conf.setFixedWidth(150)
        opt2_layout.addWidget(opt2_lbl)
        opt2_layout.addStretch()
        opt2_layout.addWidget(self.slider_conf)
        frame_layout.addLayout(opt2_layout)

        opt3_layout = QHBoxLayout()
        opt3_lbl = QLabel("深色模式")
        self.switch_dark_mode = MkSwitch(checked=False)
        opt3_layout.addWidget(opt3_lbl)
        opt3_layout.addStretch()
        opt3_layout.addWidget(self.switch_dark_mode)
        frame_layout.addLayout(opt3_layout)

        opt4_layout = QHBoxLayout()
        opt4_lbl = QLabel("界面动画效果")
        self.switch_animation = MkSwitch(checked=True)
        opt4_layout.addWidget(opt4_lbl)
        opt4_layout.addStretch()
        opt4_layout.addWidget(self.switch_animation)
        frame_layout.addLayout(opt4_layout)

        layout.addWidget(settings_frame)

        desc = QLabel("说明：以上选项将在下次启动时生效。")
        desc.setStyleSheet("color: #999999; font-size: 12px; font-style: italic;")
        layout.addWidget(desc)
        layout.addStretch()
