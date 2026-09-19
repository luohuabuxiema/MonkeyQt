from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QFrame, QSizePolicy
from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QIcon, QPainter, QColor
from monkeyqt.core.icons import MkPhosphorIcon, PHOSPHOR_ICONS
from monkeyqt.themes.engine import ThemeEngine


def _resolve_icon_pixmap(icon_val, color=None, size=18):
    """Resolve icon object, monkeyqt-icons name, or inline Phosphor icon into a QPixmap."""
    if not icon_val:
        return None
    if color is None:
        color = ThemeEngine.get("--text-muted", "#606266")
    if hasattr(icon_val, "pixmap"):
        try:
            return icon_val.pixmap(size=size, color=color)
        except Exception:
            try:
                return icon_val.pixmap(size=size)
            except Exception:
                pass
    if isinstance(icon_val, str):
        try:
            from monkeyqt.icons import Ph
            pm = Ph.pixmap(icon_val, size=size, color=color)
            if pm and not pm.isNull():
                return pm
        except Exception:
            pass
        if icon_val in PHOSPHOR_ICONS:
            return MkPhosphorIcon.get_pixmap(icon_val, color, size)
    return None


class MkMenuItem(QPushButton):
    """最底层的菜单项"""
    def __init__(self, item_id, text, icon=None, height=50, parent=None):
        super().__init__(parent) # Do not pass text here, we use labels
        self.item_id = item_id
        self._original_text = text
        self._icon_str = icon
        self._item_height = height
        self.setFixedHeight(self._item_height) # 设置前端标准高度
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(12, 0, 12, 0)
        self._layout.setSpacing(12)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedWidth(24)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        if self._icon_str:
            pm = _resolve_icon_pixmap(self._icon_str, "#606266", 18)
            if pm:
                self.icon_label.setPixmap(pm)
            else:
                self.icon_label.setText(str(self._icon_str))
        
        self.text_label = QLabel(self._original_text)
        self.text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self._layout.addWidget(self.icon_label)
        self._layout.addWidget(self.text_label)
        self._layout.addStretch()
        
        self._base_style = """
            MkMenuItem {
                border: none;
                background-color: transparent;
                border-radius: 8px;
                margin: 2px 10px;
                padding: 0px 8px;
            }
            MkMenuItem:hover {
                background-color: rgba(0, 0, 0, 0.04);
                border-radius: 8px;
            }
            MkMenuItem:checked {
                background-color: rgba(0, 0, 0, 0.08);
                border-radius: 8px;
            }
        """
        
        self.setStyleSheet(self._base_style)
        self._apply_theme_style()
        try:
            ThemeEngine.instance().themeChanged.connect(self._apply_theme_style)
        except Exception:
            pass
        self.toggled.connect(self._on_toggled)

    def _apply_theme_style(self, theme_name=None):
        active_bg = ThemeEngine.get("--sidebar-active-bg", "rgba(255, 255, 255, 0.12)" if ThemeEngine.is_dark() else "rgba(0, 0, 0, 0.08)")
        active_fg = ThemeEngine.get("--sidebar-active-fg", "#FFFFFF" if ThemeEngine.is_dark() else "#0F172A")
        hover_bg = ThemeEngine.get("--sidebar-hover-bg", "rgba(255, 255, 255, 0.06)" if ThemeEngine.is_dark() else "rgba(0, 0, 0, 0.04)")
        muted = ThemeEngine.get("--sidebar-text-muted", "#A1A1AA" if ThemeEngine.is_dark() else "#64748B")
        font_family = ThemeEngine.get("--font", '"Segoe UI", "Microsoft YaHei", "PingFang SC", Arial, sans-serif')

        self._base_style = f"""
            MkMenuItem {{
                border: none;
                background-color: transparent;
                border-radius: 8px;
                margin: 2px 10px;
                padding: 0px 8px;
            }}
            MkMenuItem:hover {{
                background-color: {hover_bg};
                border-radius: 8px;
            }}
            MkMenuItem:checked {{
                background-color: {active_bg};
                border-radius: 8px;
            }}
        """
        self.setStyleSheet(self._base_style)
        self._label_style = f"""
            QLabel {{
                color: {muted};
                font-size: 14px;
                font-family: {font_family};
                font-weight: 500;
                border: none;
                background: transparent;
            }}
        """
        self._label_checked_style = f"""
            QLabel {{
                color: {active_fg};
                font-size: 14px;
                font-family: {font_family};
                font-weight: 600;
                border: none;
                background: transparent;
            }}
        """
        self._label_hover_style = f"""
            QLabel {{
                color: {active_fg};
                font-size: 14px;
                font-family: {font_family};
                font-weight: 500;
                border: none;
                background: transparent;
            }}
        """
        self._update_label_styles()

    def _on_toggled(self, checked):
        self._update_label_styles()

    def _update_icon_color(self, color_hex):
        pm = _resolve_icon_pixmap(self._icon_str, color_hex, 18)
        if pm:
            self.icon_label.setPixmap(pm)

    def enterEvent(self, event):
        super().enterEvent(event)
        if not self.isChecked():
            active_fg = ThemeEngine.get("--sidebar-active-fg", "#FFFFFF" if ThemeEngine.is_dark() else "#0F172A")
            self.text_label.setStyleSheet(getattr(self, "_label_hover_style", ""))
            self._update_icon_color(active_fg)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._update_label_styles()

    def _update_label_styles(self):
        active_fg = ThemeEngine.get("--sidebar-active-fg", "#FFFFFF" if ThemeEngine.is_dark() else "#0F172A")
        muted = ThemeEngine.get("--sidebar-text-muted", "#A1A1AA" if ThemeEngine.is_dark() else "#64748B")
        if self.isChecked():
            self.text_label.setStyleSheet(getattr(self, "_label_checked_style", ""))
            self._update_icon_color(active_fg)
        else:
            self.text_label.setStyleSheet(getattr(self, "_label_style", ""))
            self._update_icon_color(muted)

    def set_collapsed(self, is_collapsed):
        if is_collapsed:
            self.text_label.hide()
            self.setToolTip(self._original_text)
            self._layout.setContentsMargins(20, 0, 20, 0)
            self.icon_label.setAlignment(Qt.AlignCenter)
        else:
            self.text_label.show()
            self.setToolTip("")
            # Submenu items might need more left margin, we can handle that by setting margins externally
            self._layout.setContentsMargins(self._current_left_margin, 0, 20, 0)

    @property
    def _current_left_margin(self):
        return getattr(self, '_left_margin_val', 20)

    def set_left_margin(self, margin):
        self._left_margin_val = margin
        if not self.text_label.isHidden(): # meaning not collapsed
            self._layout.setContentsMargins(margin, 0, 20, 0)


