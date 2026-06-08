# -*- coding: utf-8 -*-
"""ThemedProgressRing — circular progress indicator."""

from PySide6.QtCore import Property, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..engine import ThemeEngine
from ..style_utils import qcolor


_STATUS_COLORS = {
    "normal": None,
    "success": "#22C55E",
    "warning": "#F59E0B",
    "exception": "#EF4444",
}


class ThemedProgressRing(QWidget):
    """A themed circular progress indicator with semantic status support."""

    def __init__(self, percentage=0, status="normal", stroke_width=7, width=116, show_text=True, parent=None):
        super().__init__(parent)
        self._percentage = max(0, min(100, int(percentage)))
        self._status = status if status in _STATUS_COLORS else "normal"
        self._stroke_width = max(2, int(stroke_width))
        self._ring_width = int(width)
        self._show_text = bool(show_text)
        self._time_angle = 0.0

        self.setFixedSize(self._ring_width, self._ring_width)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_label = QLabel(f"{self._percentage}%")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setVisible(self._show_text)
        self.layout.addWidget(self.text_label)

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def _color(self):
        return _STATUS_COLORS[self._status] or ThemeEngine.get("--primary", "#409EFF")

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
        font_size = max(12, int(self._ring_width * 0.15))
        self.text_label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                color: {fg};
                font-size: {font_size}px;
                font-weight: 800;
            }}
        """)
        self.update()

    def paintEvent(self, event):
        t = ThemeEngine
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        sw = self._stroke_width
        rect = QRectF(sw / 2 + 3, sw / 2 + 3, self.width() - sw - 6, self.height() - sw - 6)
        accent = qcolor(self._color())

        if t.is_glow() or t.is_liquid_glass():
            glow = QColor(accent)
            glow.setAlphaF(0.18)
            pen_glow = QPen(glow)
            pen_glow.setWidth(sw + 8)
            pen_glow.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_glow)
            painter.drawArc(rect, 90 * 16, int(-self._percentage / 100.0 * 360 * 16))

        track = qcolor(t.get("--surface-muted", "#E5E7EB"))
        if t.is_dark() or t.is_glow():
            track = qcolor("#243244")
        elif t.is_glass():
            track = qcolor(t.get("--glass-surface", "rgba(255, 255, 255, 70)"))
        elif t.is_brutal() or t.is_pixel():
            track = QColor("#FFFFFF")

        pen_bg = QPen(track)
        pen_bg.setWidth(sw)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap if not (t.is_brutal() or t.is_pixel()) else Qt.PenCapStyle.SquareCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)

        if t.is_brutal() or t.is_pixel():
            outline = QPen(QColor("#000000"))
            outline.setWidth(2)
            outline.setCapStyle(Qt.PenCapStyle.SquareCap)
            painter.setPen(outline)
            painter.drawArc(rect, 0, 360 * 16)

        if self._percentage > 0:
            pen_fg = QPen(accent)
            pen_fg.setWidth(sw)
            pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap if not (t.is_brutal() or t.is_pixel()) else Qt.PenCapStyle.SquareCap)
            painter.setPen(pen_fg)
            start = int((90 + (self._time_angle * 18 if t.is_liquid_glass() else 0)) * 16)
            span = int(-self._percentage / 100.0 * 360 * 16)
            painter.drawArc(rect, start, span)

            if t.is_liquid_glass():
                shine = QColor("#FFFFFF")
                shine.setAlphaF(0.70)
                pen_shine = QPen(shine)
                pen_shine.setWidth(max(2, sw // 3))
                pen_shine.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(pen_shine)
                painter.drawArc(rect, start, max(-28 * 16, span // 8))

        painter.end()

    @Property(int)
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, value):
        value = max(0, min(100, int(value)))
        if self._percentage != value:
            self._percentage = value
            self.text_label.setText(f"{value}%")
            self.update()

    @Property(str)
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value if value in _STATUS_COLORS else "normal"
        self.update()

    @Property(bool)
    def show_text(self):
        return self._show_text

    @show_text.setter
    def show_text(self, value):
        self._show_text = bool(value)
        self.text_label.setVisible(self._show_text)

    def _on_liquid_timeout(self):
        import math
        self._time_angle += 0.025
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()
