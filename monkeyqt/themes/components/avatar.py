# -*- coding: utf-8 -*-
"""ThemedAvatar — image/text avatar component."""

import os

from PySide6.QtCore import Property, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QBrush
from PySide6.QtWidgets import QLabel

from ..engine import ThemeEngine
from ..style_utils import draw_liquid_glass, parse_px, qcolor, readable_text


class ThemedAvatar(QLabel):
    """Avatar with themed fallback color, rim, and special-style treatment."""

    def __init__(self, text="", image_path="", shape="circle", size=44, parent=None):
        super().__init__(parent)
        self._text = text
        self._image_path = image_path
        self._shape = shape if shape in ("circle", "square") else "circle"
        self._avatar_size = int(size)
        self._time_angle = 0.0
        self.setFixedSize(self._avatar_size, self._avatar_size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

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

        font = self.font()
        font.setPixelSize(max(11, int(self._avatar_size * 0.38)))
        font.setWeight(QFont.Weight.Black)
        if t.is_pixel():
            font.setFamily("Consolas")
        self.setFont(font)
        self.update()

    def paintEvent(self, event):
        t = ThemeEngine
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = self.rect().adjusted(2, 2, -2, -2)
        radius = rect.width() / 2 if self._shape == "circle" else parse_px(t.get("--radius", "6px"), 6, 0, 18)

        path = QPainterPath()
        if self._shape == "circle":
            path.addEllipse(rect)
        elif t.is_brutal() or t.is_pixel():
            path.addRect(rect)
        else:
            path.addRoundedRect(rect, radius, radius)

        primary = t.get("--primary", "#409EFF")
        accent = t.get("--accent", "#7DD3FC")

        if t.is_liquid_glass():
            draw_liquid_glass(
                painter, rect, int(radius), primary,
                dark=t.is_dark(), hovered=True, angle=self._time_angle, intensity=0.65,
            )

        painter.save()
        painter.setClipPath(path)
        if self._image_path and os.path.exists(self._image_path):
            pixmap = QPixmap(self._image_path)
            scaled = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
            if t.is_brutal() or t.is_pixel():
                grad.setColorAt(0.0, qcolor(primary))
                grad.setColorAt(1.0, qcolor(primary))
            elif t.is_glass():
                c1 = qcolor(primary, "#409EFF", 0.58)
                c2 = qcolor(accent, "#7DD3FC", 0.42)
                grad.setColorAt(0.0, c1)
                grad.setColorAt(1.0, c2)
            else:
                grad.setColorAt(0.0, qcolor(primary))
                grad.setColorAt(1.0, qcolor(accent))
            painter.fillPath(path, QBrush(grad))

            if self._text:
                text = self._text[:2].upper()
                text_color = QColor("#000000") if (t.is_brutal() or t.is_pixel()) else QColor(readable_text(primary))
                painter.setPen(text_color)
                painter.setFont(self.font())
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

        if t.is_brutal() or t.is_pixel():
            painter.setPen(QPen(QColor("#000000"), 2))
        elif t.is_glass():
            painter.setPen(QPen(qcolor(t.get("--glass-border", "rgba(255, 255, 255, 120)")), 1.2))
        else:
            painter.setPen(QPen(qcolor(t.get("--border", "#E2E8F0")), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self._shape == "circle":
            painter.drawEllipse(rect)
        elif t.is_brutal() or t.is_pixel():
            painter.drawRect(rect)
        else:
            painter.drawRoundedRect(rect, radius, radius)
        painter.end()

    @Property(str)
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.update()

    @Property(str)
    def image_path(self):
        return self._image_path

    @image_path.setter
    def image_path(self, value):
        self._image_path = value
        self.update()

    @Property(str)
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        self._shape = value if value in ("circle", "square") else "circle"
        self.update()

    @Property(int)
    def size(self):
        return self._avatar_size

    @size.setter
    def size(self, value):
        self._avatar_size = int(value)
        self.setFixedSize(self._avatar_size, self._avatar_size)
        self.set_theme_style()

    def _on_liquid_timeout(self):
        import math
        self._time_angle += 0.03
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()
