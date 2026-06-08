# -*- coding: utf-8 -*-
"""
ThemedCard — 支持 67 种 UI 风格的卡片容器组件
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsBlurEffect
from PySide6.QtCore import Qt, Property
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont, QLinearGradient
from ..engine import ThemeEngine
from ..style_utils import draw_liquid_glass, parse_px, qcolor


class ThemedCard(QFrame):
    """
    风格化卡片容器。

    用法:
        card = ThemedCard(title="Settings", parent=self)
        card_layout = card.content_layout  # 在此添加子组件
    """

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self._title = title
        self._hovered = False
        self._time_angle = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumSize(200, 120)

        # 内部布局
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(8)

        # 标题
        self._title_label = QLabel(title)
        self._title_label.setStyleSheet("background: transparent;")
        font = QFont("Segoe UI", 13, QFont.Weight.DemiBold)
        self._title_label.setFont(font)
        if title:
            self._layout.addWidget(self._title_label)

        # 内容区域（用户可往此添加子组件）
        self._content_widget = QFrame()
        self._content_widget.setStyleSheet("background: transparent; border: none;")
        self.content_layout = QVBoxLayout(self._content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(6)
        self._layout.addWidget(self._content_widget)

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self._update_style()

    def _update_style(self):
        t = ThemeEngine

        # 如果是流态玻璃，启动动画定时器以触发重绘
        if t.is_liquid_glass():
            if not hasattr(self, "_liquid_timer"):
                from PySide6.QtCore import QTimer
                self._liquid_timer = QTimer(self)
                self._liquid_timer.timeout.connect(self._on_liquid_timeout)
            if not self._liquid_timer.isActive():
                self._liquid_timer.start(33)  # 30 fps
        else:
            if hasattr(self, "_liquid_timer") and self._liquid_timer.isActive():
                self._liquid_timer.stop()

        fg = t.get("--fg", "#1E293B")

        # 标题颜色
        if t.is_dark():
            self._title_label.setStyleSheet(f"background: transparent; color: #FFFFFF;")
        elif t.is_brutal():
            self._title_label.setStyleSheet(f"background: transparent; color: #000000; font-weight: 900;")
        else:
            self._title_label.setStyleSheet(f"background: transparent; color: {fg};")

        # 对于复杂风格使用 paintEvent
        if t.is_neumorphic() or t.is_glass() or t.is_brutal() or t.is_glow() or t.is_pixel():
            self.setStyleSheet("QFrame { background: transparent; border: none; }")
            return

        # 标准 QSS
        bg = t.get("--bg", "#FFFFFF")
        border = t.get("--border", "#E2E8F0")
        radius = t.get("--radius", "6px")
        border_w = t.get("--border-width", "1px")

        card_bg = bg if not t.is_dark() else t._lighten_hex(bg, 0.06)

        self.setStyleSheet(f"""
            ThemedCard {{
                background-color: {card_bg};
                border: {border_w} solid {border};
                border-radius: {radius};
            }}
            ThemedCard:hover {{
                border-color: {t._lighten_hex(t.get('--primary', '#409EFF'), 0.3)};
            }}
        """)

    def paintEvent(self, event):
        t = ThemeEngine

        if not (t.is_neumorphic() or t.is_glass() or t.is_brutal() or t.is_glow() or t.is_pixel()):
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        primary = t.get("--primary", "#409EFF")
        bg = t.get("--bg", "#FFFFFF")
        r_str = t.get("--radius", "6px")
        radius = parse_px(r_str, 6, 0, 36)

        if t.is_neumorphic():
            inset = rect.adjusted(6, 6, -6, -6)
            # 凸起效果
            painter.setPen(Qt.PenStyle.NoPen)
            # 暗阴影
            painter.setBrush(QBrush(QColor(0, 0, 0, 25)))
            painter.drawRoundedRect(inset.translated(4, 4), radius, radius)
            # 亮阴影
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.drawRoundedRect(inset.translated(-3, -3), radius, radius)
            # 主体
            bg_color = QColor(bg) if bg.startswith("#") else QColor("#E8E8E8")
            painter.setBrush(QBrush(bg_color))
            painter.drawRoundedRect(inset, radius, radius)

        elif t.is_glass():
            inset = rect.adjusted(3, 3, -3, -3)
            if t.is_liquid_glass():
                angle = getattr(self, "_time_angle", 0.0)
                draw_liquid_glass(
                    painter,
                    inset,
                    max(radius, 18),
                    primary,
                    dark=t.is_dark(),
                    hovered=self._hovered,
                    angle=angle,
                    intensity=1.2,
                )
            else:
                # 毛玻璃
                if t.is_dark():
                    glass = QColor(255, 255, 255, 20)
                else:
                    glass = QColor(255, 255, 255, 50)
                painter.setPen(QPen(qcolor(t.get("--glass-border", "rgba(255, 255, 255, 100)")), 1))
                painter.setBrush(QBrush(glass))
                painter.drawRoundedRect(inset, radius, radius)
                # 顶部高光线
                painter.setPen(QPen(QColor(255, 255, 255, 60), 1))
                painter.drawLine(inset.left() + radius, inset.top(),
                               inset.right() - radius, inset.top())

        elif t.is_brutal():
            inset = rect.adjusted(4, 4, -8, -8)
            # 硬偏移阴影
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#000000")))
            painter.drawRect(inset.translated(4, 4))
            # 白色主体
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(inset)

        elif t.is_glow():
            inset = rect.adjusted(5, 5, -5, -5)
            glow_color = QColor(primary)
            # 外发光
            for i in range(3, 0, -1):
                gc = QColor(glow_color)
                gc.setAlphaF(0.06 * i)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(gc))
                painter.drawRoundedRect(inset.adjusted(-i*3, -i*3, i*3, i*3), radius, radius)
            # 主体
            card_bg = QColor(20, 20, 30) if t.is_dark() else QColor(bg)
            painter.setBrush(QBrush(card_bg))
            painter.setPen(QPen(QColor(primary), 1))
            painter.drawRoundedRect(inset, radius, radius)

        elif t.is_pixel():
            inset = rect.adjusted(3, 3, -6, -6)
            # 像素阴影
            pixel = 3
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#000000")))
            for x in range(inset.left() + pixel, inset.right() + pixel, pixel):
                painter.drawRect(x, inset.bottom(), pixel, pixel)
            for y in range(inset.top() + pixel, inset.bottom() + pixel, pixel):
                painter.drawRect(inset.right(), y, pixel, pixel)
            # 主体
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(inset)

        painter.end()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def _on_liquid_timeout(self):
        import math
        self._time_angle += 0.04
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()

    def set_theme_style(self, style_name: str = None):
        self._update_style()
        self.update()

    @Property(str)
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self._title_label.setText(value)
        self._title_label.setVisible(bool(value))