from ..layout.widget import MkQWidget


class MkSubMenu(MkQWidget):
    """带折叠功能的子菜单容器"""
    toggled = Signal(bool)

    def __init__(self, title, icon=None, height=50, parent=None):
        super().__init__(parent)
        self._original_title = title
        self._icon_str = icon
        self._is_expanded = False
        self._item_height = height
        self._items = [] # 存储子项
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # 标题按钮（使用与 MkMenuItem 类似的布局以保证对齐）
        self.title_btn = QPushButton()
        self.title_btn.setObjectName("SubMenuTitleButton")
        self.title_btn.setFixedHeight(self._item_height) # 设置前端标准高度
        self.title_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                border-radius: 8px;
                margin: 2px 10px;
                padding: 0px 8px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.04);
                border-radius: 8px;
            }
        """)
        
        self.title_layout = QHBoxLayout(self.title_btn)
        self.title_layout.setContentsMargins(12, 0, 12, 0)
        self.title_layout.setSpacing(12)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedWidth(24)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.text_label = QLabel(self._original_title)
        self.text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self._apply_theme_style()
        try:
            ThemeEngine.instance().themeChanged.connect(self._apply_theme_style)
        except Exception:
            pass
        
        self.title_layout.addWidget(self.icon_label)
        self.title_layout.addWidget(self.text_label)
        self.title_layout.addStretch()

        self.title_btn.clicked.connect(self.toggle)
        
        # 为了实现悬浮变色，需要重写 enterEvent 和 leaveEvent 或使用事件过滤器
        self.title_btn.installEventFilter(self)
        
        self._layout.addWidget(self.title_btn)

        # 子菜单容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # 初始状态隐藏
        self.content_widget.setVisible(False)
        self._layout.addWidget(self.content_widget)

    def _apply_theme_style(self, theme_name=None):
        fg = ThemeEngine.get("--fg", "#303133")
        hover_bg = ThemeEngine.get("--sidebar-hover-bg", "rgba(255, 255, 255, 0.06)" if ThemeEngine.is_dark() else "rgba(0, 0, 0, 0.04)")
        self.title_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-color: transparent;
                border-radius: 8px;
                margin: 2px 10px;
                padding: 0px 8px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                border-radius: 8px;
            }}
        """)
        self.text_label.setStyleSheet(f"color: {fg}; font-size: 14px; font-weight: 500;")
        if self._icon_str:
            pm = _resolve_icon_pixmap(self._icon_str, fg, 18)
            if pm:
                self.icon_label.setPixmap(pm)
            else:
                self.icon_label.setText(str(self._icon_str))

    def eventFilter(self, obj, event):
        if obj == self.title_btn:
            active_fg = ThemeEngine.get("--sidebar-active-fg", "#FFFFFF" if ThemeEngine.is_dark() else "#0F172A")
            fg = ThemeEngine.get("--fg", "#303133")
            if event.type() == event.Type.Enter:
                pm = _resolve_icon_pixmap(self._icon_str, active_fg, 18)
                if pm:
                    self.icon_label.setPixmap(pm)
                self.text_label.setStyleSheet(f"color: {active_fg}; font-size: 14px; font-weight: 500;")
            elif event.type() == event.Type.Leave:
                pm = _resolve_icon_pixmap(self._icon_str, fg, 18)
                if pm:
                    self.icon_label.setPixmap(pm)
                self.text_label.setStyleSheet(f"color: {fg}; font-size: 14px; font-weight: 500;")
        return super().eventFilter(obj, event)
        return super().eventFilter(obj, event)

    def add_item(self, item: MkMenuItem):
        self._items.append(item)
        self.content_layout.addWidget(item)

    def toggle(self):
        # 折叠模式下，暂不支持展开子菜单
        self._is_expanded = not self._is_expanded
        self.content_widget.setVisible(self._is_expanded)
        self.toggled.emit(self._is_expanded)

    def set_collapsed(self, is_collapsed):
        if is_collapsed:
            self.text_label.hide()
            self.title_btn.setToolTip(self._original_title)
            self.content_widget.setVisible(False) # 强制收起子项
            self.title_layout.setContentsMargins(20, 0, 20, 0)
            for i in range(self.title_layout.count()):
                item = self.title_layout.itemAt(i)
                w = item.widget() if item else None
                if w and w not in (self.icon_label, self.text_label):
                    w.hide()
        else:
            self.text_label.show()
            self.title_btn.setToolTip("")
            self.content_widget.setVisible(self._is_expanded) # 恢复原来的展开状态
            self.title_layout.setContentsMargins(20, 0, 20, 0)
            for i in range(self.title_layout.count()):
                item = self.title_layout.itemAt(i)
                w = item.widget() if item else None
                if w and w not in (self.icon_label, self.text_label):
                    w.show()
        
        for item in self._items:
            item.set_collapsed(is_collapsed)

