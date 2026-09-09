# -*- coding: utf-8 -*-
import time
from PySide6.QtCore import Qt, QPoint, QRect, QEvent
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QKeyEvent
from PySide6.QtWidgets import (
    QComboBox, QFrame, QListView, QWidget, QVBoxLayout,
    QGraphicsDropShadowEffect
)

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import draw_liquid_glass, parse_px, qcolor, readable_text


class MkDropdownPopup(QWidget):
    """
    无边框透明浮动卡片下拉弹窗 (Frameless Floating Card Dropdown)
    彻底消除 Windows 平台原生 HWND 方形黑角与锯齿遮挡，
    呈现媲美 Web/macOS 的真实抗锯齿圆角、柔和外发散阴影与高质感卡片。
    """
    MARGIN = 10  # 预留给柔和发散外阴影的空间，避免阴影边缘被窗口硬裁切

    def __init__(self, combo: "MkComboBox"):
        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.combo = combo
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        root_layout.setSpacing(0)

        # 核心浮动卡片
        self.card = QFrame(self)
        self.card.setObjectName("mkDropdownCard")
        self._card_layout = QVBoxLayout(self.card)
        self._card_layout.setContentsMargins(4, 4, 4, 4)
        self._card_layout.setSpacing(0)

        # 弥散外阴影
        self.shadow = QGraphicsDropShadowEffect(self.card)
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.card.setGraphicsEffect(self.shadow)

        root_layout.addWidget(self.card)

        self.view = None
        if combo.view() is not None:
            self.set_view(combo.view())

        self.update_theme_style()

    def set_view(self, view: QListView):
        if self.view is not None and self.view != view:
            self._card_layout.removeWidget(self.view)
            try:
                self.view.clicked.disconnect(self._on_item_clicked)
            except Exception:
                pass

        self.view = view
        self.view.setParent(self.card)
        self.view.setFrameShape(QFrame.Shape.NoFrame)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setSelectionMode(QListView.SelectionMode.SingleSelection)
        if hasattr(self.view, "viewport") and self.view.viewport():
            self.view.viewport().setAutoFillBackground(False)
        self.view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._card_layout.addWidget(self.view)
        self.view.clicked.connect(self._on_item_clicked)
        self.update_theme_style()

    def update_theme_style(self):
        t = ThemeEngine
        is_dark = t.is_dark() or getattr(self.combo, "_is_dark", False)
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--fg", "#1E293B") if not is_dark else (t.get("--fg", "#F1F5F9") if t.is_dark() else "#F1F5F9")
        surface = t.get("--surface", "#FFFFFF") if not is_dark else (t.get("--surface", "#18181B") if t.is_dark() else "#18181B")
        border = t.get("--border", "#E2E8F0") if not is_dark else (t.get("--border", "#3F3F46") if t.is_dark() else "#3F3F46")
        radius_raw = t.get("--radius", "8px")
        radius = parse_px(radius_raw, 8, 4, 20)
        selection_fg = readable_text(primary)

        if t.is_brutal() or t.is_pixel():
            self.shadow.setEnabled(False)
            card_border = "2px solid #000000"
            card_radius = 0
            card_bg = "#FFFFFF"
        else:
            self.shadow.setEnabled(True)
            if is_dark:
                self.shadow.setColor(QColor(0, 0, 0, 130))
                self.shadow.setBlurRadius(24)
                self.shadow.setOffset(0, 4)
            else:
                self.shadow.setColor(QColor(0, 0, 0, 38))
                self.shadow.setBlurRadius(20)
                self.shadow.setOffset(0, 4)
            card_border = f"1px solid {t.get('--glass-border', border) if t.is_glass() else border}"
            card_radius = radius
            card_bg = surface

        self.card.setStyleSheet(f"""
            QFrame#mkDropdownCard {{
                background-color: {card_bg};
                border: {card_border};
                border-radius: {card_radius}px;
            }}
        """)

        hover_bg = t.get('--surface-muted', '#f1f5f9') if not is_dark else 'rgba(255, 255, 255, 0.08)'

        if self.view is not None:
            self.view.setStyleSheet(f"""
                QListView {{
                    background-color: transparent;
                    border: none;
                    outline: none;
                    color: {fg};
                    padding: 2px;
                    selection-background-color: {primary};
                    selection-color: {selection_fg};
                }}
                QListView::item {{
                    min-height: 30px;
                    padding: 5px 12px;
                    border-radius: {max(card_radius - 2, 4) if card_radius > 0 else 0}px;
                    margin: 1px 2px;
                    color: {fg};
                }}
                QListView::item:hover {{
                    background-color: {hover_bg};
                    color: {fg};
                }}
                QListView::item:selected {{
                    background-color: {primary};
                    color: {selection_fg};
                }}
                QScrollBar:vertical {{
                    background: transparent;
                    width: 6px;
                    margin: 4px 2px 4px 0px;
                }}
                QScrollBar::handle:vertical {{
                    background: {'rgba(255, 255, 255, 0.25)' if is_dark else 'rgba(148, 163, 184, 0.5)'};
                    border-radius: 3px;
                    min-height: 24px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background: {'rgba(255, 255, 255, 0.4)' if is_dark else 'rgba(148, 163, 184, 0.8)'};
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    background: none;
                    border: none;
                    height: 0px;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: transparent;
                }}
            """)

    def _on_item_clicked(self, index):
        if index.isValid():
            self.combo.setCurrentIndex(index.row())
            self.combo.activated.emit(index.row())
        self.hide()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.view is not None:
                curr = self.view.currentIndex()
                if curr.isValid():
                    self.combo.setCurrentIndex(curr.row())
                    self.combo.activated.emit(curr.row())
            self.hide()
            event.accept()
        elif key == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
            if self.view is not None:
                self.view.keyPressEvent(event)
            event.accept()
        else:
            super().keyPressEvent(event)

    def hideEvent(self, event):
        self.combo._last_close_time = time.time()
        self.combo.update()
        super().hideEvent(event)

    def show_at_combo(self):
        combo = self.combo
        count = combo.count()
        if count == 0:
            return

        max_visible = combo.maxVisibleItems()
        visible_rows = min(count, max_visible)
        needs_scroll = count > max_visible

        total_items_h = 0
        for i in range(visible_rows):
            s = self.view.sizeHintForRow(i) if self.view is not None else 32
            total_items_h += max(s, 32)

        content_h = total_items_h + 10
        total_h = content_h + self.MARGIN * 2

        if self.view is not None:
            self.view.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded if needs_scroll else Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

        hint_w = self.view.sizeHintForColumn(0) if self.view is not None else 0
        card_w = max(combo.width(), hint_w + (32 if needs_scroll else 16))
        card_w = min(card_w, 640)
        total_w = card_w + self.MARGIN * 2
        self.resize(total_w, total_h)

        screen = combo.screen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)
        global_pos = combo.mapToGlobal(QPoint(0, 0))

        space_below = avail.bottom() - (global_pos.y() + combo.height())
        space_above = global_pos.y() - avail.top()

        if space_below < content_h + 10 and space_above > space_below:
            popup_y = global_pos.y() - total_h + self.MARGIN + 3
        else:
            popup_y = global_pos.y() + combo.height() - self.MARGIN - 3

        popup_x = global_pos.x() - self.MARGIN
        if popup_x + total_w > avail.right():
            popup_x = avail.right() - total_w
        if popup_x < avail.left():
            popup_x = avail.left()

        self.move(popup_x, popup_y)

        idx = combo.currentIndex()
        if 0 <= idx < count and self.view is not None and combo.model() is not None:
            model_idx = combo.model().index(idx, 0)
            self.view.setCurrentIndex(model_idx)
            self.view.scrollTo(model_idx)

        self.show()
        self.raise_()
        self.activateWindow()
        if self.view is not None:
            self.view.setFocus()


