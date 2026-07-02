# -*- coding: utf-8 -*-
from PySide6.QtCore import Property, QEvent, Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QSizePolicy, QToolTip, QVBoxLayout, QWidget

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import darken, lighten, parse_px, readable_text

class MkSlider(QWidget):
    """
    MkSlider 组件 - 完美实现滑动条在所有内置 68 种主题风格中的 3D 浮雕与毛玻璃特效，
    内置当前数值提示标签与高精度气泡提示。
    """
    valueChanged = Signal(int)

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent)
        self._orientation = orientation
        self._show_value = True
        self._formatter = None

        self._layout = QHBoxLayout(self) if orientation == Qt.Orientation.Horizontal else QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)

        self.value_label = QLabel("0")
        self.value_label.setObjectName("themedSliderValue")
        if orientation == Qt.Orientation.Horizontal:
            self.value_label.setFixedWidth(42)
            self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        else:
            self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider = QSlider(orientation)
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.slider.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.slider.installEventFilter(self)
        self.slider.valueChanged.connect(self._on_value_changed)

        if orientation == Qt.Orientation.Horizontal:
            self._layout.addWidget(self.value_label)
            self._layout.addWidget(self.slider, 1)
        else:
            self._layout.addWidget(self.slider, 1)
            self._layout.addWidget(self.value_label)

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def eventFilter(self, obj, event):
        if obj == self.slider and event.type() in (QEvent.Type.HoverEnter, QEvent.Type.HoverLeave, QEvent.Type.HoverMove):
            self.slider.update()
        return super().eventFilter(obj, event)

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        radius = parse_px(t.get("--radius", "6px"), 6, 0, 24)
        handle_radius = 8 if not t.is_brutal() and not t.is_pixel() else 0
        handle_size = 16
        handle_hover = 20

        if t.is_neumorphic():
            groove = darken(t.get("--bg", "#F5F5F5"), 0.08)
            handle = lighten(t.get("--bg", "#F5F5F5"), 0.05)
            handle_border = "rgba(255, 255, 255, 180)"
        elif t.is_glass():
            groove = t.get("--glass-surface", "rgba(255, 255, 255, 70)")
            handle = "rgba(255, 255, 255, 235)"
            handle_border = t.get("--glass-border", "rgba(255, 255, 255, 120)")
        elif t.is_glow():
            groove = "#1E293B"
            handle = primary
            handle_border = primary
        elif t.is_brutal() or t.is_pixel():
            groove = "#FFFFFF"
            handle = primary
            handle_border = "#000000"
            handle_size = 18
            handle_hover = 18
        else:
            groove = t.get("--surface-muted", "#E5E7EB")
            handle = primary
            handle_border = "#FFFFFF"

        label_color = t.get("--glass-text", fg) if t.is_glass() else fg
        self.value_label.setStyleSheet(f"""
            QLabel#themedSliderValue {{
                background: transparent;
                color: {label_color};
                font-size: 12px;
                font-weight: 600;
            }}
        """)

        if self._orientation == Qt.Orientation.Horizontal:
            qss = self._horizontal_qss(primary, groove, handle, handle_border, radius, handle_radius, handle_size, handle_hover, t)
        else:
            qss = self._vertical_qss(primary, groove, handle, handle_border, radius, handle_radius, handle_size, handle_hover, t)
        self.slider.setStyleSheet(qss)
        self.update()

    def _horizontal_qss(self, primary, groove, handle, handle_border, radius, handle_radius, handle_size, handle_hover, t):
        border = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {handle_border}"
        sub_border = "1px solid #000000" if t.is_brutal() or t.is_pixel() else "none"
        return f"""
            QSlider:horizontal {{
                min-height: 28px;
                border: none;
                background: transparent;
            }}
            QSlider::groove:horizontal {{
                border: {sub_border};
                height: 6px;
                background: {groove};
                border-radius: {min(radius, 6)}px;
            }}
            QSlider::sub-page:horizontal {{
                background: {primary};
                border-radius: {min(radius, 6)}px;
            }}
            QSlider::handle:horizontal {{
                background: {handle};
                border: {border};
                width: {handle_size}px;
                height: {handle_size}px;
                margin: -8px 0;
                border-radius: {handle_radius}px;
            }}
            QSlider::handle:horizontal:hover {{
                width: {handle_hover}px;
                height: {handle_hover}px;
                margin: -10px 0;
                border-radius: {0 if handle_radius == 0 else handle_hover // 2}px;
                background: {primary if t.is_glass() else handle};
            }}
        """

    def _vertical_qss(self, primary, groove, handle, handle_border, radius, handle_radius, handle_size, handle_hover, t):
        border = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {handle_border}"
        sub_border = "1px solid #000000" if t.is_brutal() or t.is_pixel() else "none"
        return f"""
            QSlider:vertical {{
                min-width: 28px;
                border: none;
                background: transparent;
            }}
            QSlider::groove:vertical {{
                border: {sub_border};
                width: 6px;
                background: {groove};
                border-radius: {min(radius, 6)}px;
            }}
            QSlider::sub-page:vertical {{
                background: {primary};
                border-radius: {min(radius, 6)}px;
            }}
            QSlider::handle:vertical {{
                background: {handle};
                border: {border};
                width: {handle_size}px;
                height: {handle_size}px;
                margin: 0 -8px;
                border-radius: {handle_radius}px;
            }}
            QSlider::handle:vertical:hover {{
                width: {handle_hover}px;
                height: {handle_hover}px;
                margin: 0 -10px;
                border-radius: {0 if handle_radius == 0 else handle_hover // 2}px;
                background: {primary if t.is_glass() else handle};
            }}
        """

    def _on_value_changed(self, value):
        display_text = self._formatter(value) if self._formatter else str(value)
        self.value_label.setText(display_text)
        if self.slider.isSliderDown():
            QToolTip.showText(QCursor.pos(), display_text, self.slider)
        self.valueChanged.emit(value)

    def setRange(self, min_val, max_val):
        self.slider.setRange(min_val, max_val)

    def setValue(self, val):
        self.slider.setValue(val)
        self.value_label.setText(self._formatter(val) if self._formatter else str(val))

    def value(self):
        return self.slider.value()

    def setSingleStep(self, step):
        self.slider.setSingleStep(step)

    def set_formatter(self, formatter_func):
        self._formatter = formatter_func
        self.value_label.setText(formatter_func(self.value()) if formatter_func else str(self.value()))

    @Property(bool)
    def show_value(self):
        return self._show_value

    @show_value.setter
    def show_value(self, val):
        self._show_value = bool(val)
        self.value_label.setVisible(self._show_value)
