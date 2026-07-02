# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFormLayout, QLabel, QVBoxLayout, QWidget, QSizePolicy

from monkeyqt.themes.engine import ThemeEngine

class MkForm(QWidget):
    """
    MkForm 组件 - 提供结构化的表单布局支持，完美自适应 68 种主题风格的标签文本与标题排版。
    """
    def __init__(self, label_width=100, label_position="right", parent=None, title="", description=""):
        # 兼容 ThemedForm("title", "description", parent) 构造传参
        if isinstance(label_width, str):
            title = label_width
            description = label_position if isinstance(label_position, str) else ""
            parent = parent
            label_width = 100
            label_position = "right"

        super().__init__(parent)
        self._label_width = label_width
        self._label_position = label_position  # right, left, top
        self._title = title
        self._description = description

        self._setup_ui()
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def _setup_ui(self):
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # 主布局：纵向结构，容纳标题与表单内容
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        # 标题与描述
        self.title_label = QLabel(self._title)
        self.title_label.setVisible(bool(self._title))
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.main_layout.addWidget(self.title_label)

        self.description_label = QLabel(self._description)
        self.description_label.setWordWrap(True)
        self.description_label.setVisible(bool(self._description))
        self.main_layout.addWidget(self.description_label)

        # 表单具体内容容器
        self.form_container = QWidget()
        self.form_container.setStyleSheet("background: transparent; border: none;")
        
        if self._label_position in ["right", "left"]:
            self.form_layout = QFormLayout(self.form_container)
            self.form_layout.setContentsMargins(0, 0, 0, 0)
            self.form_layout.setSpacing(20)
            
            if self._label_position == "right":
                self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            else:
                self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                
            self.form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        else:
            # Top layout
            self.form_layout = QVBoxLayout(self.form_container)
            self.form_layout.setContentsMargins(0, 0, 0, 0)
            self.form_layout.setSpacing(12)

        self.main_layout.addWidget(self.form_container)

    def add_item(self, label_text, widget):
        label = QLabel(label_text)
        label.setObjectName("form_item_label")
        
        if self._label_position in ["right", "left"]:
            label.setFixedWidth(self._label_width)
            self.form_layout.addRow(label, widget)
        else:
            # Top alignment: label above widget
            item_layout = QVBoxLayout()
            item_layout.setSpacing(4)
            item_layout.addWidget(label)
            item_layout.addWidget(widget)
            self.form_layout.addLayout(item_layout)
        self.set_theme_style()

    def add_row(self, label: str, field: QWidget):
        # 兼容 ThemedForm.add_row 接口
        self.add_item(label, field)

    def set_label_width(self, width):
        self._label_width = width

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        family = "Consolas" if t.is_pixel() else '"Segoe UI", "Microsoft YaHei"'
        
        self.setStyleSheet(f"""
            MkForm, QLabel {{
                background: transparent;
                color: {fg};
                font-family: {family};
            }}
            QLabel#form_item_label {{
                font-size: 13px;
                font-weight: 600;
            }}
        """)
        self.title_label.setStyleSheet(f"background: transparent; color: {fg}; font-weight: 800; font-size: 15px;")
        self.description_label.setStyleSheet(f"background: transparent; color: {muted}; font-size: 12px;")
