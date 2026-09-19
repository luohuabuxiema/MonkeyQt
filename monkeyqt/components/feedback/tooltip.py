# -*- coding: utf-8 -*-
"""
MonkeyQt Tooltip & Popover Components.
Features:
- MkTooltipPopover: Speech-bubble popover with directional pointer arrow and multi-theme adaptation.
- MkInfoIcon / MkInfoIconButton: Modern vector info icon with circular badge hover and popover trigger.
- MkTooltip: Utility helper for attaching speech-bubble tooltips to any QWidget with zero boilerplate.
- create_field_header, create_input_field, create_switch_field: Helper functions for form fields with info hints.
"""

from typing import Optional, Tuple, Any
from PySide6.QtCore import Qt, QPoint, QPointF, QRect, QRectF, QObject, QEvent
from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QPolygonF,
    QColor,
    QBrush,
    QPen,
    QCursor,
    QFont,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    QApplication,
)

from monkeyqt.components.layout.widget import MkQWidget
from monkeyqt.icons import PhInfo
from monkeyqt.themes.engine import ThemeEngine


class MkTooltipPopover(MkQWidget):
    """
    Speech-bubble tooltip popover with pointer arrow.
    Benchmarked strictly against modern cloud platforms (Ultralytics HUB, OpenAI, etc.).
    Automatically adapts across all 68 MonkeyQt themes:
    - Light Mode: Pitch-black obsidian slate bubble (#0F172A), crisp white text (#FFFFFF)
    - Dark / OLED Mode: High-contrast bright bubble (#FFFFFF), crisp dark text (#09090B)
    - Glassmorphism Mode: Frosted translucent bubble with subtle border glow
    - Brutalism Mode: 2px solid black border, 0px sharp corner radius, hard shadow
    - Pixel Mode: 0px corner radius with pixelated contrast borders
    - Cyberpunk / Neon Mode: Dark bubble with neon primary accent border & soft glow
    """
    _instance: Optional["MkTooltipPopover"] = None

    @classmethod
    def get_instance(cls) -> "MkTooltipPopover":
        if cls._instance is None:
            cls._instance = MkTooltipPopover()
        return cls._instance

    @classmethod
    def show_popover(cls, target_widget: QWidget, text: str, theme_override: Optional[str] = None):
        """Display the popover anchored to target_widget."""
        if not text or not target_widget or not target_widget.isVisible():
            return
        inst = cls.get_instance()
        inst.set_content(text, theme_override=theme_override)
        inst.adjustSize()

        pop_w = inst.width()
        pop_h = inst.height()

        target_center_x = target_widget.mapToGlobal(QPoint(target_widget.width() // 2, 0)).x()
        target_top_y = target_widget.mapToGlobal(QPoint(0, 0)).y()
        target_bot_y = target_top_y + target_widget.height()

        screen = target_widget.screen() or QApplication.primaryScreen()
        screen_avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)

        # Default to appearing on top with pointer arrow pointing downwards
        arrow_position = 'bottom'
        pos_y = target_top_y - pop_h - 4

        # Flip downwards if too close to the screen top edge
        if pos_y < screen_avail.top() + 10:
            pos_y = target_bot_y + 4
            arrow_position = 'top'

        # Horizontal positioning clamped to screen bounds
        pos_x = target_center_x - pop_w // 2
        pos_x = max(screen_avail.left() + 12, min(screen_avail.right() - pop_w - 12, pos_x))

        inst.set_arrow_position(arrow_position)
        inst.move(pos_x, pos_y)
        inst.set_arrow_global_x(target_center_x)
        inst.show()
        inst.raise_()

    @classmethod
    def hide_popover(cls):
        """Dismiss the popover immediately."""
        if cls._instance and cls._instance.isVisible():
            cls._instance.hide()

    def __init__(self):
        super().__init__(None)
        self.setWindowFlags(
            Qt.WindowType.ToolTip
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._arrow_x = 0.5
        self._arrow_position = 'bottom'
        self._padding = 8
        self._style_meta = {}

        self.box_layout = QVBoxLayout(self)
        self.box_layout.setContentsMargins(
            self._padding + 12, self._padding + 8, self._padding + 12, 6 + 10
        )

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setTextFormat(Qt.TextFormat.PlainText)
        self.box_layout.addWidget(self.label)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(16)
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)

    def on_theme_changed(self, theme_name: str = ""):
        if self.isVisible() and self.label.text():
            self.set_content(self.label.text())
            self.update()

    def set_arrow_position(self, pos: str):
        self._arrow_position = pos
        p = self._padding
        if pos == 'bottom':
            self.box_layout.setContentsMargins(p + 12, p + 7, p + 12, 6 + 10)
        else:
            self.box_layout.setContentsMargins(p + 12, 6 + 10, p + 12, p + 7)

    def set_content(self, text: str, theme_override: Optional[str] = None):
        self.label.setText(text)

        # Retrieve current theme metadata
        is_dark = ThemeEngine.is_dark()
        is_brutal = ThemeEngine.is_brutal()
        is_pixel = ThemeEngine.is_pixel()
        is_glass = ThemeEngine.is_glass()
        curr_theme = (theme_override or ThemeEngine.current_theme() or "").lower()
        is_cyber = "cyber" in curr_theme or "neon" in curr_theme

        # Dynamic color and shape adaptation
        font_family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif'
        
        if is_dark:
            # Dark mode: Crisp bright card with dark charcoal text
            text_color = "#09090B"
            bg_color = QColor(255, 255, 255)
            border_color = QColor(0, 0, 0, 25)
            shadow_color = QColor(0, 0, 0, 95)
            shadow_blur = 18
            shadow_offset = (0, 4)
            corner_radius = 0.0 if (is_brutal or is_pixel) else 8.0
            border_width = 2.0 if is_brutal else 1.0
        else:
            # Light mode: Pitch-black obsidian slate card with crisp white text
            text_color = "#FFFFFF"
            bg_color = QColor(15, 23, 42)
            border_color = QColor(255, 255, 255, 28)
            shadow_color = QColor(0, 0, 0, 80)
            shadow_blur = 16
            shadow_offset = (0, 4)
            corner_radius = 0.0 if (is_brutal or is_pixel) else 8.0
            border_width = 2.0 if is_brutal else 1.0

        if is_brutal:
            # Brutalism: Pure white or bright high-contrast card with thick black border
            bg_color = QColor(255, 255, 255)
            text_color = "#000000"
            border_color = QColor(0, 0, 0)
            border_width = 2.0
            corner_radius = 0.0
            shadow_color = QColor(0, 0, 0, 220)
            shadow_blur = 0
            shadow_offset = (3, 3)
        elif is_glass:
            # Glassmorphism: Translucent acrylic frosted card with border reflection
            if is_dark:
                bg_color = QColor(255, 255, 255, 235)
                text_color = "#09090B"
                border_color = QColor(255, 255, 255, 120)
            else:
                bg_color = QColor(15, 23, 42, 218)
                text_color = "#FFFFFF"
                border_color = QColor(255, 255, 255, 60)
            corner_radius = 10.0
            border_width = 1.0
            shadow_color = QColor(0, 0, 0, 90)
            shadow_blur = 20
        elif is_cyber:
            # Cyberpunk / Glow: Dark bubble with neon primary accent border
            primary_hex = ThemeEngine.token("primary", "#3B82F6")
            bg_color = QColor(10, 15, 29)
            text_color = "#F8FAFC"
            border_color = QColor(primary_hex)
            border_width = 1.5
            corner_radius = 6.0
            shadow_color = QColor(border_color.red(), border_color.green(), border_color.blue(), 110)
            shadow_blur = 18

        self._style_meta = {
            "bg_color": bg_color,
            "border_color": border_color,
            "border_width": border_width,
            "corner_radius": corner_radius,
            "is_brutal": is_brutal,
        }

        self.label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-family: {font_family};
                font-size: 12px;
                line-height: 1.45;
                font-weight: {"600" if is_brutal else "400"};
                background: transparent;
            }}
        """)

        self.shadow.setColor(shadow_color)
        self.shadow.setBlurRadius(shadow_blur)
        self.shadow.setOffset(shadow_offset[0], shadow_offset[1])

        # Dynamic width matching the card aspect ratio
        fm = self.label.fontMetrics()
        single_line_w = fm.horizontalAdvance(text)
        if single_line_w < 260:
            target_w = max(160, single_line_w + 14)
        elif single_line_w < 520:
            target_w = 320
        else:
            target_w = 380
        self.label.setFixedWidth(target_w)

        self.adjustSize()

    def set_arrow_global_x(self, target_global_x: int):
        local_x = target_global_x - self.x()
        p = self._padding
        min_x = p + 16
        max_x = self.width() - p - 16
        self._arrow_x = max(min_x, min(max_x, local_x))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = self._padding
        arrow_h = 5.0
        arrow_w = 10.0

        bg_color = self._style_meta.get("bg_color", QColor(15, 23, 42))
        border_color = self._style_meta.get("border_color", QColor(255, 255, 255, 25))
        border_w = self._style_meta.get("border_width", 1.0)
        radius = self._style_meta.get("corner_radius", 8.0)

        if self._arrow_position == 'bottom':
            body_rect = QRectF(p, p, self.width() - 2 * p, self.height() - p - arrow_h - 1)
            ax = getattr(self, '_arrow_x', self.width() / 2.0)
            arrow = QPolygonF([
                QPointF(ax - arrow_w / 2.0, body_rect.bottom()),
                QPointF(ax + arrow_w / 2.0, body_rect.bottom()),
                QPointF(ax, self.height() - 1)
            ])
        else:
            body_rect = QRectF(p, arrow_h + 1, self.width() - 2 * p, self.height() - p - arrow_h - 1)
            ax = getattr(self, '_arrow_x', self.width() / 2.0)
            arrow = QPolygonF([
                QPointF(ax - arrow_w / 2.0, body_rect.top()),
                QPointF(ax + arrow_w / 2.0, body_rect.top()),
                QPointF(ax, 1)
            ])

        path = QPainterPath()
        if radius > 0:
            path.addRoundedRect(body_rect, radius, radius)
        else:
            path.addRect(body_rect)

        arrow_path = QPainterPath()
        arrow_path.addPolygon(arrow)

        bubble_path = path.united(arrow_path).simplified()

        painter.fillPath(bubble_path, QBrush(bg_color))
        painter.strokePath(bubble_path, QPen(border_color, border_w))


class MkInfoIcon(QLabel):
    """
    Hoverable vector info icon with circular badge hover effect and speech-bubble popover.
    Directly benchmarked against modern AI interfaces (Ultralytics HUB, LabelPaw, etc.).
    Automatically updates with MonkeyQt themes.
    """
    def __init__(self, hint_text: str = "", parent=None):
        super().__init__(parent)
        self.hint_text = hint_text
        self.setFixedSize(20, 20)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._is_hovered = False

        # React to theme changes
        ThemeEngine.instance().themeChanged.connect(self._on_theme_changed)
        self._update_appearance()

    def set_hint(self, text: str):
        """Update hint text dynamically."""
        self.hint_text = text

    def _on_theme_changed(self, theme_name: str):
        self._update_appearance()

    def _update_appearance(self):
        is_dark = ThemeEngine.is_dark()
        if is_dark:
            color = "#F4F4F5" if self._is_hovered else "#A1A1AA"
            bg = "background-color: rgba(255, 255, 255, 0.14); border-radius: 10px;" if self._is_hovered else "background: transparent; border: none;"
        else:
            color = "#09090B" if self._is_hovered else "#94A3B8"
            bg = "background-color: rgba(0, 0, 0, 0.08); border-radius: 10px;" if self._is_hovered else "background: transparent; border: none;"

        self.setStyleSheet(f"QLabel {{ {bg} }}")
        dpr = self.devicePixelRatio() if hasattr(self, "devicePixelRatio") else 1.0
        self.setPixmap(PhInfo.pixmap(size=13, color=color, weight="regular", dpr=max(1.0, float(dpr))))

    def show_tooltip(self):
        """Programmatically trigger showing the tooltip and circular hover badge."""
        self._is_hovered = True
        self._update_appearance()
        if self.hint_text:
            MkTooltipPopover.show_popover(self, self.hint_text)

    def hide_tooltip(self):
        """Programmatically hide the tooltip and reset badge."""
        self._is_hovered = False
        self._update_appearance()
        MkTooltipPopover.hide_popover()

    def enterEvent(self, event):
        self.show_tooltip()
        if event is not None:
            try:
                super().enterEvent(event)
            except Exception:
                pass

    def leaveEvent(self, event):
        cursor_pos = self.mapFromGlobal(QCursor.pos())
        if self.rect().contains(cursor_pos):
            return
        self.hide_tooltip()
        if event is not None:
            try:
                super().leaveEvent(event)
            except Exception:
                pass


# Backward-compatible alias
MkInfoIconButton = MkInfoIcon


class _MkTooltipFilter(QObject):
    """Event filter that manages showing and hiding speech-bubble tooltips for a widget."""
    def __init__(self, target_widget: QWidget, hint_text: str):
        super().__init__(target_widget)
        self.target_widget = target_widget
        self.hint_text = hint_text

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self.target_widget:
            if event.type() == QEvent.Type.Enter:
                if self.hint_text:
                    MkTooltipPopover.show_popover(self.target_widget, self.hint_text)
            elif event.type() in (QEvent.Type.Leave, QEvent.Type.Hide, QEvent.Type.Close):
                MkTooltipPopover.hide_popover()
        return super().eventFilter(watched, event)


class MkTooltip:
    """
    Utility helper for attaching speech-bubble tooltips to any QWidget.
    Usage:
        MkTooltip.attach(my_button, "Click to start model training")
        MkTooltip.show(my_button, "Hello bubble!")
        MkTooltip.hide()
        MkTooltip.detach(my_button)
    """
    _FILTERS = {}

    @classmethod
    def attach(cls, widget: QWidget, text: str):
        """Attach a modern bubble tooltip to any QWidget."""
        cls.detach(widget)
        if not text:
            return
        # Ensure native tooltip is removed to prevent double-popups
        widget.setToolTip("")
        flt = _MkTooltipFilter(widget, text)
        cls._FILTERS[widget] = flt
        widget.installEventFilter(flt)

    @classmethod
    def detach(cls, widget: QWidget):
        """Detach bubble tooltip from a widget."""
        flt = cls._FILTERS.pop(widget, None)
        if flt and widget:
            try:
                widget.removeEventFilter(flt)
            except RuntimeError:
                pass

    @classmethod
    def show(cls, target_widget: QWidget, text: str):
        """Show popover pointing at target_widget."""
        MkTooltipPopover.show_popover(target_widget, text)

    @classmethod
    def hide(cls):
        """Hide any currently visible popover."""
        MkTooltipPopover.hide_popover()


# =========================================================================
# Form Field Generation Helpers with Bubble Tooltips
# =========================================================================

def create_field_header(text: str, hint: str = "") -> QWidget:
    """
    Creates a standard field header with an optional MkInfoIcon bubble tooltip.
    """
    w = QWidget()
    w.setStyleSheet("background: transparent; border: none;")
    l = QHBoxLayout(w)
    l.setContentsMargins(0, 0, 0, 0)
    l.setSpacing(4)
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size: 13px; font-weight: 500;")
    l.addWidget(lbl)
    if hint:
        ic = MkInfoIcon(hint)
        l.addWidget(ic)
    l.addStretch()
    return w


def create_input_field(label_text: str, default_val: Any = "", hint: str = "") -> Tuple[QWidget, Any]:
    """
    Creates a standard labeled input field with an optional MkInfoIcon bubble tooltip.
    Returns: (container_widget, input_widget)
    """
    from monkeyqt.components.form.input import MkInput

    box = QVBoxLayout()
    box.setContentsMargins(0, 0, 0, 0)
    box.setSpacing(4)
    
    header = create_field_header(label_text, hint=hint)
    box.addWidget(header)
    
    inp = MkInput()
    inp.setText(str(default_val) if default_val is not None else "")
    inp.setStyleSheet("font-size: 12px; padding: 4px 8px;")
    box.addWidget(inp)
    
    container = QWidget()
    container.setStyleSheet("background: transparent; border: none;")
    container.setLayout(box)
    return container, inp


def create_switch_field(label_text: str, default_checked: bool = False, hint: str = "") -> Tuple[QWidget, Any]:
    """
    Creates a standard switch field with an optional MkInfoIcon bubble tooltip.
    Returns: (container_widget, switch_widget)
    """
    from monkeyqt.components.form.switch import MkSwitch

    w = QWidget()
    w.setStyleSheet("background: transparent; border: none;")
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 4, 4, 4)
    h.setSpacing(6)
    
    lbl = QLabel(label_text)
    lbl.setStyleSheet("font-size: 13px; font-weight: 500;")
    h.addWidget(lbl)
    if hint:
        ic = MkInfoIcon(hint)
        h.addWidget(ic)
    h.addStretch()
    
    sw = MkSwitch(checked=default_checked)
    h.addWidget(sw)
    return w, sw
