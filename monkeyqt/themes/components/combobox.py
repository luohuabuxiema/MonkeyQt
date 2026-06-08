# -*- coding: utf-8 -*-
"""ThemedComboBox — theme-aware select/dropdown component."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush
from PySide6.QtWidgets import QComboBox, QFrame, QListView

from ..engine import ThemeEngine
from ..style_utils import draw_liquid_glass, parse_px, qcolor, readable_text


class ThemedComboBox(QComboBox):
    """A themed QComboBox with custom chrome for glass/brutal/pixel/glow styles."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hovered = False
        self._pressed = False
        self._time_angle = 0.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(38)
        self.setFont(QFont("Segoe UI", 10))

        view = QListView(self)
        view.setFrameShape(QFrame.Shape.NoFrame)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setView(view)

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

        primary = t.get("--primary", "#409EFF")
        fg = t.get("--fg", "#1E293B")
        bg = t.get("--bg", "#FFFFFF")
        surface = t.get("--surface", "#FFFFFF")
        border = t.get("--border", "#E2E8F0")
        radius = t.get("--radius", "6px")
        muted = t.get("--text-muted", "#64748B")
        selection_fg = readable_text(primary)

        if t.is_neumorphic() or t.is_glass() or t.is_brutal() or t.is_glow() or t.is_pixel():
            self.setStyleSheet(f"""
                QComboBox {{
                    background: transparent;
                    border: none;
                    color: {t.get('--glass-text', fg) if t.is_glass() else fg};
                    padding: 7px 34px 7px 12px;
                    font-size: 13px;
                }}
                QComboBox::drop-down {{ width: 30px; border: none; }}
                QComboBox::down-arrow {{ image: none; width: 0; height: 0; }}
                QComboBox QAbstractItemView {{
                    background-color: {surface if not t.is_glass() else t.get('--glass-surface', surface)};
                    color: {fg};
                    border: 1px solid {t.get('--glass-border', border) if t.is_glass() else border};
                    border-radius: {radius};
                    padding: 5px;
                    outline: none;
                    selection-background-color: {primary};
                    selection-color: {selection_fg};
                }}
                QComboBox QAbstractItemView::item {{
                    min-height: 30px;
                    padding: 5px 10px;
                    border-radius: 5px;
                }}
                QComboBox QAbstractItemView::item:hover {{
                    background-color: {t.get('--surface-muted', '#F1F5F9')};
                }}
            """)
        else:
            hover = t.get("--hover-primary", primary)
            self.setStyleSheet(f"""
                QComboBox {{
                    background-color: {surface};
                    border: 1px solid {border};
                    border-radius: {radius};
                    color: {fg};
                    padding: 7px 34px 7px 12px;
                    font-size: 13px;
                    min-height: 24px;
                }}
                QComboBox:hover {{ border-color: {hover}; }}
                QComboBox:focus, QComboBox:on {{ border-color: {primary}; }}
                QComboBox:disabled {{
                    background-color: {t.get('--surface-muted', '#F1F5F9')};
                    color: {muted};
                    border-color: {border};
                }}
                QComboBox::drop-down {{
                    width: 30px;
                    border: none;
                }}
                QComboBox::down-arrow {{ image: none; width: 0; height: 0; }}
                QComboBox QAbstractItemView {{
                    background-color: {surface};
                    color: {fg};
                    border: 1px solid {border};
                    border-radius: {radius};
                    padding: 5px;
                    outline: none;
                    selection-background-color: {primary};
                    selection-color: {selection_fg};
                }}
                QComboBox QAbstractItemView::item {{
                    min-height: 30px;
                    padding: 5px 10px;
                    border-radius: 5px;
                }}
                QComboBox QAbstractItemView::item:hover {{
                    background-color: {t.get('--surface-muted', '#F1F5F9')};
                }}
            """)
        self.update()

    def paintEvent(self, event):
        t = ThemeEngine
        if not (t.is_neumorphic() or t.is_glass() or t.is_brutal() or t.is_glow() or t.is_pixel()):
            super().paintEvent(event)
            self._draw_arrow()
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        primary = t.get("--primary", "#409EFF")
        bg = t.get("--bg", "#FFFFFF")
        fg = t.get("--fg", "#1E293B")
        radius = parse_px(t.get("--radius", "6px"), 6, 0, 32)
        inset = rect.adjusted(2, 2, -2, -2)

        if t.is_neumorphic():
            base = qcolor(bg, "#F5F5F5")
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 22)))
            painter.drawRoundedRect(inset.translated(2, 2), radius, radius)
            painter.setBrush(QBrush(QColor(255, 255, 255, 160)))
            painter.drawRoundedRect(inset.translated(-1, -1), radius, radius)
            painter.setBrush(QBrush(base))
            painter.setPen(QPen(qcolor(primary), 1 if self.hasFocus() else 0))
            painter.drawRoundedRect(inset, radius, radius)
        elif t.is_glass():
            if t.is_liquid_glass():
                draw_liquid_glass(
                    painter, inset, max(radius, 14), primary,
                    dark=t.is_dark(), hovered=self._hovered or self.hasFocus(),
                    pressed=self._pressed, angle=self._time_angle, intensity=0.7,
                )
            else:
                painter.setPen(QPen(qcolor(t.get("--glass-border", "rgba(255, 255, 255, 90)")), 1))
                painter.setBrush(QBrush(QColor(255, 255, 255, 42 if not t.is_dark() else 24)))
                painter.drawRoundedRect(inset, radius, radius)
        elif t.is_brutal():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#000000")))
            painter.drawRect(inset.translated(4, 4))
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(inset)
        elif t.is_glow():
            glow = qcolor(primary, "#409EFF", 0.18)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow))
            painter.drawRoundedRect(inset.adjusted(-3, -3, 3, 3), radius + 3, radius + 3)
            painter.setBrush(QBrush(QColor(16, 18, 28)))
            painter.setPen(QPen(qcolor(primary), 1))
            painter.drawRoundedRect(inset, radius, radius)
        elif t.is_pixel():
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.drawRect(inset)

        text_color = qcolor(t.get("--glass-text", fg) if t.is_glass() else fg)
        if t.is_brutal() or t.is_pixel():
            text_color = QColor("#000000")
        painter.setPen(text_color)
        font = self.font()
        if t.is_pixel():
            font.setFamily("Consolas")
        painter.setFont(font)
        painter.drawText(rect.adjusted(13, 0, -36, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.currentText())
        painter.end()
        self._draw_arrow()

    def _draw_arrow(self):
        t = ThemeEngine
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = qcolor(t.get("--primary", "#409EFF") if (self._hovered or self.hasFocus()) else t.get("--text-muted", "#64748B"))
        if t.is_brutal() or t.is_pixel():
            color = QColor("#000000")
        painter.setPen(QPen(color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        cx = self.width() - 18
        cy = self.height() // 2 + 1
        painter.drawLine(cx - 5, cy - 3, cx, cy + 3)
        painter.drawLine(cx, cy + 3, cx + 5, cy - 3)
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
        self._time_angle += 0.035
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()
