# -*- coding: utf-8 -*-
"""ThemedCheckBox — theme-aware checkbox."""

from PySide6.QtCore import Property, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush
from PySide6.QtWidgets import QCheckBox

from ..engine import ThemeEngine
from ..style_utils import draw_liquid_glass, parse_px, qcolor


class ThemedCheckBox(QCheckBox):
    """A custom-painted checkbox so special themes do not depend on weak QSS indicators."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._hovered = False
        self._time_angle = 0.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(28)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
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

        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        self.setStyleSheet(f"""
            QCheckBox {{
                background: transparent;
                border: none;
                color: {fg};
                spacing: 8px;
                padding: 2px;
            }}
            QCheckBox::indicator {{
                width: 0;
                height: 0;
            }}
        """)
        self.update()

    def paintEvent(self, event):
        t = ThemeEngine
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        primary = t.get("--primary", "#409EFF")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        radius = 0 if t.is_pixel() or t.is_brutal() else min(parse_px(t.get("--radius", "6px"), 4, 0, 12), 5)

        size = 18
        y = (self.height() - size) // 2
        box = self.rect().adjusted(2, y, 2 - self.width() + size + 2, y - self.height() + size)
        checked = self.isChecked()

        if t.is_liquid_glass():
            draw_liquid_glass(
                painter, box, max(radius, 7), primary,
                dark=t.is_dark(), hovered=self._hovered or checked,
                angle=self._time_angle, intensity=0.45,
            )
            if checked:
                painter.setBrush(QBrush(qcolor(primary, "#409EFF", 0.72)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(box.adjusted(3, 3, -3, -3), max(2, radius - 1), max(2, radius - 1))
        elif t.is_neumorphic():
            base = qcolor(t.get("--bg", "#F5F5F5"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 24)))
            painter.drawRoundedRect(box.translated(2, 2), radius, radius)
            painter.setBrush(QBrush(QColor(255, 255, 255, 160)))
            painter.drawRoundedRect(box.translated(-1, -1), radius, radius)
            painter.setBrush(QBrush(qcolor(primary) if checked else base))
            painter.drawRoundedRect(box, radius, radius)
        elif t.is_glass():
            painter.setPen(QPen(qcolor(border), 1))
            painter.setBrush(QBrush(qcolor(primary, "#409EFF", 0.45) if checked else QColor(255, 255, 255, 42 if not t.is_dark() else 22)))
            painter.drawRoundedRect(box, radius, radius)
        elif t.is_brutal() or t.is_pixel():
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.setBrush(QBrush(qcolor(primary) if checked else QColor("#FFFFFF")))
            painter.drawRect(box)
        elif t.is_glow():
            if checked:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(qcolor(primary, "#409EFF", 0.22)))
                painter.drawRoundedRect(box.adjusted(-3, -3, 3, 3), radius + 3, radius + 3)
            painter.setPen(QPen(qcolor(primary), 1))
            painter.setBrush(QBrush(qcolor(primary) if checked else QColor(16, 18, 28)))
            painter.drawRoundedRect(box, radius, radius)
        else:
            painter.setPen(QPen(qcolor(primary if self._hovered or checked else border), 1.2))
            painter.setBrush(QBrush(qcolor(primary) if checked else qcolor(t.get("--surface", "#FFFFFF"))))
            painter.drawRoundedRect(box, radius, radius)

        if checked:
            check_color = QColor("#000000") if (t.is_brutal() or t.is_pixel()) else QColor("#FFFFFF")
            painter.setPen(QPen(check_color, 2.1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(box.left() + 4, box.center().y(), box.left() + 8, box.bottom() - 5)
            painter.drawLine(box.left() + 8, box.bottom() - 5, box.right() - 4, box.top() + 5)

        text_color = qcolor(fg)
        if not self.isEnabled():
            text_color = qcolor(t.get("--text-muted", "#94A3B8"))
        painter.setPen(text_color)
        font = self.font()
        if t.is_pixel():
            font.setFamily("Consolas")
        elif t.is_brutal():
            font.setWeight(QFont.Weight.Black)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(size + 10, 0, -2, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())
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
        self._time_angle += 0.035
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()

    @Property(str)
    def label(self):
        return self.text()

    @label.setter
    def label(self, value):
        self.setText(value)
        self.update()
