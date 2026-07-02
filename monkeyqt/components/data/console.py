# -*- coding: utf-8 -*-
"""
MonkeyQt Console Component — 控制台/打印日志输出组件
支持多级别过滤、自动滚动、一键清除、主题适配。
"""

import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor, QIcon
from monkeyqt.core.icons import MkPhosphorIcon


class MkConsole(QWidget):
    """
    一个美观且功能丰富的控制台日志输出组件。
    支持 68 种主题适配、自动滚动、行数限制、一键清空和多级日志高亮。
    """

    def __init__(self, title="控制台日志 / Console Logs", parent=None):
        super().__init__(parent)
        self._max_lines = 1000
        self._autoscroll = True
        self._show_timestamp = True
        
        # 统计计数器
        self._counts = {
            "info": 0,
            "success": 0,
            "warning": 0,
            "error": 0,
            "debug": 0
        }

        self._init_ui(title)
        from monkeyqt.themes.engine import ThemeEngine
        ThemeEngine.instance().themeChanged.connect(self.apply_theme_colors)
        self.apply_theme_colors()

    def _init_ui(self, title):
        # 主布局：上下结构
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ── 1. 头部区域 ──
        self.header_widget = QWidget()
        self.header_widget.setObjectName("ConsoleHeader")
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(10, 6, 10, 6)
        self.header_layout.setSpacing(8)

        # 标题与图标
        self.title_icon = QLabel()
        self.title_icon.setPixmap(MkPhosphorIcon.get_pixmap("terminal-window", "#64748B", 16))
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))

        self.header_layout.addWidget(self.title_icon)
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addSpacing(10)

        # 计数指示面板
        self.badge_widget = QWidget()
        self.badge_layout = QHBoxLayout(self.badge_widget)
        self.badge_layout.setContentsMargins(0, 0, 0, 0)
        self.badge_layout.setSpacing(10)

        self.lbl_info_count = QLabel("Info: 0")
        self.lbl_success_count = QLabel("Success: 0")
        self.lbl_warn_count = QLabel("Warn: 0")
        self.lbl_err_count = QLabel("Error: 0")

        for lbl in [self.lbl_info_count, self.lbl_success_count, self.lbl_warn_count, self.lbl_err_count]:
            lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
            self.badge_layout.addWidget(lbl)

        self.header_layout.addWidget(self.badge_widget)
        self.header_layout.addStretch()

        # 清除按钮
        from monkeyqt.components.basic.button import MkButton
        self.btn_clear = MkButton("清除", type="default", size="small")
        self.btn_clear.clicked.connect(self.clear)
        self.header_layout.addWidget(self.btn_clear)

        self.main_layout.addWidget(self.header_widget)

        # ── 2. 日志文本区域 ──
        self.text_edit = QTextEdit()
        self.text_edit.setProperty("mk_theme_disabled", True)
        self.text_edit.setReadOnly(True)
        self.text_edit.setUndoRedoEnabled(False)
        self.text_edit.setFont(QFont("Consolas", 9))
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) # 允许左右横向滚动

        self.main_layout.addWidget(self.text_edit, stretch=1)

        # 自适应大小策略
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def apply_theme_colors(self):
        """同步全局 MonkeyQt 主题颜色"""
        t = None
        try:
            from monkeyqt.themes.engine import ThemeEngine
            t = ThemeEngine
        except Exception:
            pass

        bg = t.get("--surface", "#1E1E2E") if t else "#1E1E2E"
        fg = t.get("--fg", "#CDD6F4") if t else "#CDD6F4"
        border = t.get("--border", "#313244") if t else "#313244"
        header_bg = t.get("--surface-muted", "#181825") if t else "#181825"
        text_muted = t.get("--text-muted", "#6C7086") if t else "#6C7086"
        primary = t.get("--primary", "#89B4FA") if t else "#89B4FA"
        accent = t.get("--accent", "#A6E3A1") if t else "#A6E3A1"

        # 颜色映射字典，供 HTML 使用
        self._level_colors = {
            "info": primary,
            "success": accent,
            "warning": "#F9E2AF",  # 黄色
            "error": "#F38BA8",    # 红色
            "debug": text_muted
        }

        # 刷新背景与文字
        self.title_icon.setStyleSheet("background: transparent;")
        self.title_label.setStyleSheet(f"color: {fg}; background: transparent;")
        self.badge_widget.setStyleSheet("background: transparent;")

        # 刷新计数指示面板文字颜色与背景
        self.lbl_info_count.setStyleSheet(f"color: {self._level_colors['info']}; background: transparent;")
        self.lbl_success_count.setStyleSheet(f"color: {self._level_colors['success']}; background: transparent;")
        self.lbl_warn_count.setStyleSheet(f"color: {self._level_colors['warning']}; background: transparent;")
        self.lbl_err_count.setStyleSheet(f"color: {self._level_colors['error']}; background: transparent;")

        # 应用 QSS 样式表
        self.setStyleSheet(f"""
            QWidget#ConsoleHeader {{
                background-color: {header_bg};
                border-bottom: 1px solid {border};
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                border-top: none;
                border-bottom-left-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
        """)
        
        # 刷新清除按钮样式与图标
        btn_press_bg = t._darken_hex(primary, 0.1) if (t and hasattr(t, "_darken_hex") and primary.startswith("#")) else "#E0E7FF"
        self.btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: {header_bg};
                color: {fg};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {primary};
                color: #FFFFFF;
                border-color: {primary};
            }}
            QPushButton:pressed {{
                background-color: {btn_press_bg};
                color: #FFFFFF;
                border-color: {btn_press_bg};
            }}
        """)
        
        self.title_icon.setPixmap(MkPhosphorIcon.get_pixmap("terminal-window", text_muted, 16))
        self.btn_clear.setIcon(MkPhosphorIcon.get_icon("trash", fg, hover_color="#FFFFFF", size=14))
        self.btn_clear.update()

    def log(self, text: str, level: str = "info", timestamp: bool = True):
        """
        核心日志打印接口。
        
        Args:
            text: 日志内容。
            level: 日志级别 ("info", "success", "warning", "error", "debug")。
            timestamp: 是否打印时间戳。
        """
        lvl = str(level).lower()
        if lvl not in self._level_colors:
            lvl = "info"

        # 更新计数
        self._counts[lvl] += 1
        self._update_badges()

        # 时间戳
        time_part = ""
        if timestamp and self._show_timestamp:
            now_str = datetime.datetime.now().strftime("%H:%M:%S")
            time_part = f'<span style="color: {self._level_colors["debug"]};">[{now_str}]</span> '

        # 级别标签
        level_tag = f'<b style="color: {self._level_colors[lvl]};">[{lvl.upper()}]</b> '

        # 最终 HTML 构建
        html_msg = f'{time_part}{level_tag}<span style="font-family: Consolas;">{text}</span>'

        # 写入控制台
        self.text_edit.append(html_msg)

        # 行数限制裁剪
        self._trim_excess_lines()

        # 自动滚动到底部
        if self._autoscroll:
            self.text_edit.moveCursor(QTextCursor.MoveOperation.End)

    # 快捷打印接口
    def info(self, text: str):
        self.log(text, "info")

    def success(self, text: str):
        self.log(text, "success")

    def warn(self, text: str):
        self.log(text, "warning")

    def error(self, text: str):
        self.log(text, "error")

    def debug(self, text: str):
        self.log(text, "debug")

    def clear(self):
        """清空控制台所有日志及计数器"""
        self.text_edit.clear()
        for k in self._counts:
            self._counts[k] = 0
        self._update_badges()

    def set_max_lines(self, limit: int):
        """设置最大日志保留行数限制，防止内存泄漏"""
        if limit > 0:
            self._max_lines = limit
            self._trim_excess_lines()

    def set_autoscroll(self, enabled: bool):
        """设置是否开启自动滚动到底部"""
        self._autoscroll = bool(enabled)

    def set_show_timestamp(self, show: bool):
        """设置是否显示时间戳"""
        self._show_timestamp = bool(show)

    def _update_badges(self):
        self.lbl_info_count.setText(f"Info: {self._counts['info']}")
        self.lbl_success_count.setText(f"Success: {self._counts['success']}")
        self.lbl_warn_count.setText(f"Warn: {self._counts['warning']}")
        self.lbl_err_count.setText(f"Error: {self._counts['error']}")

    def _trim_excess_lines(self):
        doc = self.text_edit.document()
        while doc.blockCount() > self._max_lines:
            cursor = QTextCursor(doc.begin())
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar() # 删除多余的空行回车符

    def _update_style(self):
        """提供给全局适配器的主动重绘槽"""
        self.apply_theme_colors()

    def set_theme_style(self, style_name: str = None):
        """标准主题组件的样式重绘槽"""
        self.apply_theme_colors()
