# -*- coding: utf-8 -*-
"""
ThemedInput — 支持 67 种 UI 风格的输入框组件
"""

from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt, Property
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont
from ..engine import ThemeEngine
from ..style_utils import draw_liquid_glass, parse_px, qcolor


class ThemedInput(QLineEdit):
    """
    风格化输入框组件。

    用法:
        inp = ThemedInput(placeholder="Enter your name...")
    """

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self._focused = False
        self._time_angle = 0.0
        self.setMinimumHeight(38)
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self._update_style()

    def _update_style(self):
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        bg = t.get("--bg", "#FFFFFF")
        fg = t.get("--fg", "#1E293B")
        border = t.get("--border", "#E2E8F0")
        radius = t.get("--radius", "6px")
        border_w = t.get("--border-width", "1px")

        if t.is_liquid_glass():
            if not hasattr(self, "_liquid_timer"):
                from PySide6.QtCore import QTimer
                self._liquid_timer = QTimer(self)
                self._liquid_timer.timeout.connect(self._on_liquid_timeout)
            if not self._liquid_timer.isActive():
                self._liquid_timer.start(33)
        elif hasattr(self, "_liquid_timer") and self._liquid_timer.isActive():
            self._liquid_timer.stop()

        if t.is_neumorphic() or t.is_glass() or t.is_brutal() or t.is_pixel():
            text = t.get("--glass-text", fg) if t.is_glass() else fg
            self.setStyleSheet(f"""
                QLineEdit {{
                    background: transparent;
                    border: none;
                    color: {text};
                    padding: 8px 13px;
                    selection-background-color: {primary};
                    selection-color: #FFFFFF;
                }}
            """)
            self.update()
            return

        # 暗色主题自适应
        if t.is_dark():
            input_bg = t._lighten_hex(bg, 0.08) if bg.startswith("#") else "#1E1E1E"
            placeholder_color = "#64748B"
        else:
            input_bg = "#FFFFFF"
            placeholder_color = "#94A3B8"

        hover_border = t._lighten_hex(primary, 0.3) if primary.startswith("#") else border

        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {input_bg};
                border: {border_w} solid {border};
                border-radius: {radius};
                color: {fg};
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: {primary};
                selection-color: #FFFFFF;
            }}
            QLineEdit:hover {{
                border-color: {hover_border};
            }}
            QLineEdit:focus {{
                border-color: {primary};
            }}
            QLineEdit:disabled {{
                background-color: #F1F5F9;
                color: #94A3B8;
            }}
        """)

    def paintEvent(self, event):
        t = ThemeEngine

        if not (t.is_neumorphic() or t.is_glass() or t.is_brutal() or t.is_pixel()):
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        primary = t.get("--primary", "#409EFF")
        bg = t.get("--bg", "#FFFFFF")
        fg = t.get("--fg", "#1E293B")
        r_str = t.get("--radius", "6px")
        radius = parse_px(r_str, 6, 0, 32)

        if t.is_neumorphic():
            inset = rect.adjusted(4, 4, -4, -4)
            # 凹陷效果（内阴影）
            painter.setPen(Qt.PenStyle.NoPen)
            # 暗部
            painter.setBrush(QBrush(QColor(0, 0, 0, 20)))
            painter.drawRoundedRect(inset.translated(2, 2), radius, radius)
            # 亮部
            painter.setBrush(QBrush(QColor(255, 255, 255, 150)))
            painter.drawRoundedRect(inset.translated(-1, -1), radius, radius)
            # 主体（凹陷感）
            base_color = QColor(bg).darker(105) if bg.startswith("#") else QColor("#E0E0E0")
            painter.setBrush(QBrush(base_color))
            if self._focused:
                painter.setPen(QPen(QColor(primary), 1.5))
            else:
                painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(inset, radius, radius)

        elif t.is_glass():
            inset = rect.adjusted(2, 2, -2, -2)
            if t.is_liquid_glass():
                draw_liquid_glass(
                    painter,
                    inset,
                    max(radius, 14),
                    primary,
                    dark=t.is_dark(),
                    hovered=self._focused,
                    pressed=False,
                    angle=getattr(self, "_time_angle", 0.0),
                    intensity=0.65,
                )
            else:
                glass_bg = QColor(255, 255, 255, 34) if not t.is_dark() else QColor(255, 255, 255, 18)
                border_color = qcolor(t.get("--glass-border", "rgba(255, 255, 255, 80)")) if not self._focused else qcolor(primary)
                painter.setBrush(QBrush(glass_bg))
                painter.setPen(QPen(border_color, 1.2 if self._focused else 1))
                painter.drawRoundedRect(inset, radius, radius)

        elif t.is_brutal():
            inset = rect.adjusted(2, 2, -5, -5)
            # 硬偏移阴影
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#000000")))
            painter.drawRect(inset.translated(3, 3))
            # 主体
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            border_pen = QPen(QColor("#000000"), 2)
            if self._focused:
                border_pen = QPen(QColor(primary), 2)
            painter.setPen(border_pen)
            painter.drawRect(inset)

        elif t.is_pixel():
            inset = rect.adjusted(2, 2, -2, -2)
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.drawRect(inset)

        painter.end()
        super().paintEvent(event)

    def focusInEvent(self, event):
        self._focused = True
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._focused = False
        self.update()
        super().focusOutEvent(event)

    def set_theme_style(self, style_name: str = None):
        self._update_style()
        self.update()

    def _on_liquid_timeout(self):
        import math
        self._time_angle += 0.035
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()
