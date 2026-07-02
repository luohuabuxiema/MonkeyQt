# -*- coding: utf-8 -*-
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from monkeyqt.themes.engine import ThemeEngine


class MkTitleBarShell(QFrame):
    """
    MkTitleBarShell - 非无边框的内置标题栏外壳，用于在布局中模拟窗口边框。
    """
    closeClicked = Signal()
    minimizeClicked = Signal()
    maximizeClicked = Signal()

    def __init__(self, title="MonkeyQt", parent=None):
        super().__init__(parent)
        self.setObjectName("themedTitleBar")
        self.setFixedHeight(42)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 0, 8, 0)
        self.layout.setSpacing(8)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("themedTitleBarLabel")
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.btn_min = QPushButton("−")
        self.btn_max = QPushButton("□")
        self.btn_close = QPushButton("×")
        for btn in [self.btn_min, self.btn_max, self.btn_close]:
            btn.setFixedSize(28, 28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.layout.addWidget(btn)
        self.btn_min.clicked.connect(self.minimizeClicked)
        self.btn_max.clicked.connect(self.maximizeClicked)
        self.btn_close.clicked.connect(self.closeClicked)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        hover = t.get("--surface-muted", "#F1F5F9")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        self.setStyleSheet(f"""
            QFrame#themedTitleBar {{
                background: {surface};
                border-bottom: 1px solid {border};
                border-top-left-radius: {radius};
                border-top-right-radius: {radius};
            }}
            QLabel#themedTitleBarLabel {{
                background: transparent;
                color: {fg};
                font-size: 13px;
                font-weight: 800;
            }}
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 5px;
                color: {fg};
                font-size: 14px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background: {hover};
            }}
        """)


class MkWindowShell(QFrame):
    """
    MkWindowShell - 嵌入式模拟窗口外壳容器，完美支持 68 种主题切换。
    """
    def __init__(self, title="MonkeyQt Window", parent=None):
        super().__init__(parent)
        self.setObjectName("themedWindowShell")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.titlebar = MkTitleBarShell(title)
        self.content = QWidget()
        self.content.setObjectName("themedWindowContent")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(14, 14, 14, 14)
        self.layout.addWidget(self.titlebar)
        self.layout.addWidget(self.content, 1)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "6px")
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        self.setStyleSheet(f"""
            QFrame#themedWindowShell {{
                background: {surface};
                border: {border_rule};
                border-radius: {radius};
            }}
            QWidget#themedWindowContent {{
                background: transparent;
            }}
        """)
        self.titlebar.set_theme_style()
