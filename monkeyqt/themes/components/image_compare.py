# -*- coding: utf-8 -*-
"""ThemedImageCompare — before/after comparison slider."""

from PySide6.QtCore import Property, QRect, QSize, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QSizePolicy, QWidget

from ..engine import ThemeEngine
from ..style_utils import qcolor


class ThemedImageCompare(QWidget):
    """A themed before/after image comparison widget."""

    def __init__(self, before_img=None, after_img=None, parent=None):
        super().__init__(parent)
        self._before_pixmap = QPixmap()
        self._after_pixmap = QPixmap()
        self._slider_ratio = 0.5
        self._before_label = "Before"
        self._after_label = "After"
        self._is_dragging = False
        self.setMouseTracking(True)
        self.setMinimumSize(260, 160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        if before_img is not None and after_img is not None:
            self.set_images(before_img, after_img)
        ThemeEngine.instance().themeChanged.connect(lambda name=None: self.update())

    def set_images(self, before, after):
        self._before_pixmap = self._to_pixmap(before)
        self._after_pixmap = self._to_pixmap(after)
        self.update()

    def set_labels(self, before_label, after_label):
        self._before_label = before_label
        self._after_label = after_label
        self.update()

    def _to_pixmap(self, value):
        if isinstance(value, str):
            return QPixmap(value)
        if isinstance(value, QPixmap):
            return value
        if isinstance(value, QImage):
            return QPixmap.fromImage(value)
        return QPixmap()

    def sizeHint(self):
        return QSize(420, 240)

    def _draw_rect(self):
        return self.rect().adjusted(2, 2, -2, -2)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._set_ratio_from_x(event.position().x())
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            self._set_ratio_from_x(event.position().x())
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        super().mouseReleaseEvent(event)

    def _set_ratio_from_x(self, x):
        rect = self._draw_rect()
        if rect.width() > 0:
            self.sliderRatio = (x - rect.left()) / rect.width()

    def paintEvent(self, event):
        t = ThemeEngine
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self._draw_rect()
        primary = t.get("--primary", "#409EFF")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--surface-muted", "#F1F5F9")
        radius = 0 if t.is_brutal() or t.is_pixel() else 8

        painter.setBrush(qcolor(surface))
        painter.setPen(QPen(QColor("#000000") if (t.is_brutal() or t.is_pixel()) else qcolor(border), 2 if (t.is_brutal() or t.is_pixel()) else 1))
        painter.drawRoundedRect(rect, radius, radius)

        split_x = rect.left() + int(rect.width() * self._slider_ratio)
        if not self._before_pixmap.isNull():
            painter.save()
            painter.setClipRect(QRect(rect.left(), rect.top(), split_x - rect.left(), rect.height()))
            painter.drawPixmap(rect, self._before_pixmap)
            painter.restore()
        if not self._after_pixmap.isNull():
            painter.save()
            painter.setClipRect(QRect(split_x, rect.top(), rect.right() - split_x, rect.height()))
            painter.drawPixmap(rect, self._after_pixmap)
            painter.restore()
        if self._before_pixmap.isNull() or self._after_pixmap.isNull():
            painter.setPen(qcolor(t.get("--text-muted", "#64748B")))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Image Compare")

        painter.setPen(QPen(qcolor(primary), 2.2))
        painter.drawLine(split_x, rect.top() + 8, split_x, rect.bottom() - 8)
        painter.setBrush(qcolor(primary))
        painter.drawEllipse(split_x - 9, rect.center().y() - 9, 18, 18)
        painter.end()

    @Property(float)
    def sliderRatio(self):
        return self._slider_ratio

    @sliderRatio.setter
    def sliderRatio(self, value):
        self._slider_ratio = max(0.0, min(1.0, float(value)))
        self.update()
