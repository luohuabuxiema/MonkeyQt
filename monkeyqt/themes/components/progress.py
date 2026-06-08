# -*- coding: utf-8 -*-
"""
ThemedProgressBar — 支持 67 种 UI 风格的进度条组件
"""

from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, Property, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient
from ..engine import ThemeEngine
from ..style_utils import draw_liquid_glass, parse_px, qcolor


class ThemedProgressBar(QWidget):
    """
    风格化进度条组件。

    用法:
        bar = ThemedProgressBar(percentage=75)
    """

    def __init__(self, percentage=0, show_text=True, parent=None):
        super().__init__(parent)
        self._percentage = max(0, min(100, percentage))
        self._show_text = show_text
        self._time_angle = 0.0

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(28)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        bg = t.get("--bg", "#FFFFFF")
        fg = t.get("--fg", "#1E293B")
        r_str = t.get("--radius", "6px")
        radius = parse_px(r_str, 6, 0, 24)
        bar_radius = min(radius, 8)

        w = self.width()
        h = self.height()
        stroke = 8
        text = f"{self._percentage}%"
        font = self.font()
        font.setPixelSize(12)
        painter.setFont(font)
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(text)

        track_w = w - text_width - 12 if self._show_text else w
        track_y = (h - stroke) / 2
        fg_width = track_w * (self._percentage / 100.0) if self._percentage > 0 else 0

        if t.is_neumorphic():
            # 凹陷轨道
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 15)))
            painter.drawRoundedRect(QRectF(1, track_y + 1, track_w, stroke), stroke/2, stroke/2)
            painter.setBrush(QBrush(QColor(255, 255, 255, 120)))
            painter.drawRoundedRect(QRectF(-1, track_y - 1, track_w, stroke), stroke/2, stroke/2)
            track_bg = QColor(bg).darker(108) if bg.startswith("#") else QColor("#D0D0D0")
            painter.setBrush(QBrush(track_bg))
            painter.drawRoundedRect(QRectF(0, track_y, track_w, stroke), stroke/2, stroke/2)
            # 进度条
            if fg_width > 0:
                painter.setBrush(QBrush(QColor(primary)))
                painter.drawRoundedRect(QRectF(0, track_y, fg_width, stroke), stroke/2, stroke/2)

        elif t.is_brutal():
            # 方形轨道
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.setBrush(QBrush(QColor("#E0E0E0")))
            painter.drawRect(QRectF(0, track_y, track_w, stroke))
            if fg_width > 0:
                painter.setBrush(QBrush(QColor(primary)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(QRectF(1, track_y + 1, fg_width - 2, stroke - 2))

        elif t.is_glow():
            # 暗底发光
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(30, 30, 40)))
            painter.drawRoundedRect(QRectF(0, track_y, track_w, stroke), stroke/2, stroke/2)
            if fg_width > 0:
                # 发光进度
                glow = QColor(primary)
                glow.setAlphaF(0.3)
                painter.setBrush(QBrush(glow))
                painter.drawRoundedRect(QRectF(-2, track_y - 2, fg_width + 4, stroke + 4), stroke/2 + 2, stroke/2 + 2)
                painter.setBrush(QBrush(QColor(primary)))
                painter.drawRoundedRect(QRectF(0, track_y, fg_width, stroke), stroke/2, stroke/2)

        elif t.is_glass():
            track_rect = QRectF(0, track_y - 2, track_w, stroke + 4)
            if t.is_liquid_glass():
                draw_liquid_glass(
                    painter,
                    track_rect,
                    int(stroke),
                    primary,
                    dark=t.is_dark(),
                    hovered=True,
                    angle=getattr(self, "_time_angle", 0.0),
                    intensity=0.36,
                )
            else:
                # 透明轨道
                glass_bg = QColor(255, 255, 255, 25) if t.is_dark() else QColor(0, 0, 0, 15)
                painter.setPen(QPen(qcolor(t.get("--glass-border", "rgba(255, 255, 255, 60)")), 1))
                painter.setBrush(QBrush(glass_bg))
                painter.drawRoundedRect(QRectF(0, track_y, track_w, stroke), stroke/2, stroke/2)
            if fg_width > 0:
                fg_color = qcolor(primary)
                fg_color.setAlphaF(0.70 if not t.is_liquid_glass() else 0.86)
                painter.setPen(Qt.PenStyle.NoPen)
                if t.is_liquid_glass():
                    fill_grad = QLinearGradient(0, track_y, max(fg_width, 1), track_y)
                    fill_grad.setColorAt(0.0, fg_color.lighter(130))
                    fill_grad.setColorAt(0.55, fg_color)
                    fill_grad.setColorAt(1.0, QColor(255, 255, 255, 170))
                    painter.setBrush(QBrush(fill_grad))
                else:
                    painter.setBrush(QBrush(fg_color))
                painter.drawRoundedRect(QRectF(0, track_y, fg_width, stroke), stroke/2, stroke/2)

        elif t.is_pixel():
            pixel = 3
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.setBrush(QBrush(QColor("#E0E0E0")))
            painter.drawRect(QRectF(0, track_y, track_w, stroke))
            if fg_width > 0:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(primary)))
                # 像素化填充
                for x in range(0, int(fg_width), pixel):
                    pw = min(pixel, int(fg_width) - x)
                    painter.drawRect(x + 1, int(track_y) + 1, pw, int(stroke) - 2)

        else:
            # 默认圆润风格
            bg_track = QColor("#EBEEF5") if not t.is_dark() else QColor("#333333")
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bg_track))
            painter.drawRoundedRect(QRectF(0, track_y, track_w, stroke), stroke/2, stroke/2)
            if fg_width > 0:
                painter.setBrush(QBrush(QColor(primary)))
                painter.drawRoundedRect(QRectF(0, track_y, fg_width, stroke), stroke/2, stroke/2)

        # 文本
        if self._show_text:
            text_color = QColor("#FFFFFF") if t.is_dark() else QColor(fg)
            painter.setPen(text_color)
            text_rect = QRectF(track_w + 8, 0, text_width + 4, h)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)

        painter.end()

    @Property(int)
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, value):
        value = max(0, min(100, value))
        if self._percentage != value:
            self._percentage = value
            self.update()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        if t.is_liquid_glass():
            if not hasattr(self, "_liquid_timer"):
                from PySide6.QtCore import QTimer
                self._liquid_timer = QTimer(self)
                self._liquid_timer.timeout.connect(self._on_liquid_timeout)
            if not self._liquid_timer.isActive():
                self._liquid_timer.start(33)
        elif hasattr(self, "_liquid_timer") and self._liquid_timer.isActive():
            self._liquid_timer.stop()
        self.update()

    def _on_liquid_timeout(self):
        import math
        self._time_angle += 0.035
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()
