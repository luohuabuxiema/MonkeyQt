# -*- coding: utf-8 -*-
"""
MonkeyQt Console Component — 现代化前端/终端风格控制台日志组件
采用现代 Web/开发者终端设计理念（如 Vercel Logs, GitHub Actions, VS Code Terminal）：
- macOS 窗口控制红黄绿三色圆点与终端标题栏；
- 可交互式日志级别过滤徽章（All / Info / Success / Warn / Error）；
- 实时日志关键字搜索过滤；
- 自动换行、锁底自动滚动、一键复制、日志文件导出；
- 纯黑极客终端模式 (Dark Terminal) 与 68 款全局主题自适应模式 (Adaptive)；
- 彻底解决内边距截断、重影与滚动条伪影问题。
"""

import sys
import os
import datetime
import html
from typing import Optional, List, Dict, Any, Union

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QLineEdit, QSizePolicy, 
    QToolButton, QFrame, QFileDialog, QApplication
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QTextCursor, QIcon, QColor, QClipboard

from monkeyqt.core.icons import MkPhosphorIcon
from monkeyqt.components.layout.widget import MkQWidget
from monkeyqt.themes.engine import ThemeEngine


class _ConsoleFilterPill(QPushButton):
    """现代药丸状日志级别过滤徽章，支持交互点击筛选与动态计数。"""

    def __init__(self, level: str, label: str, color_scheme: Dict[str, str], parent=None):
        super().__init__(parent)
        self.level = level
        self.raw_label = label
        self.count = 0
        self.color_scheme = color_scheme
        self.is_selected = False
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(22)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._update_text_and_style()

    def set_count(self, count: int):
        self.count = count
        self._update_text_and_style()

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self._update_text_and_style()

    def update_colors(self, color_scheme: Dict[str, str]):
        self.color_scheme = color_scheme
        self._update_text_and_style()

    def _update_text_and_style(self):
        self.setText(f"{self.raw_label} {self.count}")
        cs = self.color_scheme
        fg = cs.get("fg", "#94A3B8")
        bg = cs.get("bg", "rgba(255, 255, 255, 0.05)")
        border = cs.get("border", "rgba(255, 255, 255, 0.1)")
        active_bg = cs.get("active_bg", "rgba(255, 255, 255, 0.2)")
        active_border = cs.get("active_border", fg)

        from monkeyqt.themes.style_utils import is_color, readable_text

        cur_bg = active_bg if self.is_selected else bg
        cur_border = active_border if self.is_selected else border
        
        if self.is_selected:
            cur_fg = readable_text(active_bg) if is_color(active_bg) else "#FFFFFF"
        else:
            cur_fg = fg

        hover_fg = readable_text(active_bg) if is_color(active_bg) else "#FFFFFF"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {cur_bg};
                color: {cur_fg};
                border: 1px solid {cur_border};
                border-radius: 11px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
                font-size: 11px;
                font-weight: {'700' if self.is_selected else '500'};
                padding: 0px 8px;
            }}
            QPushButton:hover {{
                background-color: {active_bg};
                border: 1px solid {active_border};
                color: {hover_fg};
            }}
        """)


class _ConsoleToolButton(QToolButton):
    """极简现代控制台快捷工具图标按钮。"""

    def __init__(self, icon_name: str, tooltip: str, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.setToolTip(tooltip)
        self.setFixedSize(26, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.is_active_toggle = False
        self.update_theme(is_dark=True)

    def update_theme(self, is_dark: bool):
        fg = "#A1A1AA" if is_dark else "#64748B"
        hover_bg = "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.06)"
        active_bg = "rgba(59, 130, 246, 0.25)" if is_dark else "rgba(59, 130, 246, 0.15)"
        active_fg = "#60A5FA" if is_dark else "#2563EB"
        
        cur_fg = active_fg if self.is_active_toggle else fg
        cur_bg = active_bg if self.is_active_toggle else "transparent"
        
        self.setIcon(MkPhosphorIcon.get_icon(self.icon_name, cur_fg, hover_color="#FFFFFF" if is_dark else "#0F172A", size=14))
        self.setStyleSheet(f"""
            QToolButton {{
                background-color: {cur_bg};
                border: none;
                border-radius: 5px;
                padding: 3px;
            }}
            QToolButton:hover {{
                background-color: {hover_bg};
            }}
            QToolButton:pressed {{
                background-color: {active_bg};
            }}
        """)


class MkConsole(MkQWidget):
    """
    现代化前端/终端风格控制台日志输出组件。
    支持 macOS 窗口顶栏、多级别交互过滤、关键字实时搜索、自动折行、一键复制、导出与 68 款主题自适应。
    """

    def __init__(
        self,
        title: str = "控制台日志 / Console Logs",
        terminal_mode: str = "adaptive",
        show_divider: bool = False,
        show_filters: bool = True,
        show_level_tags: bool = True,
        show_timestamp: bool = True,
        show_search: bool = True,
        show_tools: bool = True,
        show_header: bool = True,
        word_wrap: bool = True,
        autoscroll: bool = True,
        max_lines: int = 1000,
        clean_mode: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.title_text = title
        self.terminal_mode = terminal_mode  # "adaptive" (默认随全局 68 款主题自适应) 或 "dark" (固定暗黑终端)
        self.show_divider = show_divider    # 顶栏与日志区域之间的分割边框线，默认不显示（严丝合缝无边框线）

        if clean_mode:
            self.show_filters = False
            self.show_level_tags = False
            self.show_timestamp = False
        else:
            self.show_filters = show_filters          # 是否显示顶部日志级别过滤胶囊（全部/Info/Success/Warn/Error）
            self.show_level_tags = show_level_tags    # 是否在日志条目首部显示彩色级别微徽标（INFO/SUCCESS/WARN/ERROR）
            self.show_timestamp = show_timestamp      # 是否显示日志时间戳

        self.show_search = show_search              # 是否显示实时关键字过滤框
        self.show_tools = show_tools                # 是否显示右侧快捷工具按钮
        self.show_header = show_header              # 是否显示整个顶部控制栏

        self._max_lines = max_lines
        self._autoscroll = autoscroll
        self._word_wrap = word_wrap
        self._current_filter_level = "all"
        self._search_keyword = ""

        # 内部日志结构数据库
        self._logs: List[Dict[str, Any]] = []
        self._counts = {
            "all": 0,
            "info": 0,
            "success": 0,
            "warning": 0,
            "error": 0,
            "debug": 0
        }

        self._init_ui()
        self.apply_theme_colors()

    def on_theme_changed(self, theme_name: str = ""):
        """接收主题全局切换信号"""
        self.apply_theme_colors()

    def _update_style(self):
        self.apply_theme_colors()

    def set_theme_style(self, style_name: Optional[str] = None):
        self.apply_theme_colors()

    def _init_ui(self):
        self.setObjectName("MkConsole")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ── 1. 现代化顶部终端工具栏 ──
        self.header_frame = QFrame(self)
        self.header_frame.setObjectName("MkConsoleHeader")
        self.header_frame.setFixedHeight(42)
        self.header_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.header_frame.setFrameShadow(QFrame.Shadow.Plain)
        self.header_frame.setLineWidth(0)
        self.header_frame.setMidLineWidth(0)

        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(14, 0, 14, 0)
        header_layout.setSpacing(10)

        # 1.1 终端图标与标题
        self.title_icon = QLabel(self.header_frame)
        self.title_label = QLabel(self.title_text, self.header_frame)
        self.title_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))

        header_layout.addWidget(self.title_icon)
        header_layout.addWidget(self.title_label)
        header_layout.addSpacing(6)

        # 1.3 日志级别过滤胶囊容器 (All, Info, Success, Warn, Error)
        self.filter_container = QWidget(self.header_frame)
        self.filter_container.setObjectName("MkConsoleFilterContainer")
        filter_layout = QHBoxLayout(self.filter_container)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(6)

        self.filter_pills: Dict[str, _ConsoleFilterPill] = {}
        pill_defs = [
            ("all", "全部", {"fg": "#E2E8F0", "bg": "rgba(255,255,255,0.08)", "border": "rgba(255,255,255,0.15)", "active_bg": "#3B82F6", "active_border": "#3B82F6"}),
            ("info", "Info", {"fg": "#60A5FA", "bg": "rgba(59,130,246,0.12)", "border": "rgba(59,130,246,0.25)", "active_bg": "#2563EB", "active_border": "#3B82F6"}),
            ("success", "Success", {"fg": "#34D399", "bg": "rgba(16,185,129,0.12)", "border": "rgba(16,185,129,0.25)", "active_bg": "#059669", "active_border": "#10B981"}),
            ("warning", "Warn", {"fg": "#FBBF24", "bg": "rgba(245,158,11,0.12)", "border": "rgba(245,158,11,0.25)", "active_bg": "#D97706", "active_border": "#F59E0B"}),
            ("error", "Error", {"fg": "#F87171", "bg": "rgba(239,68,68,0.12)", "border": "rgba(239,68,68,0.25)", "active_bg": "#DC2626", "active_border": "#EF4444"}),
        ]
        for key, lbl, colors in pill_defs:
            pill = _ConsoleFilterPill(key, lbl, colors, self.filter_container)
            pill.clicked.connect(lambda checked=False, k=key: self.set_filter_level(k))
            self.filter_pills[key] = pill
            filter_layout.addWidget(pill)

        self.filter_pills["all"].set_selected(True)
        header_layout.addWidget(self.filter_container)
        header_layout.addStretch(1)

        # 1.4 实时关键字搜索框 (不使用表情符号)
        self.search_input = QLineEdit(self.header_frame)
        self.search_input.setPlaceholderText("搜索过滤日志...")
        self.search_input.setFixedWidth(130)
        self.search_input.setFixedHeight(26)
        self.search_input.textChanged.connect(self._on_search_changed)
        header_layout.addWidget(self.search_input)

        # 1.6 快捷操作工具按钮容器
        self.tools_container = QWidget(self.header_frame)
        self.tools_container.setObjectName("MkConsoleToolsContainer")
        tools_layout = QHBoxLayout(self.tools_container)
        tools_layout.setContentsMargins(0, 0, 0, 0)
        tools_layout.setSpacing(6)

        self.btn_autoscroll = _ConsoleToolButton("arrow-down-line", "自动滚动到底部 (开启/关闭)", self.tools_container)
        self.btn_autoscroll.is_active_toggle = self._autoscroll
        self.btn_autoscroll.clicked.connect(self._toggle_autoscroll)
        tools_layout.addWidget(self.btn_autoscroll)

        self.btn_wrap = _ConsoleToolButton("text-align-left", "自动折行 (开启/关闭)", self.tools_container)
        self.btn_wrap.is_active_toggle = self._word_wrap
        self.btn_wrap.clicked.connect(self._toggle_wrap)
        tools_layout.addWidget(self.btn_wrap)

        self.btn_copy = _ConsoleToolButton("copy", "复制全部过滤日志", self.tools_container)
        self.btn_copy.clicked.connect(self.copy_all)
        tools_layout.addWidget(self.btn_copy)

        self.btn_mode = _ConsoleToolButton("sparkle", "切换终端皮肤 (Dark / Adaptive)", self.tools_container)
        self.btn_mode.clicked.connect(self._toggle_terminal_mode)
        tools_layout.addWidget(self.btn_mode)

        self.btn_clear = _ConsoleToolButton("trash", "清空控制台", self.tools_container)
        self.btn_clear.clicked.connect(self.clear)
        tools_layout.addWidget(self.btn_clear)

        header_layout.addWidget(self.tools_container)

        self.main_layout.addWidget(self.header_frame)

        # 应用组件初始可见性设置
        self.filter_container.setVisible(self.show_filters)
        self.search_input.setVisible(self.show_search)
        self.tools_container.setVisible(self.show_tools)
        self.header_frame.setVisible(self.show_header)

        # ── 2. 现代化终端日志输出视口 ──
        self.text_edit = QTextEdit(self)
        self.text_edit.setObjectName("MkConsoleEditor")
        self.text_edit.setProperty("mk_theme_disabled", True)
        self.text_edit.setFrameShape(QFrame.Shape.NoFrame)
        self.text_edit.setFrameShadow(QFrame.Shadow.Plain)
        self.text_edit.setLineWidth(0)
        self.text_edit.setMidLineWidth(0)
        self.text_edit.setReadOnly(True)
        self.text_edit.setUndoRedoEnabled(False)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth if self._word_wrap else QTextEdit.LineWrapMode.NoWrap)
        self.text_edit.document().setDocumentMargin(14)

        # 现代等宽字体，保证排版整齐划一
        mono_font = QFont("Consolas", 10)
        mono_font.setStyleHint(QFont.StyleHint.Monospace)
        self.text_edit.setFont(mono_font)

        self.main_layout.addWidget(self.text_edit, stretch=1)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_terminal_mode(self, mode: str):
        """设置控制台皮肤模式: 'dark' (固定暗黑终端) 或 'adaptive' (随 68 款全局主题自适应)。"""
        if mode in ("dark", "adaptive"):
            self.terminal_mode = mode
            self.apply_theme_colors()

    def set_show_divider(self, show: bool):
        """设置是否显示顶栏与日志区域之间的横向分割边框线。"""
        self.show_divider = bool(show)
        self.apply_theme_colors()

    def set_show_filters(self, show: bool):
        """设置是否显示顶部日志级别过滤胶囊 (全部/Info/Success/Warn/Error)。"""
        self.show_filters = bool(show)
        if hasattr(self, "filter_container"):
            self.filter_container.setVisible(self.show_filters)

    def set_show_level_tags(self, show: bool):
        """设置是否在日志行首显示彩色级别微徽标 (INFO, SUCCESS, WARN, ERROR, DEBUG)。"""
        self.show_level_tags = bool(show)
        self._rebuild_display()

    def set_clean_mode(self, clean: bool = True):
        """
        一键切换至纯净终端/训练输出模式：
        - 隐藏顶部级别过滤胶囊；
        - 隐藏每行开头的彩色级别徽标；
        - 隐藏时间戳（只保留纯净的命令行输出文本）。
        """
        self.show_filters = not clean
        self.show_level_tags = not clean
        self.show_timestamp = not clean
        if hasattr(self, "filter_container"):
            self.filter_container.setVisible(self.show_filters)
        self._rebuild_display()

    def set_show_search(self, show: bool):
        """设置是否显示顶部关键字搜索过滤框。"""
        self.show_search = bool(show)
        if hasattr(self, "search_input"):
            self.search_input.setVisible(self.show_search)

    def set_show_tools(self, show: bool):
        """设置是否显示顶部右侧快捷工具按钮。"""
        self.show_tools = bool(show)
        if hasattr(self, "tools_container"):
            self.tools_container.setVisible(self.show_tools)

    def set_show_header(self, show: bool):
        """设置是否显示整个顶部工具栏。"""
        self.show_header = bool(show)
        if hasattr(self, "header_frame"):
            self.header_frame.setVisible(self.show_header)

    def write(self, text: str):
        """
        流式/纯净文本写入接口（方便直接输出 YOLO 训练日志、流式 subprocess 输出等）。
        自动按 raw 纯文本输出，不带任何级别微徽标与时间戳。
        """
        lines = str(text).splitlines()
        if not lines:
            if text == "\n":
                return
            self.log(str(text), level="raw", timestamp=False)
        else:
            for l in lines:
                self.log(l, level="raw", timestamp=False)

    def raw(self, text: str, timestamp: bool = False):
        """纯文本打印接口，不带有任何级别微徽标。"""
        self.log(text, level="raw", timestamp=timestamp)

    def print(self, *args, sep: str = " ", end: str = "", timestamp: bool = False):
        """模拟 Python 原生 print 打印接口。"""
        text = sep.join(str(a) for a in args) + end
        self.raw(text, timestamp=timestamp)

    def _toggle_terminal_mode(self):
        self.terminal_mode = "adaptive" if self.terminal_mode == "dark" else "dark"
        self.apply_theme_colors()

    def apply_theme_colors(self):
        """同步全局 MonkeyQt 主题颜色，并针对不同风格应用沉浸式配色"""
        t = ThemeEngine
        is_dark = True if self.terminal_mode == "dark" else t.is_dark()
        is_brutal = t.is_brutal() and self.terminal_mode != "dark"
        is_glow = t.is_glow()

        # 读取当前主题 Design Tokens
        surface = t.get("--surface", "#18181B" if is_dark else "#FFFFFF")
        surface_muted = t.get("--surface-muted", "#27272A" if is_dark else "#F8FAFC")
        border_col = t.get("--border", "#3F3F46" if is_dark else "#E2E8F0")
        fg_main = t.get("--fg", "#F4F4F5" if is_dark else "#0F172A")
        fg_muted = t.get("--text-muted", "#71717A" if is_dark else "#94A3B8")
        primary = t.get("--primary", "#3B82F6")

        radius_str = str(t.get("--radius", "12px")).replace("px", "").strip()
        border_radius = 0 if is_brutal else (int(radius_str) if radius_str.isdigit() else 12)
        border_radius = max(0, min(border_radius, 16))

        bw_str = str(t.get("--border-width", "1px")).replace("px", "").strip()
        border_width = 2 if is_brutal else (int(bw_str) if bw_str.isdigit() else 1)

        if self.terminal_mode == "dark":
            # 纯黑极客终端配色 (Deep Obsidian / Graphite)
            card_bg = "#0B0F17"
            header_bg = "#0F172A"
            border = "#1E293B" if not is_glow else "rgba(59, 130, 246, 0.4)"
            editor_bg = "#0B0F17"
            fg_main = "#F1F5F9"
            fg_muted = "#64748B"
            search_bg = "#1E293B"
            search_border = "#334155"
            status_bg = "rgba(16, 185, 129, 0.15)"
            status_fg = "#34D399"
            scroll_thumb = "rgba(255, 255, 255, 0.16)"
            scroll_hover = "rgba(255, 255, 255, 0.3)"
        elif is_brutal:
            # 新野兽派模式
            card_bg = surface
            header_bg = surface_muted if surface_muted != surface else "#FEF08A"
            border = border_col
            editor_bg = surface
            search_bg = surface
            search_border = "#000000"
            status_bg = "#BBF7D0"
            status_fg = "#000000"
            scroll_thumb = "#000000"
            scroll_hover = "#4B5563"
        elif is_dark:
            # 深色主题自适应 (Dark Mode, OLED, Dracula, Nord, Cyberpunk...)
            card_bg = surface
            header_bg = surface_muted
            border = border_col if not is_glow else primary
            editor_bg = surface
            search_bg = surface_muted
            search_border = border_col
            status_bg = "rgba(16, 185, 129, 0.15)"
            status_fg = "#34D399"
            scroll_thumb = "rgba(255, 255, 255, 0.16)"
            scroll_hover = "rgba(255, 255, 255, 0.3)"
        else:
            # 现代清新浅色自适应 (Elegant Light, Minimalism, Paper...)
            card_bg = surface
            header_bg = surface_muted
            border = border_col
            editor_bg = surface
            search_bg = "#FFFFFF" if surface != "#FFFFFF" else "#F1F5F9"
            search_border = border_col
            status_bg = "rgba(16, 185, 129, 0.12)"
            status_fg = "#059669"
            scroll_thumb = "rgba(0, 0, 0, 0.12)"
            scroll_hover = "rgba(0, 0, 0, 0.25)"

        top_rad = max(0, border_radius - 1)

        self.setStyleSheet(f"""
            MkConsole {{
                background-color: {card_bg};
                border: {border_width}px solid {border};
                border-radius: {border_radius}px;
            }}
        """)

        divider_css = f"border-bottom: {border_width}px solid {border};" if self.show_divider else "border-bottom: none;"

        self.header_frame.setStyleSheet(f"""
            QFrame#MkConsoleHeader {{
                background-color: {header_bg};
                border: none;
                border-top: none;
                border-left: none;
                border-right: none;
                border-top-left-radius: {top_rad}px;
                border-top-right-radius: {top_rad}px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                {divider_css}
            }}
        """)

        self.title_label.setStyleSheet(f"color: {fg_main}; background: transparent; border: none;")
        self.title_icon.setPixmap(MkPhosphorIcon.get_pixmap("terminal-window", fg_muted, 16))

        # 动态同步过滤徽章主题样式
        pill_defs = {
            "all": {"fg": fg_main, "bg": "rgba(255,255,255,0.08)" if is_dark else "rgba(0,0,0,0.05)", "border": border, "active_bg": primary, "active_border": primary},
            "info": {"fg": "#60A5FA" if is_dark else "#2563EB", "bg": "rgba(59,130,246,0.12)", "border": "rgba(59,130,246,0.25)", "active_bg": "#2563EB", "active_border": "#3B82F6"},
            "success": {"fg": "#34D399" if is_dark else "#059669", "bg": "rgba(16,185,129,0.12)", "border": "rgba(16,185,129,0.25)", "active_bg": "#059669", "active_border": "#10B981"},
            "warning": {"fg": "#FBBF24" if is_dark else "#D97706", "bg": "rgba(245,158,11,0.12)", "border": "rgba(245,158,11,0.25)", "active_bg": "#D97706", "active_border": "#F59E0B"},
            "error": {"fg": "#F87171" if is_dark else "#DC2626", "bg": "rgba(239,68,68,0.12)", "border": "rgba(239,68,68,0.25)", "active_bg": "#DC2626", "active_border": "#EF4444"},
        }
        for k, p in self.filter_pills.items():
            if k in pill_defs:
                p.update_colors(pill_defs[k])

        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {search_bg};
                color: {fg_main};
                border: 1px solid {search_border};
                border-radius: 13px;
                padding: 2px 10px;
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border: 1px solid #3B82F6;
            }}
        """)

        # 定制现代化无缝超细滚动条 (消除 Windows 灰底与溢出伪影)
        self.text_edit.setStyleSheet(f"""
            QTextEdit#MkConsoleEditor {{
                background-color: {editor_bg};
                color: {fg_main};
                border: none;
                border-top: none;
                border-bottom: none;
                border-left: none;
                border-right: none;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: {top_rad}px;
                border-bottom-right-radius: {top_rad}px;
                selection-background-color: #2563EB;
                selection-color: #FFFFFF;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 4px 2px 4px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {scroll_thumb};
                min-height: 24px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {scroll_hover};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            QScrollBar:horizontal {{
                background: transparent;
                height: 8px;
                margin: 0px 4px 2px 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {scroll_thumb};
                min-width: 24px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {scroll_hover};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)

        for btn in [self.btn_autoscroll, self.btn_wrap, self.btn_copy, self.btn_mode, self.btn_clear]:
            btn.update_theme(is_dark)

        self._rebuild_display()

    def log(self, text: str, level: str = "info", timestamp: Optional[bool] = None):
        """
        核心日志打印接口。
        
        Args:
            text: 日志内容。
            level: 日志级别 ("info", "success", "warning", "error", "debug", "raw")。
            timestamp: 是否记录并展示时间戳；若为 None 则默认遵循 self.show_timestamp。
        """
        lvl = str(level).lower() if level else "raw"
        if lvl in ("warn", "warning"):
            lvl = "warning"
        elif lvl in ("raw", "plain", "text", "none", ""):
            lvl = "raw"
        elif lvl not in ("info", "success", "error", "debug"):
            lvl = "info"

        use_ts = self.show_timestamp if timestamp is None else bool(timestamp)
        now_str = datetime.datetime.now().strftime("%H:%M:%S") if use_ts else ""

        entry = {
            "time": now_str,
            "level": lvl,
            "text": str(text)
        }
        self._logs.append(entry)
        self._counts["all"] += 1
        if lvl != "raw":
            self._counts[lvl] = self._counts.get(lvl, 0) + 1

        # 超出行数限制则移出最早的日志
        if len(self._logs) > self._max_lines:
            removed = self._logs.pop(0)
            self._counts["all"] -= 1
            rm_lvl = removed["level"]
            if rm_lvl != "raw":
                self._counts[rm_lvl] = max(0, self._counts.get(rm_lvl, 1) - 1)
            if self._matches_filter(removed):
                doc = self.text_edit.document()
                if doc.blockCount() > 0:
                    cursor = QTextCursor(doc.begin())
                    cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                    cursor.removeSelectedText()
                    cursor.deleteChar()

        self._update_pill_counts()

        # 如果之前展示的是空状态提示，首次打印时先清空
        if len(self._logs) == 1:
            self.text_edit.clear()

        # 检查是否命中当前筛选规则与搜索词
        if self._matches_filter(entry):
            html_line = self._format_entry_html(entry)
            self.text_edit.append(html_line)
            if self._autoscroll:
                self.text_edit.moveCursor(QTextCursor.MoveOperation.End)

    def _matches_filter(self, entry: Dict[str, Any]) -> bool:
        if self.show_filters and self._current_filter_level != "all":
            if entry["level"] != self._current_filter_level:
                return False
        if self._search_keyword and self._search_keyword.lower() not in entry["text"].lower():
            return False
        return True

    def _format_entry_html(self, entry: Dict[str, Any]) -> str:
        lvl = entry["level"]
        t = ThemeEngine
        is_dark = True if self.terminal_mode == "dark" else t.is_dark()

        if is_dark:
            time_color = "#64748B"
            text_color = "#F1F5F9"
            badge_styles = {
                "info": ("#172554", "#60A5FA", "&nbsp;INFO&nbsp;&nbsp;&nbsp;"),
                "success": ("#064E3B", "#34D399", "&nbsp;SUCCESS"),
                "warning": ("#451A03", "#FBBF24", "&nbsp;WARN&nbsp;&nbsp;&nbsp;"),
                "error": ("#450A0A", "#F87171", "&nbsp;ERROR&nbsp;&nbsp;"),
                "debug": ("#27272A", "#A1A1AA", "&nbsp;DEBUG&nbsp;&nbsp;")
            }
        else:
            time_color = "#94A3B8"
            text_color = "#0F172A"
            badge_styles = {
                "info": ("#EFF6FF", "#2563EB", "&nbsp;INFO&nbsp;&nbsp;&nbsp;"),
                "success": ("#ECFDF5", "#059669", "&nbsp;SUCCESS"),
                "warning": ("#FFFBEB", "#D97706", "&nbsp;WARN&nbsp;&nbsp;&nbsp;"),
                "error": ("#FEF2F2", "#DC2626", "&nbsp;ERROR&nbsp;&nbsp;"),
                "debug": ("#F1F5F9", "#64748B", "&nbsp;DEBUG&nbsp;&nbsp;")
            }

        time_part = f'<span style="color: {time_color}; font-family: Consolas;">{entry["time"]}</span>&nbsp;&nbsp;' if entry["time"] else ""

        # 是否展示彩色级别微徽标
        if self.show_level_tags and lvl in badge_styles:
            bg_col, fg_col, tag_html = badge_styles[lvl]
            badge_part = f'<span style="background-color: {bg_col}; color: {fg_col}; font-family: Consolas; font-weight: bold;">{tag_html}&nbsp;</span>&nbsp;&nbsp;'
        else:
            badge_part = ""

        # 安全转义并保留空格（&nbsp;）以确保 YOLO 训练等表格与字符严密对齐
        safe_text = html.escape(entry["text"]).replace(" ", "&nbsp;")

        return f'<p style="margin: 2px 0; line-height: 150%; font-family: Consolas, monospace;">{time_part}{badge_part}<span style="color: {text_color}; font-family: Consolas, monospace;">{safe_text}</span></p>'

    def _rebuild_display(self):
        self.text_edit.clear()
        if not self._logs:
            # 优雅现代化终端空状态引导 (不使用表情符号)
            t = ThemeEngine
            is_dark = True if self.terminal_mode == "dark" else t.is_dark()
            muted_col = t.get("--text-muted", "#64748B" if is_dark else "#94A3B8")
            empty_msg = f"""
            <div style="text-align: left; padding: 6px 0; color: {muted_col};">
                <p style="font-family: Consolas; font-size: 13px; margin: 0;">
                    等待日志输出...
                </p>
            </div>
            """
            self.text_edit.setHtml(empty_msg)
            return

        matching_entries = [e for e in self._logs if self._matches_filter(e)]
        html_lines = [self._format_entry_html(e) for e in matching_entries]
        self.text_edit.setHtml("".join(html_lines))
        if self._autoscroll:
            self.text_edit.moveCursor(QTextCursor.MoveOperation.End)

    def set_filter_level(self, level: str):
        """设置当前日志级别筛选 ('all', 'info', 'success', 'warning', 'error', 'debug')"""
        lvl = level.lower()
        if lvl in ("warn", "warning"):
            lvl = "warning"
        self._current_filter_level = lvl
        for k, pill in self.filter_pills.items():
            pill.set_selected(k == lvl)
        self._rebuild_display()

    def _on_search_changed(self, text: str):
        self._search_keyword = text.strip()
        self._rebuild_display()

    def set_filter_text(self, text: str):
        """代码设置关键字过滤"""
        self.search_input.setText(text)

    def _toggle_autoscroll(self):
        self._autoscroll = not self._autoscroll
        self.btn_autoscroll.is_active_toggle = self._autoscroll
        self.btn_autoscroll.update_theme(True if self.terminal_mode == "dark" else ThemeEngine.is_dark())
        if self._autoscroll:
            self.text_edit.moveCursor(QTextCursor.MoveOperation.End)

    def _toggle_wrap(self):
        self._word_wrap = not self._word_wrap
        self.btn_wrap.is_active_toggle = self._word_wrap
        self.btn_wrap.update_theme(True if self.terminal_mode == "dark" else ThemeEngine.is_dark())
        mode = QTextEdit.LineWrapMode.WidgetWidth if self._word_wrap else QTextEdit.LineWrapMode.NoWrap
        self.text_edit.setLineWrapMode(mode)

    def copy_all(self):
        """复制当前符合筛选的所有日志至系统剪贴板"""
        lines = []
        for e in self._logs:
            if self._matches_filter(e):
                t_part = f"[{e['time']}] " if e['time'] else ""
                lvl_part = f"[{e['level'].upper()}] " if self.show_level_tags and e['level'] != "raw" else ""
                lines.append(f"{t_part}{lvl_part}{e['text']}")
        text = "\n".join(lines)
        QApplication.clipboard().setText(text)
        orig_tip = self.btn_copy.toolTip()
        self.btn_copy.setToolTip("已复制全部日志！")
        QTimer.singleShot(1500, lambda: self.btn_copy.setToolTip(orig_tip))

    def export_logs(self, filepath: Optional[str] = None):
        """将日志导出为文本文件"""
        if not filepath:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "导出控制台日志", "console_logs.log", "Log Files (*.log *.txt);;All Files (*)"
            )
        if filepath:
            try:
                lines = []
                for e in self._logs:
                    t_part = f"[{e['time']}] " if e['time'] else ""
                    lvl_part = f"[{e['level'].upper()}] " if self.show_level_tags and e['level'] != "raw" else ""
                    lines.append(f"{t_part}{lvl_part}{e['text']}")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
            except Exception as e:
                self.error(f"导出日志失败: {e}")

    def clear(self):
        """清空控制台所有日志与计数器"""
        self._logs.clear()
        for k in self._counts:
            self._counts[k] = 0
        self._update_pill_counts()
        self._rebuild_display()

    def set_max_lines(self, limit: int):
        """设置最大日志保留行数限制，防止内存泄漏"""
        if limit > 0:
            self._max_lines = limit
            while len(self._logs) > self._max_lines:
                removed = self._logs.pop(0)
                self._counts["all"] -= 1
                rm_lvl = removed["level"]
                self._counts[rm_lvl] = max(0, self._counts.get(rm_lvl, 1) - 1)
            self._update_pill_counts()
            self._rebuild_display()

    def set_autoscroll(self, enabled: bool):
        """设置是否开启自动滚动到底部"""
        self._autoscroll = bool(enabled)
        self.btn_autoscroll.is_active_toggle = self._autoscroll
        self.btn_autoscroll.update_theme(True if self.terminal_mode == "dark" else ThemeEngine.is_dark())

    def set_show_timestamp(self, show: bool):
        """设置是否记录与展示时间戳"""
        self._show_timestamp = bool(show)

    def _update_pill_counts(self):
        for k, pill in self.filter_pills.items():
            pill.set_count(self._counts.get(k, 0))

    # ── 快捷日志打印 API (全向兼容原有代码) ──
    def info(self, text: str):
        self.log(text, "info")

    def success(self, text: str):
        self.log(text, "success")

    def warn(self, text: str):
        self.log(text, "warning")

    def warning(self, text: str):
        self.log(text, "warning")

    def error(self, text: str):
        self.log(text, "error")

    def debug(self, text: str):
        self.log(text, "debug")
