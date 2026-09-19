import os
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, Property, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QColor

from monkeyqt.components.layout.widget import MkQWidget
from monkeyqt.themes.engine import ThemeEngine

class MkProgressBar(MkQWidget):
    """
    进度条 (Progress Bar) 组件
    使用 paintEvent 绘制，确保像素级完美和抗锯齿。
    状态: normal, success, warning, exception
    """
    def __init__(self, percentage=0, status="normal", stroke_width=6, show_text=True, text_inside=False, parent=None):
        super().__init__(parent)
        self._percentage = max(0, min(100, percentage))
        self._status = status
        self._stroke_width = stroke_width
        self._show_text = show_text
        self._text_inside = text_inside

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(max(16, self._stroke_width))

    def _get_color(self):
        from monkeyqt.themes.engine import ThemeEngine
        t = ThemeEngine
        normal = t.get("--primary", "#0F172A" if not t.is_dark() else "#FFFFFF")
        colors = {
            "normal": normal,
            "success": "#22c55e",
            "warning": "#f59e0b",
            "exception": "#ef4444"
        }
        return colors.get(self._status, colors["normal"])

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        stroke = self._stroke_width
        
        # 设置字体和文本宽度
        text = f"{self._percentage}%"
        font = self.font()
        font.setPixelSize(max(12, stroke - 2 if self._text_inside else 14))
        painter.setFont(font)
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        
        track_x = 0
        track_y = (height - stroke) / 2
        track_width = width
        
        if self._show_text and not self._text_inside:
            track_width = width - text_width - 12
            
        # 绘制背景底轨
        bg_path = QPainterPath()
        bg_path.addRoundedRect(track_x, track_y, track_width, stroke, stroke / 2, stroke / 2)
        track_bg = ThemeEngine.get("--surface-muted", "#ebeef5" if not ThemeEngine.is_dark() else "#27272A")
        painter.fillPath(bg_path, QColor(track_bg))
        
        # 绘制前景进度轨
        if self._percentage > 0:
            fg_width = track_width * (self._percentage / 100.0)
            fg_path = QPainterPath()
            fg_path.addRoundedRect(track_x, track_y, fg_width, stroke, stroke / 2, stroke / 2)
            painter.fillPath(fg_path, QColor(self._get_color()))
            
        # 绘制百分比文字
        if self._show_text:
            if self._text_inside:
                painter.setPen(QColor("#ffffff"))
                text_rect = QRectF(track_x, track_y, fg_width if self._percentage > 0 else 0, stroke)
                painter.drawText(text_rect, Qt.AlignRight | Qt.AlignVCenter, f"{text} ")
            else:
                text_fg = ThemeEngine.get("--fg", "#606266" if not ThemeEngine.is_dark() else "#F8FAFC")
                painter.setPen(QColor(text_fg))
                text_rect = QRectF(track_width + 8, 0, text_width + 4, height)
                painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)

    # Properties
    @Property(int)
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, value):
        value = max(0, min(100, value))
        if self._percentage != value:
            self._percentage = value
            self.update()

    def setValue(self, value: int):
        """Qt API compatibility method for setting percentage value."""
        self.percentage = value

    def value(self) -> int:
        """Qt API compatibility method for getting percentage value."""
        return self._percentage

    @Property(str)
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in ["normal", "success", "warning", "exception"]:
            value = "normal"
        if self._status != value:
            self._status = value
            self.update()

    @Property(int)
    def stroke_width(self):
        return self._stroke_width

    @stroke_width.setter
    def stroke_width(self, value):
        if self._stroke_width != value:
            self._stroke_width = max(2, value)
            self.setMinimumHeight(max(16, self._stroke_width))
            self.update()

    @Property(bool)
    def show_text(self):
        return self._show_text

    @show_text.setter
    def show_text(self, value):
        if self._show_text != value:
            self._show_text = value
            self.update()

    @Property(bool)
    def text_inside(self):
        return self._text_inside

    @text_inside.setter
    def text_inside(self, value):
        if self._text_inside != value:
            self._text_inside = value
            self.update()
