# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import draw_liquid_glass, qcolor

class MkSwitch(QWidget):
    """
    MkSwitch 组件 - 开关组件，支持 68 种主题风格的自适应绘制与平滑过渡过渡效果。
    """
    toggled = Signal(bool)

    def __init__(self, checked=False, active_color="#409eff", inactive_color="#dcdfe6", width=44, height=24, parent=None):
        super().__init__(parent)
        self._checked = checked
        self._active_color = active_color
        self._inactive_color = inactive_color
        self._switch_width = width
        self._switch_height = height
        self._handle_size = height - 4

        self._handle_pos = float(2 if not checked else width - self._handle_size - 2)
        self._time_angle = 0.0

        self.setFixedSize(width, height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._anim = QPropertyAnimation(self, b"handle_pos")
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.setDuration(200)
        
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        t = ThemeEngine
        primary = qcolor(t.get("--primary", "#409EFF"))
        bg = qcolor(t.get("--bg", "#FFFFFF"))
        inactive_color = QColor(self._inactive_color) if not t.is_dark() else QColor("#4C4D4F")

        w = self.width()
        h = self.height()
        handle_size = self._handle_size
        rr = h / 2

        # ──── 绘制轨道 ────
        track_color = primary if self._checked else inactive_color

        if t.is_neumorphic():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 20)))
            painter.drawRoundedRect(1, 1, w, h, rr, rr)
            painter.setBrush(QBrush(QColor(255, 255, 255, 150)))
            painter.drawRoundedRect(-1, -1, w, h, rr, rr)
            painter.setBrush(QBrush(track_color))
            painter.drawRoundedRect(0, 0, w, h, rr, rr)

        elif t.is_brutal():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#000000")))
            painter.drawRect(3, 3, w, h)
            painter.setBrush(QBrush(track_color))
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(0, 0, w, h)

        elif t.is_glass():
            if t.is_liquid_glass():
                draw_liquid_glass(
                    painter,
                    self.rect(),
                    int(rr),
                    t.get("--primary", "#409EFF"),
                    dark=t.is_dark(),
                    hovered=self._checked,
                    pressed=False,
                    angle=getattr(self, "_time_angle", 0.0),
                    intensity=0.55,
                )
            else:
                glass_track = QColor(track_color)
                glass_track.setAlphaF(0.34 if self._checked else 0.18)
                painter.setPen(QPen(qcolor(t.get("--glass-border", "rgba(255, 255, 255, 80)")), 1))
                painter.setBrush(QBrush(glass_track))
                painter.drawRoundedRect(0, 0, w, h, rr, rr)

        elif t.is_glow():
            if self._checked:
                glow = QColor(primary)
                glow.setAlphaF(0.3)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(glow))
                painter.drawRoundedRect(-2, -2, w + 4, h + 4, rr + 2, rr + 2)
            painter.setPen(QPen(primary if self._checked else QColor("#333"), 1))
            painter.setBrush(QBrush(track_color if self._checked else QColor(20, 20, 30)))
            painter.drawRoundedRect(0, 0, w, h, rr, rr)

        elif t.is_pixel():
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.setBrush(QBrush(track_color))
            painter.drawRect(0, 0, w, h)

        else:
            path = QPainterPath()
            path.addRoundedRect(0, 0, w, h, rr, rr)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.fillPath(path, track_color)

        # ──── 绘制手柄 ────
        hx = int(self._handle_pos)
        hy = 2

        if t.is_brutal():
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(hx, hy, handle_size, handle_size)

        elif t.is_pixel():
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(hx, hy, handle_size, handle_size)

        elif t.is_neumorphic():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.drawEllipse(hx - 1, hy - 1, handle_size, handle_size)
            painter.setBrush(QBrush(QColor(0, 0, 0, 15)))
            painter.drawEllipse(hx + 1, hy + 1, handle_size, handle_size)
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.drawEllipse(hx, hy, handle_size, handle_size)

        elif t.is_glow() and self._checked:
            glow = QColor(primary)
            glow.setAlphaF(0.5)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(hx - 2, hy - 2, handle_size + 4, handle_size + 4)
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.drawEllipse(hx, hy, handle_size, handle_size)

        else:
            painter.setBrush(QBrush(QColor(255, 255, 255, 235) if t.is_glass() else QColor("#FFFFFF")))
            painter.setPen(QPen(QColor(255, 255, 255, 90), 1) if t.is_glass() else Qt.PenStyle.NoPen)
            painter.drawEllipse(hx, hy, handle_size, handle_size)

        painter.end()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)
        super().mouseReleaseEvent(event)

    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self.toggled.emit(self._checked)
            self._start_animation()

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
        self._time_angle += 0.04
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()

    def _start_animation(self):
        self._anim.stop()
        end = self._switch_width - self._handle_size - 2 if self._checked else 2
        self._anim.setStartValue(self._handle_pos)
        self._anim.setEndValue(float(end))
        self._anim.start()

    @Property(float)
    def handle_pos(self):
        return self._handle_pos

    @handle_pos.setter
    def handle_pos(self, pos):
        self._handle_pos = pos
        self.update()

    @Property(bool)
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        self.setChecked(value)