class MkComboBox(QComboBox):
    """
    MkComboBox 组件 - 完美融合 68 种内置主题风格的高清矢量绘制和对比度适配，
    支持玻璃拟态、拟物化、科幻发光以及经典样式的自动切换。
    内置 Web 标准高保真圆角阴影浮动卡片下拉窗口。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hovered = False
        self._pressed = False
        self._time_angle = 0.0
        self._last_close_time = 0.0
        self._popup_widget = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(38)
        self.setFont(QFont("Segoe UI", 10))

        view = QListView(self)
        view.setFrameShape(QFrame.Shape.NoFrame)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setView(view)

        self._popup_widget = MkDropdownPopup(self)

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def setView(self, itemView):
        super().setView(itemView)
        if hasattr(self, "_popup_widget") and self._popup_widget is not None:
            self._popup_widget.set_view(itemView)

    def showPopup(self):
        if time.time() - getattr(self, "_last_close_time", 0) < 0.25:
            return
        if self.count() == 0:
            return
        if not hasattr(self, "_popup_widget") or self._popup_widget is None:
            self._popup_widget = MkDropdownPopup(self)
        self._popup_widget.show_at_combo()

    def hidePopup(self):
        if hasattr(self, "_popup_widget") and self._popup_widget is not None:
            self._popup_widget.hide()
        super().hidePopup()

    def hideEvent(self, event):
        if hasattr(self, "_popup_widget") and self._popup_widget is not None:
            self._popup_widget.hide()
        super().hideEvent(event)


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
            """)

        if hasattr(self, "_popup_widget") and self._popup_widget is not None:
            self._popup_widget.update_theme_style()

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
            painter.setPen(Qt.PenStyle.NoPen)
            if self._hovered or self.hasFocus():
                glow = qcolor(primary, "#409EFF", 0.18)
                painter.setBrush(QBrush(glow))
                painter.drawRoundedRect(inset.adjusted(-3, -3, 3, 3), radius + 3, radius + 3)
            
            surface_color = t.get("--surface", "#1B2525")
            painter.setBrush(QBrush(qcolor(surface_color)))
            
            border_color = primary if (self._hovered or self.hasFocus()) else t.get("--border", "#2C3E3E")
            painter.setPen(QPen(qcolor(border_color), 1))
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
        if time.time() - getattr(self, "_last_close_time", 0) < 0.25:
            event.accept()
            return
        self._pressed = True
        self.update()
        if not self.isEditable():
            self.showPopup()
            event.accept()
            return
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
