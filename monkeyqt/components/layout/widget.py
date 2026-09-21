# -*- coding: utf-8 -*-
"""
MkQWidget / MkWidget: High-usability, theme-adaptive base widget for MonkeyQt.
Eliminates Qt QWidget styling boilerplate and repetitive layout code.
"""

from typing import Union, Tuple, Optional, Sequence
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLayout,
    QStyleOption,
    QStylePainter,
    QStyle
)

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import qcolor, parse_px


def _parse_margins(margins: Union[int, Sequence[int], None]) -> Tuple[int, int, int, int]:
    """Parse integer, 2-tuple (h, v), or 4-tuple (l, t, r, b) into 4 margins."""
    if margins is None:
        return (0, 0, 0, 0)
    if isinstance(margins, int):
        return (margins, margins, margins, margins)
    if isinstance(margins, (list, tuple)):
        if len(margins) == 2:
            h, v = margins
            return (h, v, h, v)
        elif len(margins) == 4:
            return (int(margins[0]), int(margins[1]), int(margins[2]), int(margins[3]))
    return (0, 0, 0, 0)


class MkQWidget(QWidget):
    """
    MkQWidget (别名 MkWidget) - MonkeyQt 高可用、多布局、自适应主题基础组件容器。

    主要特性:
    1. 【内置弹性布局引擎】：
       可直接传入 layout="v"|"h"|"grid"，并配置 margins 与 spacing，
       提供 add_widget()、add_layout()、add_stretch() 等链式/便捷操作。
    2. 【语义化主题角色 (Role)】：
       支持 role="transparent" | "surface" | "bg" | "card" | "muted"，
       无须写任何 QSS 即可自动适配 MonkeyQt 的 68 种主题风格与暗色模式。
    3. 【解决原生 QWidget 样式痛点】：
       原生 QWidget 默认不支持圆角和背景绘制，MkQWidget 内置 WA_StyledBackground 与
       标准 paintEvent 渲染引擎，保证背景、边框、圆角完美呈现且边缘平滑抗锯齿。
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        layout: Optional[Union[str, QLayout]] = None,
        margins: Optional[Union[int, Sequence[int]]] = None,
        spacing: Optional[int] = None,
        role: str = "transparent",
        bg_color: Optional[str] = None,
        border: Union[bool, str, int] = False,
        border_width: int = 1,
        border_color: Optional[str] = None,
        radius: int = 0,
        scrollable: bool = False,
        scroll_direction: str = "v",
        **kwargs
    ):
        # 兼容原生 QWidget(parent, flags) 构造调用规范
        if isinstance(layout, (Qt.WindowType, Qt.WindowFlags, int)):
            flags = Qt.WindowFlags(layout)
            layout = None
            super().__init__(parent, flags, **kwargs)
        else:
            super().__init__(parent, **kwargs)

        self._role = (role or "transparent").lower().strip()
        self._custom_bg_color = bg_color
        self._custom_border = border
        self._border_width = border_width
        self._custom_border_color = border_color
        self._radius = radius
        self._scrollable = bool(scrollable)
        self._scroll_direction = (scroll_direction or "v").lower().strip()
        self._scroll_area = None
        self._scroll_content = None

        # 确保支持 QSS 样式表背景绘制
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # 若开启了自适应滚动条模式，初始化内部现代贴边滚动容器
        if self._scrollable:
            from monkeyqt.components.layout.scroll_area import MkScrollArea
            self._scroll_area = MkScrollArea(
                self,
                horizontal=(self._scroll_direction in ("h", "both", "all", "horizontal"))
            )
            self._scroll_area.setObjectName("MkWidgetScrollArea")
            self._root_layout = QVBoxLayout(self)
            self._root_layout.setContentsMargins(0, 0, 0, 0)
            self._root_layout.setSpacing(0)
            self._root_layout.addWidget(self._scroll_area)

            self._scroll_content = QWidget()
            self._scroll_content.setObjectName("MkWidgetScrollContent")
            self._scroll_content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self._scroll_content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            self._scroll_area.setWidget(self._scroll_content)

        # 初始化排版布局
        self._inner_layout: Optional[QLayout] = None
        if layout:
            self._setup_layout(layout, margins, spacing)

        # 监听主题变更自动刷新重绘
        try:
            ThemeEngine.instance().themeChanged.connect(self._on_theme_changed)
        except Exception:
            pass

    # ----------------------------------------------------------------------
    # 布局管理快捷方法
    # ----------------------------------------------------------------------
    def _setup_layout(
        self,
        layout_spec: Union[str, QLayout],
        margins: Optional[Union[int, Sequence[int]]] = None,
        spacing: Optional[int] = None
    ) -> QLayout:
        """根据简写配置创建并绑定内部布局"""
        target = self._scroll_content if (self._scrollable and self._scroll_content is not None) else self
        if isinstance(layout_spec, QLayout):
            self._inner_layout = layout_spec
            target.setLayout(layout_spec)
        elif isinstance(layout_spec, str):
            ltype = layout_spec.lower().strip()
            if ltype in ("v", "vbox", "vertical", "col", "column"):
                self._inner_layout = QVBoxLayout(target)
            elif ltype in ("h", "hbox", "horizontal", "row"):
                self._inner_layout = QHBoxLayout(target)
            elif ltype in ("grid", "g"):
                self._inner_layout = QGridLayout(target)
            else:
                self._inner_layout = QVBoxLayout(target)

        if margins is not None and self._inner_layout:
            l, t, r, b = _parse_margins(margins)
            self._inner_layout.setContentsMargins(l, t, r, b)

        if spacing is not None and self._inner_layout:
            self._inner_layout.setSpacing(spacing)

        return self._inner_layout

    @property
    def inner_layout(self) -> Optional[QLayout]:
        """获取当前绑定的主布局对象"""
        if self._inner_layout is not None:
            return self._inner_layout
        if self._scrollable and self._scroll_content is not None:
            return self._scroll_content.layout()
        return self.layout()

    @inner_layout.setter
    def inner_layout(self, val: Optional[QLayout]):
        self._inner_layout = val

    def is_scrollable(self) -> bool:
        """判断当前部件是否配置为带滚动条的页面容器"""
        return self._scrollable

    def get_scroll_area(self):
        """获取内部的 MkScrollArea 实例（若开启了 scrollable）"""
        return self._scroll_area

    def scroll_to_top(self):
        """平滑滚动至最顶部"""
        if self._scroll_area:
            self._scroll_area.scroll_to_top()

    def scroll_to_bottom(self):
        """平滑滚动至最底部"""
        if self._scroll_area:
            self._scroll_area.scroll_to_bottom()

    def scroll_to_widget(self, target: QWidget, x_margin: int = 0, y_margin: int = 0):
        """确保目标子部件处于可视区域内"""
        if self._scroll_area:
            self._scroll_area.scroll_to_widget(target, x_margin, y_margin)

    def add_widget(self, widget: QWidget, stretch: int = 0, alignment: Qt.AlignmentFlag = Qt.AlignmentFlag(0)) -> "MkQWidget":
        """向当前布局添加子控件"""
        # 如果当前处于网页式自适应滚动模式，且子控件为支持 auto_height 的数据表格，自动激活展开模式
        if self._scrollable and hasattr(widget, "set_auto_height"):
            try:
                widget.set_auto_height(True)
            except Exception:
                pass

        lay = self.inner_layout
        if lay is None:
            lay = self._setup_layout("v")

        if isinstance(lay, (QVBoxLayout, QHBoxLayout)):
            lay.addWidget(widget, stretch, alignment)
        elif isinstance(lay, QGridLayout):
            row = lay.rowCount()
            lay.addWidget(widget, row, 0, alignment)
        else:
            lay.addWidget(widget)
        return self

    def add_layout(self, layout: QLayout, stretch: int = 0) -> "MkQWidget":
        """向当前布局添加嵌套子布局"""
        lay = self.inner_layout
        if lay is None:
            lay = self._setup_layout("v")

        if isinstance(lay, (QVBoxLayout, QHBoxLayout)):
            lay.addLayout(layout, stretch)
        elif isinstance(lay, QGridLayout):
            row = lay.rowCount()
            lay.addLayout(layout, row, 0)
        return self

    def add_stretch(self, stretch: int = 0) -> "MkQWidget":
        """添加弹性伸缩占位空间"""
        lay = self.inner_layout
        if isinstance(lay, (QVBoxLayout, QHBoxLayout)):
            lay.addStretch(stretch)
        return self

    def add_spacing(self, spacing: int) -> "MkQWidget":
        """添加固定像素间距"""
        lay = self.inner_layout
        if isinstance(lay, (QVBoxLayout, QHBoxLayout)):
            lay.addSpacing(spacing)
        return self

    def set_margins(self, *margins: Union[int, Sequence[int]]) -> "MkQWidget":
        """
        设置外边距，支持 set_margins(10) 或 set_margins(10, 20) 或 set_margins(10, 5, 10, 5)
        """
        lay = self.inner_layout
        if lay:
            if len(margins) == 1:
                parsed = _parse_margins(margins[0])
            elif len(margins) == 2:
                parsed = (int(margins[0]), int(margins[1]), int(margins[0]), int(margins[1]))
            elif len(margins) == 4:
                parsed = (int(margins[0]), int(margins[1]), int(margins[2]), int(margins[3]))
            else:
                parsed = (0, 0, 0, 0)
            lay.setContentsMargins(*parsed)
        return self

    def set_spacing(self, spacing: int) -> "MkQWidget":
        """设置布局内元素间距"""
        lay = self.inner_layout
        if lay:
            lay.setSpacing(spacing)
        return self

    def clear_layout(self) -> "MkQWidget":
        """安全清空布局中的所有子部件"""
        lay = self.inner_layout
        if not lay:
            return self
        while lay.count():
            item = lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
            elif item.layout() is not None:
                # 递归清空
                sub_lay = item.layout()
                while sub_lay.count():
                    sub_item = sub_lay.takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().setParent(None)
                        sub_item.widget().deleteLater()
        return self

    # ----------------------------------------------------------------------
    # 主题角色与视觉属性
    # ----------------------------------------------------------------------
    def set_role(self, role: str) -> "MkQWidget":
        """设置语义化角色: transparent | surface | bg | card | muted"""
        self._role = (role or "transparent").lower().strip()
        self.update()
        return self

    def get_role(self) -> str:
        return self._role

    def set_bg_color(self, color: Optional[str]) -> "MkQWidget":
        """设置自定义背景色 (支持 hex、颜色名或主题令牌如 '--surface')"""
        self._custom_bg_color = color
        self.update()
        return self

    def set_radius(self, radius: int) -> "MkQWidget":
        """设置组件圆角弧度"""
        self._radius = radius
        self.update()
        return self

    def set_border(
        self,
        border: Union[bool, str, int] = True,
        width: int = 1,
        color: Optional[str] = None
    ) -> "MkQWidget":
        """设置边框样式"""
        self._custom_border = border
        self._border_width = width
        if color:
            self._custom_border_color = color
        self.update()
        return self

    def with_role(self, role: str) -> "MkQWidget":
        return self.set_role(role)

    def with_radius(self, radius: int) -> "MkQWidget":
        return self.set_radius(radius)

    def with_margins(self, *margins) -> "MkQWidget":
        return self.set_margins(*margins)

    def with_spacing(self, spacing: int) -> "MkQWidget":
        return self.set_spacing(spacing)

    # ----------------------------------------------------------------------
    # 类工厂方法 (极简流式构造)
    # ----------------------------------------------------------------------
    @classmethod
    def vbox(
        cls,
        *widgets: QWidget,
        spacing: int = 8,
        margins: Union[int, Sequence[int]] = 0,
        role: str = "transparent",
        parent: Optional[QWidget] = None,
        **kwargs
    ) -> "MkQWidget":
        """快速构建垂直列容器 (VBox)"""
        inst = cls(parent=parent, layout="v", margins=margins, spacing=spacing, role=role, **kwargs)
        for w in widgets:
            if isinstance(w, QWidget):
                inst.add_widget(w)
        return inst

    @classmethod
    def hbox(
        cls,
        *widgets: QWidget,
        spacing: int = 8,
        margins: Union[int, Sequence[int]] = 0,
        role: str = "transparent",
        parent: Optional[QWidget] = None,
        **kwargs
    ) -> "MkQWidget":
        """快速构建水平行容器 (HBox)"""
        inst = cls(parent=parent, layout="h", margins=margins, spacing=spacing, role=role, **kwargs)
        for w in widgets:
            if isinstance(w, QWidget):
                inst.add_widget(w)
        return inst

    @classmethod
    def card(
        cls,
        *widgets: QWidget,
        spacing: int = 12,
        padding: Union[int, Sequence[int]] = 16,
        radius: int = 10,
        parent: Optional[QWidget] = None,
        **kwargs
    ) -> "MkQWidget":
        """快速构建风格化卡片容器 (Card)"""
        inst = cls(
            parent=parent,
            layout="v",
            margins=padding,
            spacing=spacing,
            role="card",
            radius=radius,
            border=True,
            **kwargs
        )
        for w in widgets:
            if isinstance(w, QWidget):
                inst.add_widget(w)
        return inst

    # ----------------------------------------------------------------------
    # 主题快捷助手与生命周期钩子
    # ----------------------------------------------------------------------
    @property
    def is_dark(self) -> bool:
        """检查当前主题是否为暗色模式"""
        if hasattr(self, "_is_dark_override") and self._is_dark_override is not None:
            return self._is_dark_override
        try:
            return ThemeEngine.is_dark()
        except Exception:
            return False

    @is_dark.setter
    def is_dark(self, value: Optional[bool]):
        self._is_dark_override = bool(value) if value is not None else None


    @property
    def tokens(self) -> dict:
        """获取当前激活主题的所有颜色与几何令牌"""
        try:
            return ThemeEngine.current_tokens()
        except Exception:
            return {}

    def token(self, key: str, default: str = "") -> str:
        """安全读取主题令牌值，例如 self.token('--surface')"""
        try:
            return ThemeEngine.get(key, default)
        except Exception:
            return default

    def on_theme_changed(self, theme_name: str = ""):
        """子类生命周期钩子：当全局主题变更时被自动调用。子类可直接重写此方法。"""
        pass

    def _on_theme_changed(self, theme_name: str = ""):
        try:
            self.on_theme_changed(theme_name)
        except Exception:
            pass
        self.update()

    def paintEvent(self, event):
        """
        绘制事件：
        - 若 role 为 'transparent' 且无自定义背景/边框，则交由标准 QStyle 绘制 (允许外层 QSS 正常生效)。
        - 若配置了 role (surface/bg/card/muted) 或自定义背景/边框/圆角，则使用抗锯齿高保真重绘。
        """
        has_custom_bg = bool(self._custom_bg_color)
        has_custom_border = bool(self._custom_border)
        is_semantic_role = self._role in ("surface", "bg", "background", "card", "muted")

        if not is_semantic_role and not has_custom_bg and not has_custom_border and self._radius == 0:
            # 标准 QStyle 绘制通道
            opt = QStyleOption()
            opt.initFrom(self)
            painter = QStylePainter(self)
            painter.drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect())

        # 1. 计算背景颜色
        t = ThemeEngine
        bg_qcolor = QColor(Qt.GlobalColor.transparent)

        if self._custom_bg_color:
            if self._custom_bg_color.startswith("--"):
                bg_qcolor = qcolor(t.get(self._custom_bg_color, "transparent"))
            elif self._custom_bg_color == "surface":
                bg_qcolor = qcolor(t.get("--surface", "#FFFFFF"))
            elif self._custom_bg_color in ("bg", "background"):
                bg_qcolor = qcolor(t.get("--bg", "#F8FAFC"))
            else:
                bg_qcolor = qcolor(self._custom_bg_color)
        elif is_semantic_role:
            if self._role in ("surface", "card"):
                bg_qcolor = qcolor(t.get("--surface", "#FFFFFF"))
            elif self._role in ("bg", "background"):
                bg_qcolor = qcolor(t.get("--bg", "#F8FAFC"))
            elif self._role == "muted":
                bg_qcolor = qcolor(t.get("--surface-variant", t.get("--bg", "#F1F5F9")))

        # 2. 计算边框颜色与粗细
        draw_border = False
        border_w = float(self._border_width)
        border_qcolor = QColor(Qt.GlobalColor.transparent)

        if self._custom_border:
            draw_border = True
            if self._custom_border_color:
                border_qcolor = qcolor(self._custom_border_color)
            elif isinstance(self._custom_border, str) and self._custom_border not in ("true", "1"):
                border_qcolor = qcolor(self._custom_border)
            else:
                border_qcolor = qcolor(t.get("--border", "#E2E8F0"))
        elif self._role == "card":
            # 卡片默认带边框
            draw_border = True
            border_qcolor = qcolor(t.get("--border", "#E2E8F0"))

        # 3. 计算圆角弧度
        radius = float(self._radius)
        if radius == 0 and self._role == "card":
            radius = float(parse_px(t.get("--radius", "8px"), 8))

        # 4. 执行抗锯齿绘制
        if draw_border and border_w > 0:
            half_w = border_w / 2.0
            inset = rect.adjusted(half_w, half_w, -half_w, -half_w)
            painter.setPen(QPen(border_qcolor, border_w))
        else:
            inset = rect
            painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(bg_qcolor))

        if radius > 0:
            painter.drawRoundedRect(inset, radius, radius)
        else:
            painter.drawRect(inset)

        painter.end()


# 友好别名导出
MkWidget = MkQWidget
