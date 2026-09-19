"""
QWidget Icon Component for monkeyqt-icons.
Enables using icons as interactive Qt widgets directly in layouts.
"""

from typing import Union, Optional
from .qt_compat import QtCore, QtGui, QtWidgets
from .core import PhosphorEngine, _parse_color, _render_pixmap_cached, PASCAL_TO_NAME


class PhIconWidget(QtWidgets.QWidget):
    """
    A standalone Qt Widget component for Phosphor Icons.
    Supports dynamic properties, click signals, and hover tinting.
    """

    clicked = QtCore.Signal()

    def __init__(
        self,
        icon: str = "house",
        size: int = 24,
        color: Union[str, QtGui.QColor, None] = None,
        weight: str = "regular",
        secondary_color: Union[str, QtGui.QColor, None] = None,
        secondary_opacity: float = 0.2,
        mirrored: bool = False,
        rotation: int = 0,
        hover_color: Union[str, QtGui.QColor, None] = None,
        parent: Optional[QtWidgets.QWidget] = None
    ):
        super().__init__(parent)
        self._icon_name = PASCAL_TO_NAME.get(icon, icon).lower()
        self._size = size
        self._color = color or "currentColor"
        self._hover_color = hover_color
        self._weight = weight
        self._secondary_color = secondary_color
        self._secondary_opacity = secondary_opacity
        self._mirrored = mirrored
        self._rotation = rotation
        self._is_hovered = False

        self.setFixedSize(self._size, self._size)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_Hover, True)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        try:
            from monkeyqt.themes import ThemeEngine
            ThemeEngine.instance().themeChanged.connect(self._on_theme_changed)
        except Exception:
            pass

    def _on_theme_changed(self, theme_name: str = ""):
        self.update()

    def set_icon(self, icon: str):
        self._icon_name = PASCAL_TO_NAME.get(icon, icon).lower()
        self.update()

    def set_color(self, color: Union[str, QtGui.QColor]):
        self._color = color
        self.update()

    def set_weight(self, weight: str):
        self._weight = weight
        self.update()

    def set_size(self, size: int):
        self._size = size
        self.setFixedSize(self._size, self._size)
        self.update()

    def enterEvent(self, event):
        if self._hover_color:
            self._is_hovered = True
            self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._hover_color:
            self._is_hovered = False
            self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event: QtGui.QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        active_color = self._hover_color if (self._is_hovered and self._hover_color) else self._color
        c_str = _parse_color(active_color)
        sc_str = _parse_color(self._secondary_color) if self._secondary_color else None

        dpr = self.devicePixelRatioF()
        pixmap = _render_pixmap_cached(
            name=self._icon_name,
            weight=self._weight,
            width=self.width(),
            height=self.height(),
            color=c_str,
            secondary_color=sc_str,
            secondary_opacity=self._secondary_opacity,
            mirrored=self._mirrored,
            rotation=self._rotation,
            dpr=dpr
        )

        rect = QtCore.QRect(0, 0, self.width(), self.height())
        painter.drawPixmap(rect, pixmap)
        painter.end()
