# -*- coding: utf-8 -*-
"""ThemedTabs — theme-aware tab container."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from ..engine import ThemeEngine
from ..style_utils import draw_liquid_glass, parse_px, qcolor


class _ThemedTabButton(QPushButton):
    def __init__(self, tab_id: str, title: str, parent=None):
        super().__init__(title, parent)
        self.tab_id = tab_id
        self._hovered = False
        self._time_angle = 0.0
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(38)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
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

        fg = t.get("--fg", "#1E293B")
        primary = t.get("--primary", "#409EFF")
        text = t.get("--glass-text", fg) if t.is_glass() else fg
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {primary if self.isChecked() else text};
                padding: 8px 16px;
                font-weight: 700;
            }}
        """)
        self.update()

    def paintEvent(self, event):
        t = ThemeEngine
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--fg", "#1E293B")
        radius = parse_px(t.get("--radius", "6px"), 6, 0, 28)
        active = self.isChecked()

        if active or self._hovered:
            inset = rect.adjusted(2, 3, -2, -3)
            if t.is_liquid_glass():
                draw_liquid_glass(
                    painter, inset, max(radius, 14), primary,
                    dark=t.is_dark(), hovered=self._hovered or active,
                    angle=self._time_angle, intensity=0.55,
                )
            elif t.is_glass():
                painter.setPen(QPen(qcolor(t.get("--glass-border", "rgba(255, 255, 255, 90)")), 1))
                painter.setBrush(QBrush(QColor(255, 255, 255, 46 if not t.is_dark() else 24)))
                painter.drawRoundedRect(inset, radius, radius)
            elif t.is_neumorphic():
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(255, 255, 255, 160)))
                painter.drawRoundedRect(inset.translated(-1, -1), radius, radius)
                painter.setBrush(QBrush(QColor(0, 0, 0, 18)))
                painter.drawRoundedRect(inset.translated(2, 2), radius, radius)
                painter.setBrush(QBrush(qcolor(t.get("--bg", "#F5F5F5"))))
                painter.drawRoundedRect(inset, radius, radius)
            elif t.is_brutal():
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor("#000000")))
                painter.drawRect(inset.translated(3, 3))
                painter.setBrush(QBrush(qcolor(primary) if active else QColor("#FFFFFF")))
                painter.setPen(QPen(QColor("#000000"), 2))
                painter.drawRect(inset)
            elif t.is_glow():
                glow = qcolor(primary, "#409EFF", 0.20 if active else 0.10)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(glow))
                painter.drawRoundedRect(inset.adjusted(-2, -2, 2, 2), radius, radius)
                painter.setBrush(QBrush(QColor(16, 18, 28)))
                painter.setPen(QPen(qcolor(primary), 1))
                painter.drawRoundedRect(inset, radius, radius)
            elif t.is_pixel():
                painter.setBrush(QBrush(qcolor(primary) if active else QColor("#FFFFFF")))
                painter.setPen(QPen(QColor("#000000"), 2))
                painter.drawRect(inset)
            else:
                fill = qcolor(primary, "#409EFF", 0.10 if not active else 0.16)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(fill))
                painter.drawRoundedRect(inset, radius, radius)

        # Active underline, useful for styles where filled tabs are subtle.
        if active and not (t.is_brutal() or t.is_pixel()):
            underline = qcolor(primary)
            painter.setPen(QPen(underline, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(10, rect.bottom() - 2, rect.width() - 10, rect.bottom() - 2)

        text_color = qcolor(primary) if active else qcolor(t.get("--glass-text", fg) if t.is_glass() else fg)
        if t.is_brutal() or t.is_pixel():
            text_color = QColor("#000000") if not active else QColor("#FFFFFF")
        painter.setPen(text_color)
        font = self.font()
        if t.is_brutal():
            font.setWeight(QFont.Weight.Black)
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

    def _on_liquid_timeout(self):
        import math
        self._time_angle += 0.035
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()


class ThemedTabs(QWidget):
    """A themed tab header plus QStackedWidget content area."""

    tabChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs: dict[str, QWidget] = {}
        self._buttons: dict[str, _ThemedTabButton] = {}

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)

        self.header_widget = QWidget()
        self.header_widget.setObjectName("themedTabsHeader")
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(6)
        self.header_layout.addStretch()
        self._layout.addWidget(self.header_widget)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self._on_tab_clicked)

        self.content_area = QStackedWidget()
        self.content_area.setObjectName("themedTabsContent")
        self._layout.addWidget(self.content_area, 1)

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def add_tab(self, tab_id: str, title: str, widget: QWidget):
        btn = _ThemedTabButton(tab_id, title)
        self.button_group.addButton(btn)
        self.header_layout.insertWidget(self.header_layout.count() - 1, btn)

        self.content_area.addWidget(widget)
        self._tabs[tab_id] = widget
        self._buttons[tab_id] = btn

        if len(self._tabs) == 1:
            btn.setChecked(True)
            self.content_area.setCurrentWidget(widget)
            btn.set_theme_style()

    def set_active(self, tab_id: str):
        btn = self._buttons.get(tab_id)
        if btn:
            btn.setChecked(True)
            self._on_tab_clicked(btn)

    def _on_tab_clicked(self, btn):
        tab_id = btn.tab_id
        widget = self._tabs.get(tab_id)
        if widget:
            self.content_area.setCurrentWidget(widget)
            for button in self._buttons.values():
                button.set_theme_style()
            self.tabChanged.emit(tab_id)

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        bg = "transparent"
        content_bg = t.get("--glass-surface", "rgba(255, 255, 255, 40)") if t.is_glass() else "transparent"
        radius = t.get("--radius", "6px")
        self.header_widget.setStyleSheet(f"""
            QWidget#themedTabsHeader {{
                background: {bg};
                border-bottom: 1px solid {border};
                padding-bottom: 4px;
            }}
        """)
        self.content_area.setStyleSheet(f"""
            QStackedWidget#themedTabsContent {{
                background: {content_bg};
                border: none;
                border-radius: {radius};
            }}
        """)
        for btn in self._buttons.values():
            btn.set_theme_style()
        self.update()
