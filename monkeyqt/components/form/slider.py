from PySide6.QtCore import Property, QEvent, QRectF, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QLabel,
    QSlider,
    QSizePolicy,
    QStyle,
    QStyleOptionSlider,
    QVBoxLayout,
    QWidget,
)

from monkeyqt.components.layout.widget import MkQWidget
from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import darken, lighten, luminance, qcolor, qss_color


def _contrast_ratio(color_a, color_b):
    light, dark = sorted((luminance(color_a), luminance(color_b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def _alpha_color(value, alpha):
    color = qcolor(value)
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha / 255:.3f})"

class MkBaseSlider(QSlider):
    """
    内部自定义 QSlider，重写 wheelEvent 以防止鼠标滚轮误触。
    只有当滑块获得焦点（被点击过）时，滚轮才会改变数值；否则忽略该事件以使父容器可以正常滚动。
    """
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self._visual_palette = None
        self._handle_hovered = False
        self.setMouseTracking(True)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()

    def set_visual_palette(self, palette):
        self._visual_palette = dict(palette)
        self.update()

    def set_handle_hovered(self, hovered):
        hovered = bool(hovered)
        if hovered != self._handle_hovered:
            self._handle_hovered = hovered
            self.update()

    def _handle_center(self):
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        handle_size = 18
        if self.orientation() == Qt.Orientation.Horizontal:
            span = max(0, self.width() - handle_size)
            position = QStyle.sliderPositionFromValue(
                self.minimum(), self.maximum(), self.value(), span, option.upsideDown
            )
            return handle_size / 2 + position, self.height() / 2

        span = max(0, self.height() - handle_size)
        position = QStyle.sliderPositionFromValue(
            self.minimum(), self.maximum(), self.value(), span, option.upsideDown
        )
        return self.width() / 2, handle_size / 2 + position

    def handle_rect(self):
        """Return the geometry of the custom-painted 18px handle."""
        center_x, center_y = self._handle_center()
        return QRectF(center_x - 9, center_y - 9, 18, 18).toAlignedRect()

    def paintEvent(self, event):
        palette = self._visual_palette
        if not palette:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        flat = bool(palette["flat"])
        track_size = 5 if flat else 4
        track_radius = 0 if flat else track_size / 2
        handle_size = 18
        center_x, center_y = self._handle_center()

        if self.orientation() == Qt.Orientation.Horizontal:
            track = QRectF(
                handle_size / 2,
                center_y - track_size / 2,
                max(0, self.width() - handle_size),
                track_size,
            )
        else:
            track = QRectF(
                center_x - track_size / 2,
                handle_size / 2,
                track_size,
                max(0, self.height() - handle_size),
            )

        enabled = self.isEnabled()
        track_color = palette["track"] if enabled else palette["disabled_track"]
        active_color = palette["active"] if enabled else palette["disabled_active"]
        handle_color = palette["handle"] if enabled else palette["disabled_handle"]
        handle_border = palette["handle_border"] if enabled else palette["disabled_active"]

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(qcolor(track_color))
        painter.drawRoundedRect(track, track_radius, track_radius)

        option = QStyleOptionSlider()
        self.initStyleOption(option)
        min_position = QStyle.sliderPositionFromValue(
            self.minimum(), self.maximum(), self.minimum(),
            int(track.width() if self.orientation() == Qt.Orientation.Horizontal else track.height()),
            option.upsideDown,
        )
        if self.orientation() == Qt.Orientation.Horizontal:
            min_center = track.left() + min_position
            active = QRectF(
                min(min_center, center_x), track.top(),
                abs(center_x - min_center), track.height(),
            )
        else:
            min_center = track.top() + min_position
            active = QRectF(
                track.left(), min(min_center, center_y),
                track.width(), abs(center_y - min_center),
            )
        painter.setBrush(qcolor(active_color))
        painter.drawRoundedRect(active, track_radius, track_radius)

        handle = QRectF(
            center_x - handle_size / 2,
            center_y - handle_size / 2,
            handle_size,
            handle_size,
        )
        interactive = enabled and (self._handle_hovered or self.hasFocus() or self.isSliderDown())
        if interactive and not flat:
            ring = QRectF(center_x - 14, center_y - 14, 28, 28)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(qcolor(palette["hover_ring"]))
            painter.drawEllipse(ring)

        if not flat:
            shadow = handle.translated(0, 1)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, 42 if enabled else 20))
            painter.drawEllipse(shadow)

        painter.setBrush(qcolor(handle_color))
        painter.setPen(QPen(qcolor(handle_border), 2 if flat else 1))
        if flat:
            painter.drawRect(handle.adjusted(1, 1, -1, -1))
        else:
            painter.drawEllipse(handle.adjusted(0.5, 0.5, -0.5, -0.5))
        painter.end()

