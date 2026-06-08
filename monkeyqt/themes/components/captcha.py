# -*- coding: utf-8 -*-
"""ThemedCaptchaWidget — themed graphical captcha."""

import random
import string

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from ..engine import ThemeEngine
from ..style_utils import qcolor


class ThemedCaptchaWidget(QWidget):
    """A theme-aware captcha preview/control."""

    codeChanged = Signal(str)

    def __init__(self, width=110, height=38, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._current_code = ""
        ThemeEngine.instance().themeChanged.connect(lambda name=None: self.update())
        self.generate_new_code()

    def generate_new_code(self):
        chars = string.ascii_uppercase + string.digits
        for exclude in ["O", "0", "I", "1", "L", "Z", "2"]:
            chars = chars.replace(exclude, "")
        self._current_code = "".join(random.choice(chars) for _ in range(4))
        self.codeChanged.emit(self._current_code)
        self.update()

    def get_code(self):
        return self._current_code

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.generate_new_code()
            event.accept()
        else:
            super().mousePressEvent(event)

    def paintEvent(self, event):
        t = ThemeEngine
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--glass-surface", t.get("--surface-muted", "#F8FAFC")) if t.is_glass() else t.get("--surface-muted", "#F8FAFC")
        radius = 0 if t.is_brutal() or t.is_pixel() else 7

        painter.setBrush(qcolor(surface))
        painter.setPen(QPen(QColor("#000000") if (t.is_brutal() or t.is_pixel()) else qcolor(border), 2 if (t.is_brutal() or t.is_pixel()) else 1))
        painter.drawRoundedRect(rect, radius, radius)

        for _ in range(38):
            color = qcolor(primary)
            color.setAlpha(random.randint(35, 95))
            painter.setPen(QPen(color, random.choice([1, 1.5])))
            painter.drawPoint(random.randint(3, self.width() - 3), random.randint(3, self.height() - 3))

        for _ in range(2):
            path = QPainterPath()
            path.moveTo(2, random.randint(6, self.height() - 6))
            path.cubicTo(self.width() * 0.35, random.randint(0, self.height()),
                         self.width() * 0.65, random.randint(0, self.height()),
                         self.width() - 2, random.randint(6, self.height() - 6))
            line = qcolor(primary)
            line.setAlpha(90)
            painter.setPen(QPen(line, 1))
            painter.drawPath(path)

        char_w = self.width() / 4
        families = ["Consolas", "Arial", "Verdana", "Georgia"]
        for idx, char in enumerate(self._current_code):
            painter.save()
            font = QFont("Consolas" if t.is_pixel() else random.choice(families), random.randint(17, 22), QFont.Weight.Black)
            painter.setFont(font)
            painter.setPen(qcolor("#000000" if t.is_brutal() or t.is_pixel() else fg))
            cx = idx * char_w + char_w / 2
            cy = self.height() / 2
            painter.translate(cx, cy)
            painter.rotate(random.randint(-18, 18))
            metrics = QFontMetrics(font)
            painter.drawText(int(-metrics.horizontalAdvance(char) / 2), int(metrics.ascent() / 2), char)
            painter.restore()
        painter.end()
