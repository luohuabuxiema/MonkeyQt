# -*- coding: utf-8 -*-
"""
MonkeyQt Tooltip & Popover Components.
Features:
- MkTooltipPopover: Speech-bubble popover with directional pointer arrow and multi-theme adaptation.
- MkInfoIcon / MkInfoIconButton: Modern vector info icon with circular badge hover and popover trigger.
- MkTooltip: Utility helper for attaching speech-bubble tooltips to any QWidget with zero boilerplate.
- create_field_header, create_input_field, create_switch_field: Helper functions for form fields with info hints.
"""

import re
from typing import Optional, Tuple, Any
from PySide6.QtCore import Qt, QPoint, QPointF, QRect, QRectF, QObject, QEvent, QTimer
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
    QPushButton,
)

from monkeyqt.components.layout.widget import MkQWidget
from monkeyqt.icons import PhInfo
from monkeyqt.themes.engine import ThemeEngine


class MkTooltipPopover(MkQWidget):
    """
    现代化气泡提示浮窗 (Speech-bubble Tooltip Popover)
    对标现代 AI 云平台 (Ultralytics HUB、LabelPaw 等) 标杆设计：
    - 亮色模式 (参考图三)：沉浸黑卡片 (#18181B / #121212)，纯白清晰文本 (#FFFFFF)，代码块标签与右上角关闭按钮；
    - 暗色模式 (参考图四)：纯白高反差卡片 (#FFFFFF)，深炭黑高清晰文本 (#09090B)，代码块标签与右上角关闭按钮；
    - 玻璃拟态风格：磨砂半透明浮层 + 微发光边缘反射；
    - 新野兽派 / 像素风格：粗黑边框、硬投影与高饱和纯色；
    - 赛博朋克风格：深炭黑浮层 + 霓虹主色描边。
    集成像素级平滑闭合路径抗锯齿绘制与智能防遮挡边缘对齐。
    """
    _instance: Optional["MkTooltipPopover"] = None

    @classmethod
    def get_instance(cls) -> "MkTooltipPopover":
        if cls._instance is None:
            cls._instance = MkTooltipPopover()
        return cls._instance

    @classmethod
    def show_popover(cls, target_widget: QWidget, text: str, theme_override: Optional[str] = None):
        """Display the popover anchored to target_widget with pixel precision."""
        if not text or not target_widget or not target_widget.isVisible():
            return
        inst = cls.get_instance()
        inst.cancel_close()
        inst._target_widget = target_widget
        inst.set_content(text, theme_override=theme_override)

        target_rect = QRect(target_widget.mapToGlobal(QPoint(0, 0)), target_widget.size())
        target_center_x = target_rect.center().x()

        screen = target_widget.screen() or QApplication.primaryScreen()
        screen_avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)

        top_boundary = screen_avail.top() + 8
        if target_widget.window():
            win_top = target_widget.window().mapToGlobal(QPoint(0, 0)).y()
            top_boundary = max(top_boundary, win_top + 45)

        padding = float(inst._padding)
        gap = 2  # Gap between arrow tip and target widget boundary

        # First pass: try bottom arrow (popover appears above target)
        arrow_position = 'bottom'
        inst.set_arrow_position(arrow_position)
        inst.adjustSize()
        pop_w = inst.width()
        pop_h = inst.height()

        pos_y = int(target_rect.top() - gap - (pop_h - padding))

        # If insufficient room above, flip to top arrow (popover appears below target)
        if pos_y < top_boundary:
            arrow_position = 'top'
            inst.set_arrow_position(arrow_position)
            inst.adjustSize()
            pop_w = inst.width()
            pop_h = inst.height()
            pos_y = int(target_rect.bottom() + gap - padding)

        # Clamped horizontal positioning centered on target widget
        pos_x = target_center_x - pop_w // 2
        pos_x = max(screen_avail.left() + 8, min(screen_avail.right() - pop_w - 8, pos_x))

        target_local_x = float(target_center_x - pos_x)

        inst.set_arrow_x(target_local_x)
        inst.move(pos_x, pos_y)
        inst.show()
        inst.raise_()

    @classmethod
    def show_popover_delayed(cls, target_widget: QWidget, text: str, delay_ms: int = 350, theme_override: Optional[str] = None):
        """
        Delayed popover trigger (Open Delay).
        Industry standard open delay: 300ms ~ 500ms (default 350ms).
        Prevents visual flicker when the cursor sweeps across table rows.
        If the popover is already showing, smoothly transitions to the new cell immediately.
        """
        if not text or not target_widget or not target_widget.isVisible():
            return
        inst = cls.get_instance()
        inst.cancel_close()

        if inst.isVisible():
            cls.show_popover(target_widget, text, theme_override=theme_override)
            return

        cls.cancel_open()
        inst._pending_target = target_widget
        inst._pending_text = text
        inst._pending_theme = theme_override
        inst._open_timer.start(delay_ms)

    @classmethod
    def cancel_open(cls):
        """Cancel any pending delayed popover open."""
        if cls._instance:
            cls._instance._open_timer.stop()
            cls._instance._pending_target = None
            cls._instance._pending_text = None
            cls._instance._pending_theme = None

    @classmethod
    def hide_popover(cls):
        """Dismiss the popover immediately and reset target widget hover state."""
        if cls._instance:
            cls.cancel_open()
            cls._instance._close_timer.stop()
            if cls._instance.isVisible():
                cls._instance.hide()
            if cls._instance._target_widget:
                try:
                    if hasattr(cls._instance._target_widget, "_update_appearance"):
                        cls._instance._target_widget._is_hovered = False
                        cls._instance._target_widget._update_appearance()
                except RuntimeError:
                    pass

    @classmethod
    def schedule_close(cls, delay_ms: int = 180):
        """Schedule automatic close after grace period unless re-entered."""
        if cls._instance:
            cls.cancel_open()
            if cls._instance.isVisible():
                cls._instance._close_timer.start(delay_ms)

    @classmethod
    def cancel_close(cls):
        """Cancel any pending auto-close."""
        if cls._instance:
            cls._instance._close_timer.stop()

    def _check_auto_close(self):
        """Grace timer callback: close popover if cursor is outside both anchor and popover."""
        cursor_pos = QCursor.pos()
        if self.isVisible() and self.geometry().adjusted(-4, -4, 4, 4).contains(cursor_pos):
            return
        if self._target_widget and self._target_widget.isVisible():
            try:
                tw_rect = QRect(self._target_widget.mapToGlobal(QPoint(0, 0)), self._target_widget.size())
                if tw_rect.adjusted(-6, -6, 6, 6).contains(cursor_pos):
                    return
            except Exception:
                pass
        self.hide_popover()

    def __init__(self):
        super().__init__(None)
        self.setWindowFlags(
            Qt.WindowType.ToolTip
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._target_widget: Optional[QWidget] = None
        self._arrow_x = 0.5
        self._arrow_position = 'bottom'
        self._padding = 10
        self._arrow_h = 6.0
        self._arrow_w = 12.0
        self._style_meta = {}

        self.box_layout = QVBoxLayout(self)
        self.box_layout.setContentsMargins(
            self._padding + 14, self._padding + 9, self._padding + 14, self._padding + 9
        )
        self.box_layout.setSpacing(0)

        # 内容标签 (支持富文本与代码高亮胶囊，移除关闭按钮后更开阔精致)
        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.setOpenExternalLinks(True)
        self.box_layout.addWidget(self.label)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(16)
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)

        # 鼠标移出区域平滑自动关闭定时器 (Grace Period Timer, 类似签到卡片悬停体验)
        self._close_timer = QTimer(self)
        self._close_timer.setSingleShot(True)
        self._close_timer.setInterval(180)
        self._close_timer.timeout.connect(self._check_auto_close)

        # 鼠标移入延迟展开定时器 (Open Delay Timer, 业界标准 300~500ms，杜绝鼠标扫过时的浮窗抖动)
        self._open_timer = QTimer(self)
        self._open_timer.setSingleShot(True)
        self._open_timer.timeout.connect(self._on_open_timer_timeout)
        self._pending_target = None
        self._pending_text = None
        self._pending_theme = None

    def _on_open_timer_timeout(self):
        target = self._pending_target
        text = self._pending_text
        theme = self._pending_theme
        self._pending_target = None
        self._pending_text = None
        self._pending_theme = None
        if target and text and target.isVisible():
            self.show_popover(target, text, theme_override=theme)


    def on_theme_changed(self, theme_name: str = ""):
        if self.isVisible() and self.label.text():
            self.set_content(self.label.text())
            self.update()

    def set_arrow_position(self, pos: str):
        self._arrow_position = pos
        p = self._padding
        ah = int(self._arrow_h)
        if pos == 'bottom':
            self.box_layout.setContentsMargins(p + 14, p + 9, p + 14, p + ah + 9)
        else:
            self.box_layout.setContentsMargins(p + 14, p + ah + 9, p + 14, p + 9)

    def set_arrow_x(self, local_x: float):
        p = float(self._padding)
        min_x = p + 16.0
        max_x = float(self.width()) - p - 16.0
        self._arrow_x = max(min_x, min(max_x, float(local_x)))
        self.update()

    def set_content(self, text: str, theme_override: Optional[str] = None):
        # Retrieve current theme metadata
        is_dark = ThemeEngine.is_dark()
        is_brutal = ThemeEngine.is_brutal()
        is_pixel = ThemeEngine.is_pixel()
        is_glass = ThemeEngine.is_glass()
        curr_theme = (theme_override or ThemeEngine.current_theme() or "").lower()
        is_cyber = "cyber" in curr_theme or "neon" in curr_theme

        font_family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif'

        if is_dark:
            # 暗黑主题下 (参考图四)：高对比度纯白气泡卡片，深黑字
            text_color = "#09090B"
            bg_color = QColor(255, 255, 255)
            border_color = QColor(0, 0, 0, 30)
            shadow_color = QColor(0, 0, 0, 100)
            shadow_blur = 18
            shadow_offset = (0, 4)
            corner_radius = 0.0 if (is_brutal or is_pixel) else 10.0
            border_width = 2.0 if is_brutal else 1.0
            code_bg = "#F4F4F5"
            code_text = "#18181B"
            code_border = "#E4E4E7"
            link_color = "#2563EB"
        else:
            # 浅色/默认雅致亮色下 (参考图三)：沉浸黑气泡卡片，纯白清晰文字
            text_color = "#FFFFFF"
            bg_color = QColor(24, 24, 27)
            border_color = QColor(255, 255, 255, 36)
            shadow_color = QColor(0, 0, 0, 120)
            shadow_blur = 16
            shadow_offset = (0, 4)
            corner_radius = 0.0 if (is_brutal or is_pixel) else 10.0
            border_width = 2.0 if is_brutal else 1.0
            code_bg = "#333338"
            code_text = "#FFFFFF"
            code_border = "rgba(255, 255, 255, 0.10)"
            link_color = "#60A5FA"

        if is_brutal:
            bg_color = QColor(255, 255, 255)
            text_color = "#000000"
            border_color = QColor(0, 0, 0)
            border_width = 2.0
            corner_radius = 0.0
            shadow_color = QColor(0, 0, 0, 220)
            shadow_blur = 0
            shadow_offset = (3, 3)
            code_bg = "#E2E8F0"
            code_text = "#000000"
            code_border = "#000000"
            link_color = "#000000"
        elif is_glass:
            if is_dark:
                bg_color = QColor(255, 255, 255, 235)
                text_color = "#09090B"
                border_color = QColor(255, 255, 255, 120)
            else:
                bg_color = QColor(24, 24, 27, 225)
                text_color = "#FFFFFF"
                border_color = QColor(255, 255, 255, 60)
            corner_radius = 12.0
            border_width = 1.0
            shadow_color = QColor(0, 0, 0, 90)
            shadow_blur = 20
        elif is_cyber:
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

        # 格式化富文本 (支持 `code` 与 Learn more 链接)
        code_style = f'background-color: {code_bg}; color: {code_text}; font-family: Consolas, monospace; font-size: 11px;'
        formatted = re.sub(r"`([^`]+)`", rf'<code style="{code_style}">&nbsp;\1&nbsp;</code>', text)
        link_style = f'color: {link_color}; text-decoration: none; font-weight: 500;'
        formatted = re.sub(r"(Learn more\s*[↗→]?)", rf'<a href="#" style="{link_style}">\1</a>', formatted)

        self.label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-family: {font_family};
                font-size: 12px;
                font-weight: {"600" if is_brutal else "400"};
                background: transparent;
                border: none;
                padding: 2px 0px;
            }}
        """)
        self.label.setText(formatted)

        self.shadow.setColor(shadow_color)
        self.shadow.setBlurRadius(shadow_blur)
        self.shadow.setOffset(shadow_offset[0], shadow_offset[1])

        # 根据纯文本长度动态伸缩卡片宽度
        plain_len = len(re.sub(r"<[^>]+>", "", formatted))
        if plain_len < 25:
            target_w = max(180, plain_len * 12 + 40)
        elif plain_len < 60:
            target_w = 270
        elif plain_len < 100:
            target_w = 320
        else:
            target_w = 360
        self.label.setFixedWidth(int(target_w))
        self.adjustSize()

    def enterEvent(self, event):
        self.cancel_close()
        if event is not None:
            try:
                super().enterEvent(event)
            except Exception:
                pass

    def leaveEvent(self, event):
        self.schedule_close(180)
        if event is not None:
            try:
                super().leaveEvent(event)
            except Exception:
                pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = float(self._padding)
        arrow_h = float(self._arrow_h)
        arrow_w = float(self._arrow_w)

        bg_color = self._style_meta.get("bg_color", QColor(24, 24, 27))
        border_color = self._style_meta.get("border_color", QColor(255, 255, 255, 36))
        border_w = float(self._style_meta.get("border_width", 1.0))
        radius = float(self._style_meta.get("corner_radius", 10.0))

        w = float(self.width())
        h = float(self.height())
        rect = QRectF(p, p, w - 2.0 * p, h - 2.0 * p)

        path = QPainterPath()
        ax = getattr(self, '_arrow_x', w / 2.0)
        min_ax = rect.left() + radius + arrow_w / 2.0 + 2.0
        max_ax = rect.right() - radius - arrow_w / 2.0 - 2.0
        if min_ax <= max_ax:
            ax = max(min_ax, min(max_ax, ax))
        else:
            ax = rect.center().x()

        if self._arrow_position == 'bottom':
            body = QRectF(rect.left(), rect.top(), rect.width(), rect.height() - arrow_h)
            path.moveTo(body.left() + radius, body.top())
            path.lineTo(body.right() - radius, body.top())
            path.arcTo(QRectF(body.right() - 2.0 * radius, body.top(), 2.0 * radius, 2.0 * radius), 90, -90)
            path.lineTo(body.right(), body.bottom() - radius)
            path.arcTo(QRectF(body.right() - 2.0 * radius, body.bottom() - 2.0 * radius, 2.0 * radius, 2.0 * radius), 0, -90)
            path.lineTo(ax + arrow_w / 2.0, body.bottom())
            path.lineTo(ax, rect.bottom())
            path.lineTo(ax - arrow_w / 2.0, body.bottom())
            path.lineTo(body.left() + radius, body.bottom())
            path.arcTo(QRectF(body.left(), body.bottom() - 2.0 * radius, 2.0 * radius, 2.0 * radius), 270, -90)
            path.lineTo(body.left(), body.top() + radius)
            path.arcTo(QRectF(body.left(), body.top(), 2.0 * radius, 2.0 * radius), 180, -90)
            path.closeSubpath()
        else:
            body = QRectF(rect.left(), rect.top() + arrow_h, rect.width(), rect.height() - arrow_h)
            path.moveTo(body.left() + radius, body.top())
            path.lineTo(ax - arrow_w / 2.0, body.top())
            path.lineTo(ax, rect.top())
            path.lineTo(ax + arrow_w / 2.0, body.top())
            path.lineTo(body.right() - radius, body.top())
            path.arcTo(QRectF(body.right() - 2.0 * radius, body.top(), 2.0 * radius, 2.0 * radius), 90, -90)
            path.lineTo(body.right(), body.bottom() - radius)
            path.arcTo(QRectF(body.right() - 2.0 * radius, body.bottom() - 2.0 * radius, 2.0 * radius, 2.0 * radius), 0, -90)
            path.lineTo(body.left() + radius, body.bottom())
            path.arcTo(QRectF(body.left(), body.bottom() - 2.0 * radius, 2.0 * radius, 2.0 * radius), 270, -90)
            path.lineTo(body.left(), body.top() + radius)
            path.arcTo(QRectF(body.left(), body.top(), 2.0 * radius, 2.0 * radius), 180, -90)
            path.closeSubpath()

        painter.fillPath(path, QBrush(bg_color))
        painter.strokePath(path, QPen(border_color, border_w))


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
        MkTooltipPopover.cancel_close()
        self.show_tooltip()
        if event is not None:
            try:
                super().enterEvent(event)
            except Exception:
                pass

    def leaveEvent(self, event):
        MkTooltipPopover.schedule_close(180)
        if event is not None:
            try:
                super().leaveEvent(event)
            except Exception:
                pass

    def mousePressEvent(self, event):
        popover = MkTooltipPopover.get_instance()
        if popover.isVisible():
            self.hide_tooltip()
        else:
            self.show_tooltip()
        event.accept()


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
                MkTooltipPopover.cancel_close()
                if self.hint_text:
                    MkTooltipPopover.show_popover(self.target_widget, self.hint_text)
            elif event.type() == QEvent.Type.Leave:
                MkTooltipPopover.schedule_close(180)
            elif event.type() in (QEvent.Type.Hide, QEvent.Type.Close):
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
