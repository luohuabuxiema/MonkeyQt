# -*- coding: utf-8 -*-
"""
ThemedAlert — 支持 67 种 UI 风格的信息条组件
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Signal, Property
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont
from ..engine import ThemeEngine
from ..style_utils import draw_liquid_glass, parse_px, qcolor


# 各类型的语义色
_ALERT_SEMANTIC = {
    "info":    {"icon": "i", "color": "#3B82F6", "light_bg": "#EFF6FF", "light_border": "#DBEAFE"},
    "success": {"icon": "+", "color": "#22C55E", "light_bg": "#F0FDF4", "light_border": "#DCFCE7"},
    "warning": {"icon": "!", "color": "#F59E0B", "light_bg": "#FFFBEB", "light_border": "#FEF3C7"},
    "error":   {"icon": "x", "color": "#EF4444", "light_bg": "#FEF2F2", "light_border": "#FEE2E2"},
}


class ThemedAlert(QWidget):
    """
    风格化信息条组件。

    用法:
        alert = ThemedAlert("Operation completed!", alert_type="success")
    """
    closed = Signal()

    def __init__(self, message="", alert_type="info", closable=False, parent=None):
        super().__init__(parent)
        self._message = message
        self._alert_type = alert_type
        self._closable = closable

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(44)
        self._time_angle = 0.0

        self._setup_ui()
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        # 图标
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(20, 20)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._icon_label, 0)

        # 消息文本
        self._msg_label = QLabel(self._message)
        self._msg_label.setWordWrap(True)
        self._msg_label.setStyleSheet("background: transparent;")
        layout.addWidget(self._msg_label, 1)

        # 关闭按钮
        self._close_btn = QPushButton("x")
        self._close_btn.setFixedSize(18, 18)
        self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_btn.setStyleSheet("QPushButton { background: transparent; border: none; font-size: 12px; }")
        self._close_btn.clicked.connect(self._on_close)
        self._close_btn.setVisible(self._closable)
        layout.addWidget(self._close_btn, 0)

    def _update_style(self):
        t = ThemeEngine
        sem = _ALERT_SEMANTIC.get(self._alert_type, _ALERT_SEMANTIC["info"])
        accent = sem["color"]
        primary = t.get("--primary", "#409EFF")
        bg = t.get("--bg", "#FFFFFF")
        fg = t.get("--fg", "#1E293B")
        radius = t.get("--radius", "6px")
        border_w = t.get("--border-width", "1px")

        # 图标
        self._icon_label.setText(sem["icon"])

        if t.is_brutal():
            self._icon_label.setStyleSheet(f"""
                QLabel {{ background: {accent}; color: #FFFFFF;
                border: 2px solid #000000; font-weight: 900; font-size: 12px; }}
            """)
            self._msg_label.setStyleSheet(f"background: transparent; color: #000000; font-weight: 700;")
            self._close_btn.setStyleSheet("QPushButton { background: transparent; border: none; color: #000; font-weight: 900; }")
            self.setStyleSheet("QWidget { background: transparent; }")

        elif t.is_glow() or t.is_dark():
            self._icon_label.setStyleSheet(f"""
                QLabel {{ background: transparent; color: {accent};
                font-weight: 900; font-size: 14px; }}
            """)
            self._msg_label.setStyleSheet(f"background: transparent; color: #E0E0E0;")
            self._close_btn.setStyleSheet("QPushButton { background: transparent; border: none; color: #888; }")
            self.setStyleSheet("QWidget { background: transparent; }")

        elif t.is_glass():
            self._icon_label.setStyleSheet(f"""
                QLabel {{ background: transparent; color: {accent};
                font-weight: 900; font-size: 14px; }}
            """)
            self._msg_label.setStyleSheet(f"background: transparent; color: {t.get('--glass-text', fg)};")
            self.setStyleSheet("QWidget { background: transparent; }")

        elif t.is_neumorphic():
            self._icon_label.setStyleSheet(f"""
                QLabel {{ background: transparent; color: {accent};
                font-weight: 900; font-size: 14px; }}
            """)
            self._msg_label.setStyleSheet(f"background: transparent; color: {fg};")
            self.setStyleSheet("QWidget { background: transparent; }")

        elif t.is_pixel():
            self._icon_label.setStyleSheet(f"""
                QLabel {{ background: {accent}; color: #FFFFFF;
                font-family: Consolas; font-weight: 900; font-size: 11px; }}
            """)
            self._msg_label.setStyleSheet(f"background: transparent; color: {fg}; font-family: Consolas;")
            self.setStyleSheet("QWidget { background: transparent; }")

        else:
            # 标准平面风格
            alert_bg = sem["light_bg"]
            alert_border = sem["light_border"]
            if t.is_dark():
                alert_bg = t._darken_hex(accent, 0.7)
                alert_border = t._darken_hex(accent, 0.5)

            self._icon_label.setStyleSheet(f"""
                QLabel {{ background: transparent; color: {accent};
                font-weight: 900; font-size: 14px; }}
            """)
            self._msg_label.setStyleSheet(f"background: transparent; color: {fg if not t.is_dark() else '#E0E0E0'};")
            self._close_btn.setStyleSheet(f"QPushButton {{ background: transparent; border: none; color: {accent}; }}")
            self.setStyleSheet(f"""
                ThemedAlert {{
                    background-color: {alert_bg};
                    border: {border_w} solid {alert_border};
                    border-radius: {radius};
                }}
            """)

    def paintEvent(self, event):
        t = ThemeEngine
        if not (t.is_neumorphic() or t.is_glass() or t.is_brutal() or t.is_glow() or t.is_dark() or t.is_pixel()):
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        sem = _ALERT_SEMANTIC.get(self._alert_type, _ALERT_SEMANTIC["info"])
        accent = QColor(sem["color"])
        primary = t.get("--primary", "#409EFF")
        bg = t.get("--bg", "#FFFFFF")
        r_str = t.get("--radius", "6px")
        radius = parse_px(r_str, 6, 0, 32)

        if t.is_neumorphic():
            inset = rect.adjusted(4, 4, -4, -4)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 15)))
            painter.drawRoundedRect(inset.translated(2, 2), radius, radius)
            painter.setBrush(QBrush(QColor(255, 255, 255, 150)))
            painter.drawRoundedRect(inset.translated(-1, -1), radius, radius)
            bg_color = QColor(bg) if bg.startswith("#") else QColor("#E8E8E8")
            painter.setBrush(QBrush(bg_color))
            painter.drawRoundedRect(inset, radius, radius)
            # 左侧色条
            painter.setBrush(QBrush(accent))
            painter.drawRoundedRect(inset.left(), inset.top() + 4, 4, inset.height() - 8, 2, 2)

        elif t.is_glass():
            inset = rect.adjusted(2, 2, -2, -2)
            if t.is_liquid_glass():
                draw_liquid_glass(
                    painter,
                    inset,
                    max(radius, 14),
                    sem["color"],
                    dark=t.is_dark(),
                    hovered=True,
                    angle=getattr(self, "_time_angle", 0.0),
                    intensity=0.7,
                )
            else:
                glass = QColor(accent)
                glass.setAlphaF(0.12)
                painter.setPen(QPen(qcolor(t.get("--glass-border", "rgba(255, 255, 255, 70)")), 1))
                painter.setBrush(QBrush(glass))
                painter.drawRoundedRect(inset, radius, radius)
            # 左侧色条
            bar_color = QColor(accent)
            bar_color.setAlphaF(0.7)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bar_color))
            painter.drawRoundedRect(inset.left(), inset.top() + 4, 3, inset.height() - 8, 1, 1)

        elif t.is_brutal():
            inset = rect.adjusted(3, 3, -6, -6)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#000000")))
            painter.drawRect(inset.translated(3, 3))
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(inset)
            # 左侧色块
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(accent))
            painter.drawRect(inset.left(), inset.top(), 6, inset.height())

        elif t.is_glow() or t.is_dark():
            inset = rect.adjusted(1, 1, -1, -1)
            # 暗底
            painter.setBrush(QBrush(QColor(15, 15, 25)))
            painter.setPen(QPen(accent, 1))
            painter.drawRoundedRect(inset, radius, radius)
            # 左侧色条
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(accent))
            painter.drawRoundedRect(inset.left() + 1, inset.top() + 4, 3, inset.height() - 8, 1, 1)

        elif t.is_pixel():
            inset = rect.adjusted(2, 2, -5, -5)
            pixel = 3
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#000000")))
            for x in range(inset.left() + pixel, inset.right() + pixel, pixel):
                painter.drawRect(x, inset.bottom(), pixel, pixel)
            for y in range(inset.top() + pixel, inset.bottom() + pixel, pixel):
                painter.drawRect(inset.right(), y, pixel, pixel)
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(inset)
            # 左侧色块
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(accent))
            painter.drawRect(inset.left(), inset.top(), 6, inset.height())

        painter.end()

    def _on_close(self):
        self.hide()
        self.closed.emit()

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
        self._update_style()
        self.update()

    def _on_liquid_timeout(self):
        import math
        self._time_angle += 0.035
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()

    @Property(str)
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value
        self._msg_label.setText(value)

    @Property(str)
    def alert_type(self):
        return self._alert_type

    @alert_type.setter
    def alert_type(self, value):
        if value not in _ALERT_SEMANTIC:
            value = "info"
        self._alert_type = value
        self._update_style()
        self.update()