class MkMenu(MkQWidget):
    """
    Element Plus 风格的侧边栏 (ElMenu)
    支持多级折叠 (SubMenu)、菜单项 (MenuItem) 和顶部标题区，
    支持悬浮折叠按钮或汉堡包按钮收缩。
    """
    itemClicked = Signal(str)

    def __init__(self, title="", icon=None, collapse_mode="floating", item_height=50, parent=None):
        super().__init__(parent)
        self._is_collapsed = False
        self._title = title
        self._icon = icon
        self._collapse_mode = collapse_mode
        self._item_height = item_height
        
        # 整体主布局
        self.main_layout = QVBoxLayout(self)
        if self._collapse_mode == "floating":
            self.main_layout.setContentsMargins(0, 0, 12, 0)
        else:
            self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # 带有右边框的内部框架
        self.inner_frame = QFrame(self)
        self.inner_frame.setObjectName("SidebarInnerFrame")
        self.inner_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.inner_layout = QVBoxLayout(self.inner_frame)
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_layout.setSpacing(0)
        
        # --- 1. 顶部标题区域 ---
        self.title_area = QWidget()
        self.title_area.setObjectName("SidebarTitleArea")
        self.title_area.setFixedHeight(60)
        self.title_layout = QHBoxLayout(self.title_area)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.setSpacing(0) # Remove default spacing
        
        # 汉堡包按钮 (如果模式为 hamburger)
        self.hamburger_btn = QPushButton("≡")
        self.hamburger_btn.setObjectName("SidebarHamburgerButton")
        self.hamburger_btn.setFixedSize(64, 60)
        self.hamburger_btn.setCursor(Qt.PointingHandCursor)
        self.hamburger_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 20px;
                color: #606266;
                padding: 0px;
                margin: 0px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.04);
            }
        """)
        self.hamburger_btn.clicked.connect(self.toggle_collapse)
        
        # 头部折叠按钮
        self.header_collapse_btn = QPushButton()
        self.header_collapse_btn.setObjectName("SidebarHeaderCollapseButton")
        self.header_collapse_btn.setFixedSize(36, 36)
        self.header_collapse_btn.setCursor(Qt.PointingHandCursor)
        self.header_collapse_btn.setIcon(MkPhosphorIcon.get_icon("sidebar", "#606266", size=20))
        self.header_collapse_btn.setIconSize(QSize(20, 20))
        self.header_collapse_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #f5f7fa;
                border: none;
            }
        """)
        self.header_collapse_btn.clicked.connect(self.toggle_collapse)
        
        if self._collapse_mode != "header":
            self.header_collapse_btn.hide()
            
        if self._collapse_mode == "hamburger":
            self.title_layout.addWidget(self.hamburger_btn)
            # 汉堡包模式下，如果仍有图标，放到汉堡包后面
            if self._icon:
                self.icon_label = QLabel()
                self.icon_label.setFixedWidth(24)
                self.icon_label.setAlignment(Qt.AlignCenter)
                pm = _resolve_icon_pixmap(self._icon, "#303133", 20)
                if pm:
                    self.icon_label.setPixmap(pm)
                else:
                    self.icon_label.setText(str(self._icon))
                self.title_layout.addWidget(self.icon_label)
                self.title_layout.addSpacing(8) # 图标与文字的间距
            else:
                self.icon_label = QLabel() # placeholder
                self.icon_label.hide()
        elif self._collapse_mode == "header":
            self.hamburger_btn.hide()
            self.title_layout.setContentsMargins(20, 0, 16, 0)
            self.icon_label = QLabel()
            self.icon_label.setFixedWidth(24)
            self.icon_label.setAlignment(Qt.AlignCenter)
            if self._icon:
                pm = _resolve_icon_pixmap(self._icon, "#303133", 20)
                if pm:
                    self.icon_label.setPixmap(pm)
                else:
                    self.icon_label.setText(str(self._icon))
                self.title_layout.addWidget(self.icon_label)
                self.title_layout.addSpacing(12)
            else:
                self.icon_label.hide()
        else:
            self.hamburger_btn.hide()
            self.title_layout.addSpacing(20) # 悬浮模式左侧留白 20
            
            # 标题图标
            self.icon_label = QLabel()
            self.icon_label.setFixedWidth(24) # Match MkMenuItem icon width
            self.icon_label.setAlignment(Qt.AlignCenter)
            if self._icon:
                pm = _resolve_icon_pixmap(self._icon, "#303133", 20)
                if pm:
                    self.icon_label.setPixmap(pm)
                else:
                    self.icon_label.setText(str(self._icon))
            self.title_layout.addWidget(self.icon_label)
            self.title_layout.addSpacing(20) # 20 + 24 + 20 = 64
            
        # 标题文本
        self.title_label = QLabel(self._title)
        self.title_label.setObjectName("SidebarTitleLabel")
        title_font = self.title_label.font()
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.title_label.setMinimumHeight(24)
        self.title_layout.addWidget(self.title_label)
        
        self.title_layout.addStretch()
        
        if self._collapse_mode == "header":
            self.title_layout.addWidget(self.header_collapse_btn)
            
        self.inner_layout.addWidget(self.title_area)
        
        self._apply_theme_style()
        try:
            ThemeEngine.instance().themeChanged.connect(self._apply_theme_style)
        except Exception:
            pass
        
        # --- 2. 核心滚动区域 ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("SidebarScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c4cc;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #909399;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent; border: none;")
        self._layout = QVBoxLayout(self.content_widget)
        self._layout.setContentsMargins(0, 10, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addStretch()

        self.scroll_area.setWidget(self.content_widget)
        self.inner_layout.addWidget(self.scroll_area)
        
        self.main_layout.addWidget(self.inner_frame)

        # 设置初始宽度
        self.setFixedWidth(200)

        # 存储所有 item 以便管理排他性高亮
        self._all_items = []
        self._all_submenus = []
        
        # --- 3. 悬浮在边框上的收缩展开按钮 ---
        # 作为 MkMenu 的子组件，使用 resizeEvent 进行绝对定位
        self.collapse_btn = QPushButton("❮", self)
        self.collapse_btn.setObjectName("SidebarCollapseButton")
        self.collapse_btn.setFixedSize(24, 24)
        self.collapse_btn.setCursor(Qt.PointingHandCursor)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #dcdfe6;
                border-radius: 12px;
                color: #606266;
                font-size: 12px;
                font-weight: bold;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: #f5f7fa;
            }
        """)
        self.collapse_btn.clicked.connect(self.toggle_collapse)
        if self._collapse_mode in ("hamburger", "header"):
            self.collapse_btn.hide()

    def _apply_theme_style(self, theme_name=None):
        fg = ThemeEngine.get("--fg", "#303133")
        active_fg = ThemeEngine.get("--sidebar-active-fg", "#FFFFFF" if ThemeEngine.is_dark() else "#0F172A")
        hover_bg = ThemeEngine.get("--sidebar-hover-bg", "rgba(255, 255, 255, 0.06)" if ThemeEngine.is_dark() else "rgba(0, 0, 0, 0.04)")
        border = ThemeEngine.get("--border", "#E2E8F0")
        surface = ThemeEngine.get("--surface", "#FFFFFF")
        if hasattr(self, "title_label"):
            self.title_label.setStyleSheet(f"color: {fg}; font-size: 15px; font-weight: bold;")
        if hasattr(self, "hamburger_btn"):
            self.hamburger_btn.setStyleSheet(f"""
                QPushButton {{
                    border: none;
                    background: transparent;
                    font-size: 20px;
                    color: {fg};
                    padding: 0px;
                    margin: 0px;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    color: {active_fg};
                    background-color: {hover_bg};
                }}
            """)
        if hasattr(self, "collapse_btn"):
            self.collapse_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {surface};
                    border: 1px solid {border};
                    border-radius: 12px;
                    color: {fg};
                    font-size: 12px;
                    font-weight: bold;
                    padding-bottom: 2px;
                }}
                QPushButton:hover {{
                    color: {active_fg};
                    border-color: {active_fg};
                    background-color: {hover_bg};
                }}
            """)
        if hasattr(self, "icon_label") and getattr(self, "_icon", None):
            pm = _resolve_icon_pixmap(self._icon, fg, 20)
            if pm:
                self.icon_label.setPixmap(pm)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._collapse_mode == "floating":
            # 将按钮定位在右侧边缘内侧，避免被裁剪和引入额外的 layout margin
            self.collapse_btn.move(self.width() - 24, 28)
            self.collapse_btn.raise_()

    def enable_collapse_button(self, enable=True):
        """兼容老接口，现在折叠按钮默认显示"""
        self.collapse_btn.setVisible(enable)

    def set_border_right(self, border_style: str):
        """设置右侧边框样式，例如 'none' 或者 '1px solid #dcdfe6'"""
        self._border_right_style = border_style
        if border_style == "none":
            self.inner_frame.setProperty("border_right_none", "true")
        else:
            self.inner_frame.setProperty("border_right_none", "false")
        self.inner_frame.style().unpolish(self.inner_frame)
        self.inner_frame.style().polish(self.inner_frame)
        self.inner_frame.update()

    def add_item(self, item_id: str, text: str, icon=None) -> MkMenuItem:
        """添加一级菜单项"""
        item = MkMenuItem(item_id, text, icon, height=self._item_height)
        item.set_left_margin(20)
        self._register_item(item)
        self._layout.insertWidget(self._layout.count() - 1, item)
        return item

    def add_submenu(self, title: str, icon=None) -> MkSubMenu:
        """添加一个折叠子菜单"""
        submenu = MkSubMenu(title, icon, height=self._item_height)
        self._all_submenus.append(submenu)
        self._layout.insertWidget(self._layout.count() - 1, submenu)
        return submenu
        
    def add_submenu_item(self, submenu: MkSubMenu, item_id: str, text: str, icon=None) -> MkMenuItem:
        """向子菜单中添加项"""
        item = MkMenuItem(item_id, text, icon, height=self._item_height)
        item._parent_submenu = submenu
        item.set_left_margin(40) # 子菜单项缩进
        self._register_item(item)
        submenu.add_item(item)
        return item

    def _register_item(self, item: MkMenuItem):
        self._all_items.append(item)
        item.clicked.connect(lambda checked=False, i=item: self._on_item_clicked(i))

    def _on_item_clicked(self, clicked_item: MkMenuItem):
        # 实现类似 QButtonGroup 的排他性（互斥）
        for item in self._all_items:
            if item != clicked_item:
                item.setChecked(False)
        clicked_item.setChecked(True)
        self.itemClicked.emit(clicked_item.item_id)

    def set_active(self, item_id: str):
        """代码层面设置高亮"""
        for item in self._all_items:
            if item.item_id == item_id:
                self._on_item_clicked(item)
                parent_sub = getattr(item, "_parent_submenu", None)
                if parent_sub and not parent_sub._is_expanded:
                    parent_sub.toggle()
                break

    def toggle_collapse(self):
        """切换菜单折叠/展开状态"""
        self._is_collapsed = not self._is_collapsed
        target_width = 64 if self._is_collapsed else 200
        self.setFixedWidth(target_width)
        
        if self._is_collapsed:
            self.title_label.hide()
            self.icon_label.hide()
            if self._collapse_mode == "floating":
                self.collapse_btn.setText("❯")
            elif self._collapse_mode == "header":
                self.title_layout.setContentsMargins(14, 0, 14, 0)
        else:
            self.title_label.show()
            if self._collapse_mode == "floating":
                # Only show icon_label if we are in floating mode, or in hamburger mode but with an icon
                if self._icon or self._collapse_mode == "floating":
                    self.icon_label.show()
                self.collapse_btn.setText("❮")
            elif self._collapse_mode == "header":
                if self._icon:
                    self.icon_label.show()
                self.title_layout.setContentsMargins(20, 0, 16, 0)
            else:
                if self._icon:
                    self.icon_label.show()
            
        # 告诉所有子元素当前的状态，让他们隐藏文字
        for item in self._all_items:
            item.set_collapsed(self._is_collapsed)
        for submenu in self._all_submenus:
            submenu.set_collapsed(self._is_collapsed)
