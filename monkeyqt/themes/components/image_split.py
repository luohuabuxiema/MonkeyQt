# -*- coding: utf-8 -*-
"""ThemedImageSplit — side-by-side split image container."""

from PySide6.QtCore import Property, QRect, QSize, Qt
from PySide6.QtGui import QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QSizePolicy, QWidget

from ..engine import ThemeEngine
from ..style_utils import qcolor


class ThemedImageSplit(QWidget):
    """A themed split image viewer with draggable divider."""

    def __init__(self, left_img=None, right_img=None, parent=None):
        super().__init__(parent)
        self._left_pixmap = self._to_pixmap(left_img)
        self._right_pixmap = self._to_pixmap(right_img)
        self._split_ratio = 0.5
        self._is_dragging = False
        self.setMouseTracking(True)
        self.setMinimumSize(260, 160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ThemeEngine.instance().themeChanged.connect(lambda name=None: self.update())

    def _to_pixmap(self, value):
        if isinstance(value, str):
            return QPixmap(value)
        if isinstance(value, QPixmap):
            return value
        if isinstance(value, QImage):
            return QPixmap.fromImage(value)
        return QPixmap()

    def set_images(self, left, right):
        self._left_pixmap = self._to_pixmap(left)
        self._right_pixmap = self._to_pixmap(right)
        self.update()

    def sizeHint(self):
        return QSize(420, 240)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._set_ratio(event.position().x())
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            self._set_ratio(event.position().x())
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        super().mouseReleaseEvent(event)

    def _set_ratio(self, x):
        rect = self.rect().adjusted(2, 2, -2, -2)
        if rect.width() > 0:
            self.splitRatio = (x - rect.left()) / rect.width()

    def paintEvent(self, event):
        t = ThemeEngine
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(2, 2, -2, -2)
        primary = t.get("--primary", "#409EFF")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--surface-muted", "#F1F5F9")
        radius = 0 if t.is_brutal() or t.is_pixel() else 8
        split_x = rect.left() + int(rect.width() * self._split_ratio)

        painter.setBrush(qcolor(surface))
        painter.setPen(QPen(qcolor(border), 1))
        painter.drawRoundedRect(rect, radius, radius)

        left_rect = QRect(rect.left(), rect.top(), split_x - rect.left(), rect.height())
        right_rect = QRect(split_x, rect.top(), rect.right() - split_x, rect.height())
        if not self._left_pixmap.isNull():
            painter.drawPixmap(left_rect, self._left_pixmap)
        else:
            painter.setPen(qcolor(t.get("--text-muted", "#64748B")))
            painter.drawText(left_rect, Qt.AlignmentFlag.AlignCenter, "Left")
        if not self._right_pixmap.isNull():
            painter.drawPixmap(right_rect, self._right_pixmap)
        else:
            painter.setPen(qcolor(t.get("--text-muted", "#64748B")))
            painter.drawText(right_rect, Qt.AlignmentFlag.AlignCenter, "Right")

        painter.setPen(QPen(qcolor(primary), 2))
        painter.drawLine(split_x, rect.top() + 6, split_x, rect.bottom() - 6)
        painter.setBrush(qcolor(primary))
        painter.drawRoundedRect(split_x - 8, rect.center().y() - 26, 16, 52, 8, 8)
        painter.end()

    @Property(float)
    def splitRatio(self):
        return self._split_ratio

    @splitRatio.setter
    def splitRatio(self, value):
        self._split_ratio = max(0.05, min(0.95, float(value)))
        self.update()
