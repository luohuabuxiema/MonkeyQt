# -*- coding: utf-8 -*-
"""
ThemedButton — 支持 67 种 UI 风格的按钮组件
根据当前 ThemeEngine 活跃的 Design Token 自动切换视觉表现。
"""

from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont, QLinearGradient
from ..engine import ThemeEngine
from ..style_utils import draw_liquid_glass, parse_px, qcolor, readable_text


class ThemedButton(QPushButton):
    """
    风格化按钮组件。

    用法:
        btn = ThemedButton("Click Me", btn_type="primary")
        ThemeEngine.set_theme("Cyberpunk UI")  # 全局切换后自动刷新
    """

    def __init__(self, text="", btn_type="primary", parent=None):
        super().__init__(text, parent)
        self._btn_type = btn_type  # primary / secondary / default / danger / success
        self._hovered = False
        self._pressed = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self._time_angle = 0.0
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self._update_style()

    def _update_style(self):
        """根据当前主题生成 QSS 或设置自定义绘制标志"""
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
        primary = t.get("--primary", "#409EFF")
        bg = t.get("--bg", "#FFFFFF")
        fg = t.get("--fg", "#1E293B")
        border = t.get("--border", "#E2E8F0")
        radius = t.get("--radius", "6px")
        border_w = t.get("--border-width", "1px")

        # 对于需要 paintEvent 的复杂风格，仅设透明背景
        if t.is_neumorphic() or t.is_glass() or t.is_glow() or t.is_brutal() or t.is_pixel():
            text = t.get("--glass-text", fg) if t.is_glass() else fg
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: {text};
                    padding: 8px 20px;
                    font-weight: 700;
                }}
                QPushButton:disabled {{
                    color: #94A3B8;
                }}
            """)
            # 清除旧的阴影效果
            self.setGraphicsEffect(None)
            self.update()
            return

        # 标准 QSS 风格
        hover_primary = t._lighten_hex(primary, 0.15) if primary.startswith("#") else primary
        press_primary = t._darken_hex(primary, 0.1) if primary.startswith("#") else primary

        if self._btn_type == "primary":
            btn_bg = primary
            btn_fg = "#FFFFFF"
            btn_border = primary
            btn_hover_bg = hover_primary
            btn_press_bg = press_primary
        elif self._btn_type == "danger":
            btn_bg = "#EF4444"
            btn_fg = "#FFFFFF"
            btn_border = "#EF4444"
            btn_hover_bg = "#F87171"
            btn_press_bg = "#DC2626"
        elif self._btn_type == "success":
            btn_bg = "#22C55E"
            btn_fg = "#FFFFFF"
            btn_border = "#22C55E"
            btn_hover_bg = "#4ADE80"
            btn_press_bg = "#16A34A"
        elif self._btn_type == "secondary":
            btn_bg = "transparent"
            btn_fg = primary
            btn_border = primary
            btn_hover_bg = t._lighten_hex(primary, 0.9) if primary.startswith("#") else "#F0F4FF"
            btn_press_bg = t._lighten_hex(primary, 0.8) if primary.startswith("#") else "#E0E7FF"
        else:  # default
            btn_bg = bg
            btn_fg = fg
            btn_border = border
            btn_hover_bg = "#F8FAFC"
            btn_press_bg = "#F1F5F9"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_bg};
                color: {btn_fg};
                border: {border_w} solid {btn_border};
                border-radius: {radius};
                padding: 8px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {btn_hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {btn_press_bg};
            }}
            QPushButton:disabled {{
                opacity: 0.5;
                background-color: #E2E8F0;
                color: #94A3B8;
                border-color: #E2E8F0;
            }}
        """)
        self.setGraphicsEffect(None)

    def paintEvent(self, event):
        t = ThemeEngine

        # 对于标准 QSS 风格，使用默认绘制
        if not (t.is_neumorphic() or t.is_glass() or t.is_glow() or t.is_brutal() or t.is_pixel()):
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

        btn_color = qcolor(primary) if self._btn_type == "primary" else qcolor(bg, "#FFFFFF")
        text_color = QColor(readable_text(btn_color)) if self._btn_type == "primary" else qcolor(fg)
        if not self.isEnabled():
            btn_color = qcolor("#CBD5E1")
            text_color = qcolor("#64748B")

        if self._hovered:
            btn_color = btn_color.lighter(115)
        if self._pressed:
            btn_color = btn_color.darker(110)

        # ──── Neumorphism 绘制 ────
        if t.is_neumorphic():
            inset = rect.adjusted(4, 4, -4, -4)
            # 暗部阴影
            painter.setPen(Qt.PenStyle.NoPen)
            shadow_dark = QColor(0, 0, 0, 25)
            painter.setBrush(QBrush(shadow_dark))
            painter.drawRoundedRect(inset.translated(3, 3), radius, radius)
            # 亮部阴影
            shadow_light = QColor(255, 255, 255, 180)
            painter.setBrush(QBrush(shadow_light))
            painter.drawRoundedRect(inset.translated(-2, -2), radius, radius)
            # 主体
            painter.setBrush(QBrush(btn_color))
            painter.drawRoundedRect(inset, radius, radius)

        # ──── Glassmorphism 绘制 ────
        elif t.is_glass():
            inset = rect.adjusted(2, 2, -2, -2)
            if t.is_liquid_glass():
                angle = getattr(self, "_time_angle", 0.0)
                draw_liquid_glass(
                    painter,
                    inset,
                    max(radius, 14),
                    primary,
                    dark=t.is_dark(),
                    hovered=self._hovered,
                    pressed=self._pressed,
                    angle=angle,
                    intensity=0.75,
                )
                text_color = qcolor(t.get("--glass-text", fg))
            else:
                glass_bg = QColor(btn_color)
                glass_bg.setAlphaF(0.22 if self._btn_type != "primary" else 0.42)
                painter.setPen(QPen(qcolor(t.get("--glass-border", "rgba(255, 255, 255, 120)")), 1))
                painter.setBrush(QBrush(glass_bg))
                painter.drawRoundedRect(inset, radius, radius)
                text_color = qcolor(t.get("--glass-text", fg))

        # ──── Brutalism 绘制 ────
        elif t.is_brutal():
            radius = 0
            inset = rect.adjusted(2, 2, -6, -6)
            # 硬偏移阴影
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#000000")))
            painter.drawRect(inset.translated(4, 4))
            # 主体
            painter.setBrush(QBrush(btn_color))
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(inset)
            text_color = QColor("#FFFFFF") if self._btn_type == "primary" else QColor("#000000")

        # ──── Cyberpunk / Glow 绘制 ────
        elif t.is_glow():
            inset = rect.adjusted(3, 3, -3, -3)
            glow_color = QColor(primary)
            glow_color.setAlphaF(0.4)
            # 外发光
            for i in range(3, 0, -1):
                gc = QColor(glow_color)
                gc.setAlphaF(0.1 * i)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(gc))
                painter.drawRoundedRect(inset.adjusted(-i*2, -i*2, i*2, i*2), radius, radius)
            # 主体
            painter.setBrush(QBrush(QColor(primary) if self._btn_type == "primary" else QColor(20, 20, 30)))
            painter.setPen(QPen(QColor(primary), 1))
            painter.drawRoundedRect(inset, radius, radius)
            text_color = QColor(primary) if self._btn_type != "primary" else QColor("#FFFFFF")

        # ──── Pixel Art 绘制 ────
        elif t.is_pixel():
            radius = 0
            pixel = 3
            inset = rect.adjusted(2, 2, -2, -2)
            # 像素化边框
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#000000")))
            # 底部 + 右侧像素阴影
            for x in range(inset.left() + pixel, inset.right() + pixel, pixel):
                painter.drawRect(x, inset.bottom(), pixel, pixel)
            for y in range(inset.top() + pixel, inset.bottom() + pixel, pixel):
                painter.drawRect(inset.right(), y, pixel, pixel)
            # 主体
            painter.setBrush(QBrush(btn_color))
            painter.drawRect(inset)
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(inset)

        # 绘制文字
        painter.setPen(text_color)
        font = self.font()
        if t.is_brutal():
            font.setWeight(QFont.Weight.Black)
            font.setCapitalization(QFont.Capitalization.AllUppercase)
        elif t.is_pixel():
            font.setFamily("Consolas")
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def _on_liquid_timeout(self):
        import math
        self._time_angle += 0.04
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()

    def set_theme_style(self, style_name: str = None):
        """手动触发风格刷新（通常由 ThemeEngine.set_theme 全局触发）"""
        self._update_style()
        self.update()

    @Property(str)
    def btn_type(self):
        return self._btn_type

    @btn_type.setter
    def btn_type(self, value):
        self._btn_type = value
        self._update_style()