class MkSlider(MkQWidget):
    """
    MkSlider 组件 - 完美实现滑动条在所有内置 68 种主题风格中的 3D 浮雕与毛玻璃特效，
    内置跟随手柄移动的当前数值标签。
    """
    valueChanged = Signal(int)
    sliderMoved = Signal(int)
    sliderPressed = Signal()
    sliderReleased = Signal()

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent)
        self._orientation = orientation
        self._show_value = True
        self._formatter = None

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 20 if orientation == Qt.Orientation.Horizontal else 0)
        self._layout.setSpacing(0 if orientation == Qt.Orientation.Horizontal else 4)

        self.value_label = QLabel("0", self)
        self.value_label.setObjectName("themedSliderValue")
        if orientation == Qt.Orientation.Horizontal:
            self.value_label.setFixedHeight(20)
            self.value_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        else:
            self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider = MkBaseSlider(orientation)
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        if orientation == Qt.Orientation.Horizontal:
            self.slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.slider.setFixedHeight(30)
        else:
            self.slider.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            self.slider.setMinimumHeight(96)
        self.slider.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.slider.installEventFilter(self)
        self.slider.valueChanged.connect(self._on_value_changed)
        self.slider.sliderMoved.connect(self.sliderMoved)
        self.slider.sliderPressed.connect(self.sliderPressed)
        self.slider.sliderReleased.connect(self.sliderReleased)

        if orientation == Qt.Orientation.Horizontal:
            self.setMinimumHeight(50)
            self._layout.addWidget(self.slider)
            self.value_label.raise_()
        else:
            self.setMinimumWidth(52)
            self._layout.addWidget(self.slider, 1)
            self._layout.addWidget(self.value_label)

        self.set_theme_style()

    def eventFilter(self, obj, event):
        if obj == self.slider:
            event_type = event.type()
            if event_type == QEvent.Type.HoverLeave:
                self.slider.set_handle_hovered(False)
                if not self.slider.isSliderDown():
                    self.slider.clearFocus()
            elif event_type in (QEvent.Type.HoverEnter, QEvent.Type.HoverMove):
                position = event.position().toPoint()
                self._sync_handle_interaction(position)
            elif event_type == QEvent.Type.MouseButtonRelease:
                # QSlider updates ``sliderDown`` after the event filter returns.
                # Re-evaluate on the next cycle so a drag can finish normally,
                # then drop focus when the pointer was released off the handle.
                position = event.position().toPoint()
                QTimer.singleShot(0, lambda pos=position: self._sync_handle_interaction(pos))
            if event_type in (
                QEvent.Type.HoverEnter,
                QEvent.Type.HoverLeave,
                QEvent.Type.HoverMove,
                QEvent.Type.FocusIn,
                QEvent.Type.FocusOut,
                QEvent.Type.MouseButtonPress,
                QEvent.Type.MouseButtonRelease,
            ):
                self.slider.update()
                QTimer.singleShot(0, self._position_value_label)
            elif event_type in (QEvent.Type.Resize, QEvent.Type.StyleChange):
                QTimer.singleShot(0, self._position_value_label)
        return super().eventFilter(obj, event)

    def _sync_handle_interaction(self, position):
        """Keep hover/focus active only while the pointer is over the handle."""
        over_handle = self.slider.handle_rect().adjusted(-5, -5, 5, 5).contains(position)
        self.slider.set_handle_hovered(over_handle)
        if not over_handle and not self.slider.isSliderDown():
            self.slider.clearFocus()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_value_label()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._position_value_label)

    def on_theme_changed(self, theme_name: str = ""):
        self.set_theme_style(theme_name)

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        fg = t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        palette = self._slider_palette()

        label_color = t.get("--glass-text", fg) if t.is_glass() else fg
        if not t.is_brutal() and not t.is_pixel():
            label_color = muted
        self.value_label.setStyleSheet(f"""
            QLabel#themedSliderValue {{
                background: transparent;
                color: {label_color};
                font-size: 13px;
                font-weight: 500;
                border: none;
                padding: 0px;
            }}
            QLabel#themedSliderValue:disabled {{ color: {palette['disabled_text']}; }}
        """)

        if self._orientation == Qt.Orientation.Horizontal:
            qss = self._horizontal_qss(palette)
        else:
            qss = self._vertical_qss(palette)
        self.slider.set_visual_palette(palette)
        self.slider.setStyleSheet(qss)
        self.update()
        QTimer.singleShot(0, self._position_value_label)

    def _slider_palette(self):
        """Build a front-end-like slider palette from the active theme tokens."""
        t = ThemeEngine
        bg = t.get("--bg", "#FFFFFF")
        fg = t.get("--fg", "#1E293B")
        primary = t.get("--primary", "#409EFF")
        surface = t.get("--surface", bg)
        surface_muted = t.get("--surface-muted", "#E5E7EB")
        border = t.get("--border", "#D1D5DB")
        muted = t.get("--text-muted", "#64748B")
        flat = t.is_brutal() or t.is_pixel()

        if flat:
            track = "#FFFFFF"
            active = primary
            handle = primary
            handle_border = "#000000"
            hover_ring = "#000000"
        elif t.is_glow():
            track = darken(surface_muted, 0.20) if t.is_dark() else surface_muted
            active = primary
            handle = "#FFFFFF" if t.is_dark() else surface
            handle_border = primary
            hover_ring = _alpha_color(primary, 72)
        elif t.is_glass():
            track = t.get("--glass-surface", surface_muted)
            active = primary
            handle = "rgba(255, 255, 255, 245)"
            handle_border = t.get("--glass-border", border)
            hover_ring = _alpha_color(primary, 58)
        elif t.is_neumorphic():
            track = darken(bg, 0.08)
            active = primary if _contrast_ratio(primary, track) >= 1.45 else fg
            handle = lighten(bg, 0.05)
            handle_border = border
            hover_ring = _alpha_color(primary, 46)
        else:
            # Neutral light/dark themes mirror modern web sliders: dark progress
            # on light surfaces, light progress on dark surfaces.
            track = surface_muted
            active = fg
            if _contrast_ratio(active, track) < 1.45:
                active = primary
            handle = "#FFFFFF" if t.is_dark() else surface
            if luminance(handle) < 0.72:
                handle = "#F8FAFC"
            handle_border = muted if t.is_dark() else border
            hover_ring = _alpha_color(primary, 54)

        return {
            "track": qss_color(track, surface_muted),
            "active": qss_color(active, primary),
            "handle": qss_color(handle, "#FFFFFF"),
            "handle_border": qss_color(handle_border, border),
            "hover_ring": hover_ring,
            "disabled_track": qss_color(surface_muted, "#E5E7EB"),
            "disabled_active": qss_color(muted, "#94A3B8"),
            "disabled_handle": qss_color(surface, "#FFFFFF"),
            "disabled_text": qss_color(muted, "#94A3B8"),
            "flat": flat,
        }

    def _horizontal_qss(self, palette):
        # Visuals are painted by MkBaseSlider. Transparent subcontrols retain
        # predictable Qt hit-testing geometry on every platform and style.
        return f"""
            QSlider {{
                min-height: 30px;
                border: none;
                background: transparent;
                outline: none;
            }}
            QSlider::groove:horizontal {{
                border: none;
                height: 4px;
                background: transparent;
            }}
            QSlider::sub-page:horizontal,
            QSlider::add-page:horizontal {{
                background: transparent;
            }}
            QSlider::handle:horizontal {{
                background: transparent;
                border: none;
                width: 18px;
                height: 18px;
                margin: -7px 0;
            }}
        """

    def _vertical_qss(self, palette):
        return f"""
            QSlider {{
                min-width: 30px;
                border: none;
                background: transparent;
                outline: none;
            }}
            QSlider::groove:vertical {{
                border: none;
                width: 4px;
                background: transparent;
            }}
            QSlider::sub-page:vertical,
            QSlider::add-page:vertical {{
                background: transparent;
            }}
            QSlider::handle:vertical {{
                background: transparent;
                border: none;
                width: 18px;
                height: 18px;
                margin: 0 -7px;
            }}
        """

    def _position_value_label(self):
        if self._orientation != Qt.Orientation.Horizontal or not self._show_value:
            return

        text_width = self.value_label.fontMetrics().horizontalAdvance(self.value_label.text())
        label_width = max(44, text_width + 12)
        self.value_label.resize(label_width, 20)

        handle_rect = self.slider.handle_rect()
        center = self.slider.mapTo(self, handle_rect.center())
        x = max(0, min(center.x() - label_width // 2, self.width() - label_width))
        y = min(self.height() - self.value_label.height(), self.slider.geometry().bottom() + 1)
        self.value_label.move(x, max(0, y))
        self.value_label.raise_()

    def _on_value_changed(self, value):
        display_text = self._formatter(value) if self._formatter else str(value)
        self.value_label.setText(display_text)
        self._position_value_label()
        self.valueChanged.emit(value)

    def setRange(self, min_val, max_val):
        self.slider.setRange(min_val, max_val)
        self._position_value_label()

    def minimum(self) -> int:
        return self.slider.minimum()

    def maximum(self) -> int:
        return self.slider.maximum()

    def setMinimum(self, min_val: int):
        self.slider.setMinimum(min_val)
        self._position_value_label()

    def setMaximum(self, max_val: int):
        self.slider.setMaximum(max_val)
        self._position_value_label()

    def setValue(self, val):
        self.slider.setValue(val)
        self.value_label.setText(self._formatter(val) if self._formatter else str(val))
        self._position_value_label()

    def value(self):
        return self.slider.value()

    def setTracking(self, enable: bool):
        self.slider.setTracking(enable)

    def hasTracking(self) -> bool:
        return self.slider.hasTracking()

    def setSingleStep(self, step):
        self.slider.setSingleStep(step)

    def set_formatter(self, formatter_func):
        self._formatter = formatter_func
        self.value_label.setText(formatter_func(self.value()) if formatter_func else str(self.value()))
        self._position_value_label()

    @Property(bool)
    def show_value(self):
        return self._show_value

    @show_value.setter
    def show_value(self, val):
        self._show_value = bool(val)
        self.value_label.setVisible(self._show_value)
        if self._show_value:
            QTimer.singleShot(0, self._position_value_label)
