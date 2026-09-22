# -*- coding: utf-8 -*-
"""
MonkeyQt 列表选择项交互组件与多选卡片组合组件
- MkSelectItem: 单个列表选择项交互组件，现代无经典蓝配色，鼠标悬浮显示操作按钮，自适应深浅主题。
- MkSelectGroupHeader: 分组折叠标题栏（参考图三: v Detect   2）。
- MkSelectCard: 多选卡片组合组件，集成头部徽标、全选联动、分组管理与平滑滚动列表。
完美自适应 MonkeyQt 全部 68 种主题风格。
"""

from typing import Any, Dict, List, Optional, Union
from PySide6.QtCore import Qt, Signal, QSize, QPointF
from PySide6.QtGui import QColor, QFont, QIcon, QPixmap, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from monkeyqt.components.basic.checkbox import MkCheckBox
from monkeyqt.themes.engine import ThemeEngine


def _create_dot_pixmap(color: str, size: int = 10) -> QPixmap:
    """生成平滑抗锯齿的彩色圆形指示器 Pixmap（附带安全边距防裁切）。"""
    # 增加 2px 边距防抗锯齿像素截断
    pad = 2
    total = size + pad * 2
    pm = QPixmap(total, total)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color))
    painter.drawEllipse(QPointF(total / 2.0, total / 2.0), size / 2.0, size / 2.0)
    painter.end()
    return pm


class MkItemIndicator(QWidget):
    """
    自适应高清圆点/图标指示器组件。
    使用原生矢量 paintEvent 与 QPainter.Antialiasing 绘制，
    并保留足够的安全绘制边距，彻底杜绝高分屏 (High-DPI 125%/150%/200%) 下
    的点边缘像素截断 (Clipping)、锯齿与扁平切边问题。
    """
    def __init__(self, size: int = 16, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._size = size
        self._dot_color: Optional[QColor] = None
        self._dot_diameter: int = 10
        self._icon: Optional[QIcon] = None
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background: transparent;")

    def set_dot(self, color: Union[str, QColor], diameter: int = 10):
        self._dot_color = QColor(color) if isinstance(color, str) else color
        self._dot_diameter = diameter
        self._icon = None
        self.update()

    def set_icon(self, icon: Optional[QIcon]):
        self._icon = icon
        self._dot_color = None
        self.update()

    def clear(self):
        self._dot_color = None
        self._icon = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        if self._dot_color and self._dot_color.isValid():
            r = self._dot_diameter / 2.0
            cx = self.width() / 2.0
            cy = self.height() / 2.0
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self._dot_color)
            painter.drawEllipse(QPointF(cx, cy), r, r)
        elif self._icon and not self._icon.isNull():
            icon_size = min(self.width(), self.height())
            x = (self.width() - icon_size) // 2
            y = (self.height() - icon_size) // 2
            self._icon.paint(painter, x, y, icon_size, icon_size)

        painter.end()


def _resolve_icon(icon_val: Any, color: str = None, size: int = 16) -> Optional[QIcon]:
    """将图标名称、Phosphor 图标或 QIcon 统一转换为 QIcon。"""
    if not icon_val:
        return None
    if isinstance(icon_val, QIcon):
        return icon_val
    if isinstance(icon_val, QPixmap):
        return QIcon(icon_val)

    if color is None:
        color = ThemeEngine.get("--text-muted", "#71717A")

    if hasattr(icon_val, "icon"):
        try:
            return icon_val.icon(color=color, size=size)
        except Exception:
            pass

    if isinstance(icon_val, str):
        try:
            from monkeyqt.icons import Ph
            pm = Ph.pixmap(icon_val, size=size, color=color)
            if pm and not pm.isNull():
                return QIcon(pm)
        except Exception:
            pass
        try:
            from monkeyqt.core.icons import MkPhosphorIcon, PHOSPHOR_ICONS
            if icon_val in PHOSPHOR_ICONS:
                pm = MkPhosphorIcon.get_pixmap(icon_val, color, size)
                if pm and not pm.isNull():
                    return QIcon(pm)
        except Exception:
            pass

    return None


