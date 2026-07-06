# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt, Property, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import qcolor


def _parse_padding(padding):
    if isinstance(padding, int):
        return (padding, padding, padding, padding)
    if isinstance(padding, (list, tuple)):
        if len(padding) == 2:
            h, v = padding
            return (h, v, h, v)
        if len(padding) == 4:
            return tuple(padding)
    return (0, 0, 0, 0)


class MkQVBoxLayout(QFrame):
    """
    MkQVBoxLayout - 垂直布局排版箱组件 (相当于前端 Flex 容器 flex-direction: column)
    支持自动填充/自适应大小、外边距(padding)、内间距(spacing/gap)、背景颜色、圆角以及可控制显示/隐藏的边框线。
    """

    def __init__(self, widgets=None, spacing=8, padding=12, border=False, border_width=1, radius=6, bg_color=None, parent=None):
        super().__init__(parent)
        self._padding = padding
        self._border = border
        self._border_width = border_width
        self._radius = radius
        self._bg_color = bg_color

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            {self.__class__.__name__} {{
                background: transparent;
                border: none;
            }}
        """)
        
        # 核心排版引擎
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(spacing)
        
        margins = _parse_padding(padding)
        self._layout.setContentsMargins(*margins)

        if widgets:
            for w in widgets:
                if isinstance(w, QWidget):
                    self.addWidget(w)

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)

    def set_theme_style(self, style_name: str = None):
        self.update()

    def paintEvent(self, event):
        if not self._border and not self._bg_color:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        border_w = self._border_width if self._border else 0
        half_w = border_w / 2.0
        inset = rect.adjusted(half_w, half_w, -half_w, -half_w)
        
        t = ThemeEngine
        
        # 背景底色适配
        if self._bg_color:
            if self._bg_color == "surface":
                bg = qcolor(t.get("--surface", "#FFFFFF"))
            elif self._bg_color == "bg":
                bg = qcolor(t.get("--bg", "#FFFFFF"))
            else:
                bg = qcolor(self._bg_color)
        else:
            bg = QColor(Qt.GlobalColor.transparent)
            
        painter.setBrush(QBrush(bg))
        
        # 边框线适配
        if self._border:
            if isinstance(self._border, str) and self._border.lower() not in ("true", "1"):
                border_color = qcolor(self._border)
            else:
                border_color = qcolor(t.get("--border", "#E2E8F0"))
            painter.setPen(QPen(border_color, self._border_width))
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            
        radius = self._radius
        painter.drawRoundedRect(inset, radius, radius)
        painter.end()

    # ──────────── 常用布局方法代理 ────────────

    def addWidget(self, widget, stretch=0, alignment=Qt.AlignmentFlag(0)):
        self._layout.addWidget(widget, stretch, alignment)

    def addLayout(self, layout, stretch=0):
        self._layout.addLayout(layout, stretch)

    def addSpacing(self, size):
        self._layout.addSpacing(size)

    def addStretch(self, stretch=0):
        self._layout.addStretch(stretch)

    def insertWidget(self, index, widget, stretch=0, alignment=Qt.AlignmentFlag(0)):
        self._layout.insertWidget(index, widget, stretch, alignment)

    def insertLayout(self, index, layout, stretch=0):
        self._layout.insertLayout(index, layout, stretch)

    def insertSpacing(self, index, size):
        self._layout.insertSpacing(index, size)

    def insertStretch(self, index, stretch=0):
        self._layout.insertStretch(index, stretch)

    def removeWidget(self, widget):
        self._layout.removeWidget(widget)

    def count(self):
        return self._layout.count()

    def itemAt(self, index):
        return self._layout.itemAt(index)

    def takeAt(self, index):
        return self._layout.takeAt(index)

    def clear(self):
        def _clear_layout(layout):
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    _clear_layout(child.layout())
                    child.layout().deleteLater()
        _clear_layout(self._layout)

    # ──────────── 动态属性 Getter / Setter ────────────

    @Property(int)
    def spacing(self):
        return self._layout.spacing()

    @spacing.setter
    def spacing(self, val):
        self._layout.setSpacing(val)

    @Property(object)
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, val):
        self._padding = val
        margins = _parse_padding(val)
        self._layout.setContentsMargins(*margins)

    @Property(object)
    def border(self):
        return self._border

    @border.setter
    def border(self, val):
        self._border = val
        self.update()

    @Property(int)
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, val):
        self._radius = val
        self.update()

    @Property(str)
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, val):
        self._bg_color = val
        self.update()

    @Property(int)
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, val):
        self._border_width = int(val)
        self.update()


class MkQHBoxLayout(QFrame):
    """
    MkQHBoxLayout - 水平布局排版箱组件 (相当于前端 Flex 容器 flex-direction: row)
    支持自动填充/自适应大小、外边距(padding)、内间距(spacing/gap)、背景颜色、圆角以及可控制显示/隐藏的边框线。
    """

    def __init__(self, widgets=None, spacing=8, padding=12, border=False, border_width=1, radius=6, bg_color=None, parent=None):
        super().__init__(parent)
        self._padding = padding
        self._border = border
        self._border_width = border_width
        self._radius = radius
        self._bg_color = bg_color

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            {self.__class__.__name__} {{
                background: transparent;
                border: none;
            }}
        """)
        
        # 核心排版引擎
        self._layout = QHBoxLayout(self)
        self._layout.setSpacing(spacing)
        
        margins = _parse_padding(padding)
        self._layout.setContentsMargins(*margins)

        if widgets:
            for w in widgets:
                if isinstance(w, QWidget):
                    self.addWidget(w)

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)

    def set_theme_style(self, style_name: str = None):
        self.update()

    def paintEvent(self, event):
        if not self._border and not self._bg_color:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        border_w = self._border_width if self._border else 0
        half_w = border_w / 2.0
        inset = rect.adjusted(half_w, half_w, -half_w, -half_w)
        
        t = ThemeEngine
        
        # 背景底色适配
        if self._bg_color:
            if self._bg_color == "surface":
                bg = qcolor(t.get("--surface", "#FFFFFF"))
            elif self._bg_color == "bg":
                bg = qcolor(t.get("--bg", "#FFFFFF"))
            else:
                bg = qcolor(self._bg_color)
        else:
            bg = QColor(Qt.GlobalColor.transparent)
            
        painter.setBrush(QBrush(bg))
        
        # 边框线适配
        if self._border:
            if isinstance(self._border, str) and self._border.lower() not in ("true", "1"):
                border_color = qcolor(self._border)
            else:
                border_color = qcolor(t.get("--border", "#E2E8F0"))
            painter.setPen(QPen(border_color, self._border_width))
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            
        radius = self._radius
        painter.drawRoundedRect(inset, radius, radius)
        painter.end()

    # ──────────── 常用布局方法代理 ────────────

    def addWidget(self, widget, stretch=0, alignment=Qt.AlignmentFlag(0)):
        self._layout.addWidget(widget, stretch, alignment)

    def addLayout(self, layout, stretch=0):
        self._layout.addLayout(layout, stretch)

    def addSpacing(self, size):
        self._layout.addSpacing(size)

    def addStretch(self, stretch=0):
        self._layout.addStretch(stretch)

    def insertWidget(self, index, widget, stretch=0, alignment=Qt.AlignmentFlag(0)):
        self._layout.insertWidget(index, widget, stretch, alignment)

    def insertLayout(self, index, layout, stretch=0):
        self._layout.insertLayout(index, layout, stretch)

    def insertSpacing(self, index, size):
        self._layout.insertSpacing(index, size)

    def insertStretch(self, index, stretch=0):
        self._layout.insertStretch(index, stretch)

    def removeWidget(self, widget):
        self._layout.removeWidget(widget)

    def count(self):
        return self._layout.count()

    def itemAt(self, index):
        return self._layout.itemAt(index)

    def takeAt(self, index):
        return self._layout.takeAt(index)

    def clear(self):
        def _clear_layout(layout):
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    _clear_layout(child.layout())
                    child.layout().deleteLater()
        _clear_layout(self._layout)

    # ──────────── 动态属性 Getter / Setter ────────────

    @Property(int)
    def spacing(self):
        return self._layout.spacing()

    @spacing.setter
    def spacing(self, val):
        self._layout.setSpacing(val)

    @Property(object)
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, val):
        self._padding = val
        margins = _parse_padding(val)
        self._layout.setContentsMargins(*margins)

    @Property(object)
    def border(self):
        return self._border

    @border.setter
    def border(self, val):
        self._border = val
        self.update()

    @Property(int)
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, val):
        self._radius = val
        self.update()

    @Property(str)
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, val):
        self._bg_color = val
        self.update()

    @Property(int)
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, val):
        self._border_width = int(val)
        self.update()


# 便捷别名
MkVBox = MkQVBoxLayout
MkHBox = MkQHBoxLayout