class MkItemActionButton(QToolButton):
    """
    单项快捷操作按钮（如下载、删除、编辑等）。
    支持 hover 变色、danger 报警红底动效以及主题实时联动。
    """
    def __init__(
        self,
        key: str,
        icon_val: Any,
        tooltip: str = "",
        danger: bool = False,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.key = key
        self._icon_val = icon_val
        self._danger = danger
        self._is_hovered = False

        self.setFixedSize(26, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAutoRaise(True)
        if tooltip:
            self.setToolTip(tooltip)

        ThemeEngine.instance().themeChanged.connect(self._apply_style)
        self._apply_style()

    def _apply_style(self, theme_name: str = None):
        t = ThemeEngine
        is_dark = t.is_dark()
        normal_color = t.get("--text-muted", "#71717A" if is_dark else "#64748B")

        if is_dark:
            normal_bg = "#27272A"
            if self._danger:
                hover_color = "#EF4444"
                hover_bg = "rgba(239, 68, 68, 0.25)"
            else:
                hover_color = "#F8FAFC"
                hover_bg = "rgba(255, 255, 255, 0.16)"
        else:
            # 参考图一：独立白色圆角按键，无外层胶囊背景连体
            normal_bg = "#FFFFFF"
            if self._danger:
                hover_color = "#EF4444"
                hover_bg = "#FEE2E2"
            else:
                hover_color = "#0F172A"
                hover_bg = "#F1F5F9"

        curr_color = hover_color if self._is_hovered else normal_color
        icon = _resolve_icon(self._icon_val, color=curr_color, size=14)
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(14, 14))

        curr_bg = hover_bg if self._is_hovered else normal_bg

        self.setStyleSheet(f"""
            QToolButton {{
                border: none;
                border-radius: 6px;
                background-color: {curr_bg};
                padding: 0px;
            }}
        """)

    def enterEvent(self, event):
        super().enterEvent(event)
        self._is_hovered = True
        self._apply_style()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._is_hovered = False
        self._apply_style()


class MkSelectItem(QFrame):
    """
    单个列表选择项交互组件（参考图三现代卡片风格，告别经典蓝色）。
    
    结构：[复选框(中性暗调)] + [彩色圆点/图标] + [标题 + 指标副标题] + [悬浮操作按钮组/跳转箭头]
    
    特性:
        - 默认只有鼠标悬浮在该项上时才显示右侧操作图标 (actions_visible_on_hover=True)。
        - 选中状态呈现精致的白色悬浮卡片感（深色模式下为精致暗卡片），彻底告别经典蓝色！
    
    信号:
        toggled(bool): 勾选状态改变
        checked_changed(item_id, bool): 勾选状态改变并附带 item_id
        clicked(item_id): 点击整行（非子控件交互时）
        detail_clicked(item_id): 点击详情箭头
        action_clicked(action_key, item_id): 点击某个操作按钮
    """
    toggled = Signal(bool)
    checked_changed = Signal(object, bool)
    clicked = Signal(object)
    navigated = Signal(object)              # 专门预留：点击进入/跳转到指定项目或页面事件
    open_requested = Signal(object)         # 别名，兼容进入项目请求
    double_clicked = Signal(object)         # 双击条目事件
    detail_clicked = Signal(object)
    action_clicked = Signal(str, object)
    group_changed = Signal(object)

    def __init__(
        self,
        item_id: Any = None,
        title: str = "",
        subtitle: str = "",
        dot_color: Optional[str] = None,
        icon: Optional[Union[str, QIcon]] = None,
        selectable: bool = True,
        checked: bool = False,
        actions: Optional[List[Dict[str, Any]]] = None,
        show_arrow: bool = False,
        actions_visible_on_hover: bool = True,
        checkable_by_click: bool = False,
        navigate_on_click: bool = True,
        target_page: Optional[str] = None,
        group_id: Optional[str] = None,
        data: Any = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setObjectName("MkSelectItem")
        self._item_id = item_id if item_id is not None else title
        self._title_text = title
        self._subtitle_text = subtitle
        self._dot_color = dot_color
        self._icon_val = icon
        self._selectable = selectable
        self._is_checked = checked
        self._actions_config = actions or []
        self._show_arrow = show_arrow
        self._actions_visible_on_hover = actions_visible_on_hover
        self._checkable_by_click = checkable_by_click
        self._navigate_on_click = navigate_on_click
        self._target_page = target_page
        self._group_id = group_id
        self._user_data = data
        self._is_hovered = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._init_ui()
        ThemeEngine.instance().themeChanged.connect(self._apply_style)
        self._apply_style()

    def _init_ui(self):
        self._main_layout = QHBoxLayout(self)
        # 高度与间距严格对齐参考图一：12px 左右内边距，9px 上下内边距，舒适大气的条目高度
        self._main_layout.setContentsMargins(12, 9, 12, 9)
        self._main_layout.setSpacing(10)

        # 默认最小高度与参考图一完全保持一致：统一 56px，舒适大气
        self.setMinimumHeight(56)

        # 1. 现代中性暗调复选框 (图三：黑色圆角框搭配白色对勾)
        self.chk = MkCheckBox(self, variant="neutral")
        self.chk.setFixedSize(18, 18)
        self.chk.setChecked(self._is_checked)
        self.chk.setVisible(self._selectable)
        self.chk.toggled.connect(self._on_chk_toggled)
        self._main_layout.addWidget(self.chk, alignment=Qt.AlignmentFlag.AlignVCenter)

        # 2. 视觉指示器（彩色圆点 或 矢量图标，16x16 原生矢量安全渲染）
        self.lbl_indicator = MkItemIndicator(size=16, parent=self)
        self._update_indicator()
        self._main_layout.addWidget(self.lbl_indicator, alignment=Qt.AlignmentFlag.AlignVCenter)

        # 3. 文本列（主标题 + 副标题/指标）
        self.text_container = QWidget(self)
        self.text_container.setStyleSheet("background: transparent;")
        text_layout = QVBoxLayout(self.text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)

        self.lbl_title = QLabel(self._title_text, self.text_container)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setWeight(QFont.Weight.Normal)
        self.lbl_title.setFont(title_font)
        self.lbl_title.setStyleSheet("background: transparent;")
        text_layout.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel(self._subtitle_text, self.text_container)
        sub_font = QFont()
        sub_font.setPointSize(9)
        self.lbl_subtitle.setFont(sub_font)
        self.lbl_subtitle.setStyleSheet("background: transparent;")
        self.lbl_subtitle.setVisible(bool(self._subtitle_text))
        text_layout.addWidget(self.lbl_subtitle)

        self._main_layout.addWidget(self.text_container, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)

        # 4. 右侧操作按钮与箭头容器（参考图一: 容器完全透明无背景，按钮独立分离）
        self.actions_container = QWidget(self)
        self.actions_container.setObjectName("MkItemActionsContainer")
        self.actions_layout = QHBoxLayout(self.actions_container)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setSpacing(4)

        # 关键优化：保留隐藏时的尺寸占位（retainSizeWhenHidden=True），
        # 确保隐藏与显现操作图标时，条目高度保持绝对一致，100% 杜绝鼠标移入移出的高度跳变抖动！
        sp = self.actions_container.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.actions_container.setSizePolicy(sp)

        self._action_buttons: List[MkItemActionButton] = []
        for act in self._actions_config:
            btn = MkItemActionButton(
                key=act.get("key", ""),
                icon_val=act.get("icon"),
                tooltip=act.get("tooltip", ""),
                danger=act.get("danger", False),
                parent=self.actions_container,
            )
            key = act.get("key", "")
            btn.clicked.connect(lambda checked=False, k=key: self.action_clicked.emit(k, self._item_id))
            self._action_buttons.append(btn)
            self.actions_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        # 详情箭头按钮 (尺寸 26x26)
        self.btn_arrow = QToolButton(self.actions_container)
        self.btn_arrow.setFixedSize(26, 26)
        self.btn_arrow.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_arrow.setAutoRaise(True)
        self.btn_arrow.setVisible(self._show_arrow)
        self.btn_arrow.clicked.connect(self._on_arrow_clicked)
        self.actions_layout.addWidget(self.btn_arrow, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._main_layout.addWidget(self.actions_container, alignment=Qt.AlignmentFlag.AlignVCenter)

        # 初始状态：若开启了悬浮展示，则默认隐藏
        if self._actions_visible_on_hover:
            self.actions_container.setVisible(False)

    def _update_indicator(self):
        """更新圆点或图标展示"""
        if self._dot_color:
            self.lbl_indicator.set_dot(self._dot_color, diameter=10)
            self.lbl_indicator.show()
        elif self._icon_val:
            icon = _resolve_icon(self._icon_val, color=ThemeEngine.get("--fg", "#1E293B"), size=16)
            if icon:
                self.lbl_indicator.set_icon(icon)
                self.lbl_indicator.show()
            else:
                self.lbl_indicator.clear()
                self.lbl_indicator.hide()
        else:
            self.lbl_indicator.clear()
            self.lbl_indicator.hide()

    def _on_chk_toggled(self, checked: bool):
        self._is_checked = checked
        self._apply_style()
        self.toggled.emit(checked)
        self.checked_changed.emit(self._item_id, checked)

    def _apply_style(self, theme_name: str = None):
        t = ThemeEngine
        is_dark = t.is_dark()
        fg = t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#71717A" if is_dark else "#64748B")

        # 样式参考图三：完全告别经典蓝色！
        # 选中时：精致卡片（微灰白卡或暗卡）；未选时：纯净透明
        if self._is_checked:
            if is_dark:
                bg = "#202023"
                active_border = "rgba(255, 255, 255, 0.12)"
                title_color = "#F8FAFC"
            else:
                bg = "#F8F8F8"
                active_border = "#E4E4E7"
                title_color = "#0F172A"
        else:
            if is_dark:
                bg = "transparent"
                active_border = "transparent"
                title_color = "#D4D4D8"
            else:
                bg = "transparent"
                active_border = "transparent"
                title_color = "#1E293B"

        if is_dark:
            hover_bg = "rgba(255, 255, 255, 0.05)" if not self._is_checked else "#262629"
            hover_border = "rgba(255, 255, 255, 0.18)" if self._is_checked else "transparent"
        else:
            hover_bg = "#F8F8F8" if not self._is_checked else "#F4F4F5"
            hover_border = "#E4E4E7" if self._is_checked else "transparent"

        self.setStyleSheet(f"""
            #MkSelectItem {{
                background-color: {bg};
                border: 1px solid {active_border};
                border-radius: 8px;
            }}
            #MkSelectItem:hover {{
                background-color: {hover_bg};
                border-color: {hover_border};
            }}
            #MkItemActionsContainer {{
                background: transparent;
                border: none;
            }}
        """)

        self.lbl_title.setStyleSheet(f"color: {title_color}; background: transparent; font-weight: normal;")
        self.lbl_subtitle.setStyleSheet(f"color: {muted}; background: transparent;")

        if self._show_arrow:
            arrow_icon = _resolve_icon("caret-right", color=muted, size=13)
            if arrow_icon:
                self.btn_arrow.setIcon(arrow_icon)
                self.btn_arrow.setIconSize(QSize(13, 13))
            arrow_bg = "#2E2E32" if is_dark else "#FFFFFF"
            arrow_hover = "rgba(255, 255, 255, 0.18)" if is_dark else "#F1F5F9"
            self.btn_arrow.setStyleSheet(f"""
                QToolButton {{
                    border: none;
                    border-radius: 5px;
                    background-color: {arrow_bg};
                    padding: 0px;
                }}
                QToolButton:hover {{
                    background-color: {arrow_hover};
                }}
            """)

        self._update_indicator()

    def enterEvent(self, event):
        super().enterEvent(event)
        self._is_hovered = True
        if self._actions_visible_on_hover:
            has_actions = bool(self._action_buttons) or self._show_arrow
            if has_actions:
                self.actions_container.setVisible(True)
        self._apply_style()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._is_hovered = False
        if self._actions_visible_on_hover:
            self.actions_container.setVisible(False)
        self._apply_style()

    def _on_arrow_clicked(self):
        self.detail_clicked.emit(self._item_id)
        self.navigated.emit(self._item_id)
        self.open_requested.emit(self._item_id)

    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if child in ([self.chk, self.btn_arrow] + self._action_buttons):
            super().mousePressEvent(event)
            return
        if self._checkable_by_click and self._selectable:
            self.set_checked(not self.is_checked())
        self.clicked.emit(self._item_id)
        if self._navigate_on_click:
            self.navigated.emit(self._item_id)
            self.open_requested.emit(self._item_id)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        child = self.childAt(event.pos())
        if child in ([self.chk, self.btn_arrow] + self._action_buttons):
            super().mouseDoubleClickEvent(event)
            return
        self.double_clicked.emit(self._item_id)
        self.navigated.emit(self._item_id)
        self.open_requested.emit(self._item_id)
        super().mouseDoubleClickEvent(event)

    # ── Public APIs ──

    @property
    def item_id(self) -> Any:
        return self._item_id

    @property
    def target_page(self) -> Optional[str]:
        return self._target_page

    @target_page.setter
    def target_page(self, val: Optional[str]):
        self._target_page = val

    @property
    def group_id(self) -> Optional[str]:
        return self._group_id

    @group_id.setter
    def group_id(self, val: Optional[str]):
        if self._group_id != val:
            self._group_id = val
            self.group_changed.emit(val)

    def is_checked(self) -> bool:
        return self.chk.isChecked()

    def set_checked(self, checked: bool, block_signal: bool = False):
        if self._is_checked == checked:
            return
        self._is_checked = checked
        if block_signal:
            self.chk.blockSignals(True)
            self.chk.setChecked(checked)
            self.chk.blockSignals(False)
            self._apply_style()
        else:
            self.chk.setChecked(checked)

    def set_title(self, title: str):
        self._title_text = title
        self.lbl_title.setText(title)

    def set_subtitle(self, subtitle: str):
        self._subtitle_text = subtitle
        self.lbl_subtitle.setText(subtitle)
        self.lbl_subtitle.setVisible(bool(subtitle))
        self.setMinimumHeight(56)

    def set_dot_color(self, color: Optional[str]):
        self._dot_color = color
        self._update_indicator()

    def set_icon(self, icon: Optional[Union[str, QIcon]]):
        self._icon_val = icon
        self._update_indicator()

    def set_selectable(self, selectable: bool):
        self._selectable = selectable
        self.chk.setVisible(selectable)

    def set_show_arrow(self, show: bool):
        self._show_arrow = show
        self.btn_arrow.setVisible(show)

    def add_action(self, key: str, icon: Any, tooltip: str = "", danger: bool = False):
        btn = MkItemActionButton(key=key, icon_val=icon, tooltip=tooltip, danger=danger, parent=self.actions_container)
        btn.clicked.connect(lambda checked=False, k=key: self.action_clicked.emit(k, self._item_id))
        self._action_buttons.append(btn)
        self.actions_layout.insertWidget(self.actions_layout.count() - 1, btn, alignment=Qt.AlignmentFlag.AlignVCenter)

    def get_data(self) -> Any:
        return self._user_data

    def set_data(self, data: Any):
        self._user_data = data


class MkSelectGroupHeader(QFrame):
    """
    分组折叠标题栏（参考图三: v Detect   2）
    """
    toggled = Signal(bool)  # collapsed 状态

    def __init__(
        self,
        group_id: str,
        title: str = "Detect",
        count: Optional[int] = None,
        collapsed: bool = False,
        auto_count: bool = True,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setObjectName("MkSelectGroupHeader")
        self.group_id = group_id
        self._title = title
        self._count = count
        self._is_collapsed = collapsed
        self.auto_count = auto_count
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._init_ui()
        ThemeEngine.instance().themeChanged.connect(self._apply_style)
        self._apply_style()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        self.lbl_arrow = QLabel(self)
        self.lbl_arrow.setFixedSize(14, 14)
        self.lbl_arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_arrow, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.lbl_title = QLabel(self._title, self)
        font = QFont()
        font.setPointSize(10)
        font.setWeight(QFont.Weight.DemiBold)
        self.lbl_title.setFont(font)
        layout.addWidget(self.lbl_title, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addStretch()

        self.lbl_count = QLabel(str(self._count) if self._count is not None else "", self)
        count_font = QFont()
        count_font.setPointSize(9)
        count_font.setWeight(QFont.Weight.Bold)
        self.lbl_count.setFont(count_font)
        self.lbl_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_count.setVisible(self._count is not None)
        layout.addWidget(self.lbl_count, alignment=Qt.AlignmentFlag.AlignVCenter)

    def _apply_style(self, theme_name: str = None):
        t = ThemeEngine
        is_dark = t.is_dark()
        fg = t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#71717A" if is_dark else "#64748B")
        count_bg = "#27272A" if is_dark else "#F1F5F9"

        arrow_name = "caret-right" if self._is_collapsed else "caret-down"
        arrow_icon = _resolve_icon(arrow_name, color=muted, size=12)
        if arrow_icon:
            self.lbl_arrow.setPixmap(arrow_icon.pixmap(12, 12))

        self.lbl_title.setStyleSheet(f"color: {fg}; background: transparent;")
        self.lbl_count.setStyleSheet(f"""
            background-color: {count_bg};
            color: {muted};
            border-radius: 9px;
            padding: 1px 7px;
            font-size: 11px;
        """)

        hover_bg = "rgba(255, 255, 255, 0.04)" if is_dark else "#F8FAFC"
        self.setStyleSheet(f"""
            #MkSelectGroupHeader {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }}
            #MkSelectGroupHeader:hover {{
                background-color: {hover_bg};
            }}
        """)

    def mousePressEvent(self, event):
        self._is_collapsed = not self._is_collapsed
        self._apply_style()
        self.toggled.emit(self._is_collapsed)
        super().mousePressEvent(event)

    def set_count(self, count: Optional[int]):
        self._count = count
        if count is not None:
            self.lbl_count.setText(str(count))
            self.lbl_count.show()
        else:
            self.lbl_count.hide()

    def is_collapsed(self) -> bool:
        return self._is_collapsed


class MkSelectCard(QFrame):
    """
    多选卡片整个组合组件（参考图三现代极简面板，告别经典蓝色）。
    
    集成特性:
        1. 顶部 Header: 左侧图标 + 标题（例如“Models”），右侧简约文本计数（如“1 selected” / “1 已选”）。
        2. 全选控制栏: “Select all” / “全选”现代暗调复选框，自动同步全选、半选三态与全未选。
        3. 分组支持: 可随时添加分组折叠栏 (如 Detect   2)。
        4. 列表滚动容器: 无内层多余边框，纯净平滑滚动。
    
    信号:
        selection_changed(list): 选中的 item_id 列表改变
        item_clicked(item_id): 点击某项
        item_action_clicked(action_key, item_id): 点击某项的操作按钮
        item_detail_clicked(item_id): 点击某项的详情箭头
    """
    selection_changed = Signal(list)
    item_clicked = Signal(object)
    item_navigated = Signal(object)          # 专为“点击进入/跳转指定页面”预留的核心信号！
    item_open_requested = Signal(object)     # 别名信号，兼容进入请求
    item_double_clicked = Signal(object)     # 双击条目事件
    item_action_clicked = Signal(str, object)
    item_detail_clicked = Signal(object)

    def __init__(
        self,
        title: str = "Models",
        icon: Optional[str] = "cube",
        show_select_all: bool = True,
        select_all_text: str = "Select all",
        badge_pattern: str = "{count} selected",
        max_list_height: Optional[int] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setObjectName("MkSelectCard")
        self._title_text = title
        self._icon_name = icon
        self._show_select_all = show_select_all
        self._select_all_text = select_all_text
        self._badge_pattern = badge_pattern
        self._max_list_height = max_list_height

        self._items: List[MkSelectItem] = []
        self._item_map: Dict[Any, MkSelectItem] = {}
        self._groups: Dict[str, MkSelectGroupHeader] = {}
        self._updating_select_all = False

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._init_ui()
        ThemeEngine.instance().themeChanged.connect(self._apply_style)
        self._apply_style()

    def _init_ui(self):
        self._card_layout = QVBoxLayout(self)
        self._card_layout.setContentsMargins(14, 14, 14, 14)
        self._card_layout.setSpacing(10)

        # ── 1. Header 栏 ──
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(8)

        self.lbl_hdr_icon = QLabel(self)
        self.lbl_hdr_icon.setStyleSheet("background: transparent;")
        self.header_layout.addWidget(self.lbl_hdr_icon)

        self.lbl_hdr_title = QLabel(self._title_text, self)
        hdr_font = QFont()
        hdr_font.setPointSize(11)
        hdr_font.setWeight(QFont.Weight.Bold)
        self.lbl_hdr_title.setFont(hdr_font)
        self.lbl_hdr_title.setStyleSheet("background: transparent;")
        self.header_layout.addWidget(self.lbl_hdr_title)

        self.header_layout.addStretch()

        # 右侧简约文本计数（参考图三: "1 selected"，告别蓝色胶囊）
        self.lbl_badge = QLabel(self._badge_pattern.format(count=0), self)
        badge_font = QFont()
        badge_font.setPointSize(9)
        badge_font.setWeight(QFont.Weight.Normal)
        self.lbl_badge.setFont(badge_font)
        self.lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_layout.addWidget(self.lbl_badge)

        self._card_layout.addLayout(self.header_layout)

        # ── 2. 全选 / 取消全选控制栏（现代暗调复选框） ──
        self.chk_all = MkCheckBox(self._select_all_text, self, variant="neutral")
        self.chk_all.setVisible(self._show_select_all)
        self.chk_all.setTristate(True)
        self.chk_all.clicked.connect(self._on_chk_all_clicked)
        self._card_layout.addWidget(self.chk_all)

        # ── 3. 选择项滚动列表区（无多余内外层嵌套卡片边框） ──
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        if self._max_list_height:
            self.scroll_area.setMaximumHeight(self._max_list_height)

        self.list_container = QWidget()
        self.list_container.setObjectName("MkSelectListContainer")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(6)

        # 空状态占位提示
        self.lbl_empty = QLabel("暂无数据项", self.list_container)
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet("color: #71717A; padding: 20px; font-size: 11px;")
        self.list_layout.addWidget(self.lbl_empty)

        self.list_layout.addStretch()
        self.scroll_area.setWidget(self.list_container)
        self._card_layout.addWidget(self.scroll_area, stretch=1)

        # ── 4. 底部扩展插槽 ──
        self.bottom_slot_widget = QWidget(self)
        self.bottom_slot_widget.setStyleSheet("background: transparent;")
        self.bottom_slot_layout = QVBoxLayout(self.bottom_slot_widget)
        self.bottom_slot_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_slot_layout.setSpacing(6)
        self.bottom_slot_widget.hide()
        self._card_layout.addWidget(self.bottom_slot_widget)

    def _apply_style(self, theme_name: str = None):
        t = ThemeEngine
        is_dark = t.is_dark()
        fg = t.get("--fg", "#1E293B")
        border = t.get("--border", "#E2E8F0" if not is_dark else "#27272A")
        muted = t.get("--text-muted", "#71717A" if is_dark else "#64748B")

        # 卡片外框整体样式（参考图三: 优雅柔和的面板背景）
        card_bg = "#121214" if is_dark else "#FAFAFA"
        self.setStyleSheet(f"""
            #MkSelectCard {{
                background-color: {card_bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
            #MkSelectListContainer {{
                background: transparent;
            }}
            QScrollArea {{
                background: transparent;
                border: none;
            }}
        """)

        self.lbl_hdr_title.setStyleSheet(f"color: {fg}; font-weight: 700; background: transparent;")

        if self._icon_name:
            hdr_icon = _resolve_icon(self._icon_name, color=fg, size=18)
            if hdr_icon:
                self.lbl_hdr_icon.setPixmap(hdr_icon.pixmap(18, 18))
                self.lbl_hdr_icon.show()
            else:
                self.lbl_hdr_icon.hide()
        else:
            self.lbl_hdr_icon.hide()

        # 简约文本计数样式（告别经典蓝色胶囊）
        self.lbl_badge.setStyleSheet(f"""
            background: transparent;
            color: {muted};
            font-size: 13px;
            font-weight: 500;
            border: none;
            padding: 0px 4px;
        """)

    def _on_chk_all_clicked(self):
        if self._updating_select_all:
            return
        target_state = self.chk_all.checkState() != Qt.CheckState.Unchecked
        self.select_all(target_state)

    def _on_item_checked(self, item_id: Any, checked: bool):
        self._sync_select_all_and_badge()
        self.selection_changed.emit(self.get_selected_ids())

    def _sync_select_all_and_badge(self):
        total = len(self._items)
        selected_count = sum(1 for item in self._items if item.is_checked())

        self.lbl_badge.setText(self._badge_pattern.format(count=selected_count))

        if total == 0:
            self._updating_select_all = True
            self.chk_all.setCheckState(Qt.CheckState.Unchecked)
            self._updating_select_all = False
            return

        self._updating_select_all = True
        if selected_count == total:
            self.chk_all.setCheckState(Qt.CheckState.Checked)
        elif selected_count == 0:
            self.chk_all.setCheckState(Qt.CheckState.Unchecked)
        else:
            self.chk_all.setCheckState(Qt.CheckState.PartiallyChecked)
        self._updating_select_all = False

    def _sync_group_counts(self):
        """动态同步各个分组下的条目数量徽标"""
        group_counts: Dict[str, int] = {}
        for item in self._items:
            gid = item.group_id
            if gid:
                group_counts[gid] = group_counts.get(gid, 0) + 1

        for gid, header in self._groups.items():
            if getattr(header, "auto_count", True):
                cnt = group_counts.get(gid, 0)
                header.set_count(cnt)

    def get_group_count(self, group_id: str) -> int:
        """获取指定分组下的当前条目数量"""
        return sum(1 for item in self._items if item.group_id == group_id)

    def set_group_count(self, group_id: str, count: Optional[int]):
        """手动设置某个分组的计数值（调用后该分组关闭 auto_count）"""
        hdr = self._groups.get(group_id)
        if hdr:
            hdr.auto_count = False
            hdr.set_count(count)

    def add_group(
        self,
        group_id: str,
        title: str,
        count: Optional[int] = None,
        auto_count: bool = True,
        collapsed: bool = False,
    ) -> MkSelectGroupHeader:
        """
        添加分组折叠标题栏（参考图三: v Detect   3）

        参数:
            group_id: 分组唯一标识
            title: 分组标题文本
            count: 初始计数值。若为 None 且 auto_count 为 True，将自动动态计算该分组项数
            auto_count: 是否随条目添加/删除自动动态计算数量。默认 True
            collapsed: 是否默认折叠
        """
        hdr = MkSelectGroupHeader(
            group_id=group_id,
            title=title,
            count=count,
            collapsed=collapsed,
            auto_count=auto_count,
            parent=self.list_container,
        )
        self._groups[group_id] = hdr
        hdr.toggled.connect(lambda is_coll, gid=group_id: self._on_group_toggled(gid, is_coll))
        self.lbl_empty.hide()
        self.list_layout.insertWidget(self.list_layout.count() - 1, hdr)
        self._sync_group_counts()
        return hdr

    def _on_group_toggled(self, group_id: str, is_collapsed: bool):
        for item in self._items:
            if item.group_id == group_id:
                item.setVisible(not is_collapsed)

    def add_item(self, item: Union[MkSelectItem, Dict[str, Any]]) -> MkSelectItem:
        """向卡片添加项。"""
        if isinstance(item, dict):
            item_widget = MkSelectItem(
                item_id=item.get("id", item.get("item_id")),
                title=item.get("title", ""),
                subtitle=item.get("subtitle", ""),
                dot_color=item.get("dot_color"),
                icon=item.get("icon"),
                selectable=item.get("selectable", True),
                checked=item.get("checked", False),
                actions=item.get("actions", []),
                show_arrow=item.get("show_arrow", False),
                actions_visible_on_hover=item.get("actions_visible_on_hover", True),
                checkable_by_click=item.get("checkable_by_click", False),
                navigate_on_click=item.get("navigate_on_click", True),
                target_page=item.get("target_page"),
                group_id=item.get("group_id"),
                data=item.get("data"),
                parent=self.list_container,
            )
        else:
            item_widget = item
            item_widget.setParent(self.list_container)

        self._items.append(item_widget)
        self._item_map[item_widget.item_id] = item_widget

        item_widget.checked_changed.connect(self._on_item_checked)
        item_widget.clicked.connect(lambda iid: self.item_clicked.emit(iid))
        item_widget.navigated.connect(lambda iid: self.item_navigated.emit(iid))
        item_widget.open_requested.connect(lambda iid: self.item_open_requested.emit(iid))
        item_widget.double_clicked.connect(lambda iid: self.item_double_clicked.emit(iid))
        item_widget.action_clicked.connect(lambda k, iid: self.item_action_clicked.emit(k, iid))
        item_widget.detail_clicked.connect(lambda iid: self.item_detail_clicked.emit(iid))
        item_widget.group_changed.connect(lambda _: self._sync_group_counts())

        self.lbl_empty.hide()
        self.list_layout.insertWidget(self.list_layout.count() - 1, item_widget)

        # 检查是否属于某个已折叠分组
        if item_widget.group_id and item_widget.group_id in self._groups:
            if self._groups[item_widget.group_id].is_collapsed():
                item_widget.hide()

        self._sync_select_all_and_badge()
        self._sync_group_counts()
        return item_widget

    def add_items(self, items: List[Union[MkSelectItem, Dict[str, Any]]]):
        for item in items:
            self.add_item(item)

    def remove_item(self, item_id: Any):
        item = self._item_map.pop(item_id, None)
        if item:
            if item in self._items:
                self._items.remove(item)
            self.list_layout.removeWidget(item)
            item.deleteLater()

            if len(self._items) == 0:
                self.lbl_empty.show()

            self._sync_select_all_and_badge()
            self._sync_group_counts()
            self.selection_changed.emit(self.get_selected_ids())

    def clear_items(self):
        for item in list(self._items):
            self.list_layout.removeWidget(item)
            item.deleteLater()
        self._items.clear()
        self._item_map.clear()
        self.lbl_empty.show()
        self._sync_select_all_and_badge()
        self._sync_group_counts()
        self.selection_changed.emit([])

    def get_item(self, item_id: Any) -> Optional[MkSelectItem]:
        return self._item_map.get(item_id)

    def get_items(self) -> List[MkSelectItem]:
        return list(self._items)

    def get_selected_ids(self) -> List[Any]:
        return [item.item_id for item in self._items if item.is_checked()]

    def get_selected_items(self) -> List[MkSelectItem]:
        return [item for item in self._items if item.is_checked()]

    def set_selected_ids(self, ids: List[Any]):
        id_set = set(ids)
        for item in self._items:
            item.set_checked(item.item_id in id_set, block_signal=True)
        self._sync_select_all_and_badge()
        self.selection_changed.emit(self.get_selected_ids())

    def select_all(self, checked: bool):
        for item in self._items:
            item.set_checked(checked, block_signal=True)
        self._sync_select_all_and_badge()
        self.selection_changed.emit(self.get_selected_ids())

    def set_title(self, title: str):
        self._title_text = title
        self.lbl_hdr_title.setText(title)

    def set_badge_pattern(self, pattern: str):
        self._badge_pattern = pattern
        self._sync_select_all_and_badge()

    def set_bottom_widget(self, widget: Optional[QWidget]):
        while self.bottom_slot_layout.count():
            child = self.bottom_slot_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if widget:
            self.bottom_slot_layout.addWidget(widget)
            self.bottom_slot_widget.show()
        else:
            self.bottom_slot_widget.hide()
