# -*- coding: utf-8 -*-
"""
MonkeyQt Line Chart Component — 现代化高性能轻量级折线图与指标监控看板组件
采用现代 Web 前端数据可视化设计（对标 Ultralytics HUB / Chart.js / ApexCharts）：
- 60 FPS 满帧硬件加速微秒级原生渲染（零外部第三方依赖，无需 matplotlib/pyqtgraph）；
- 垂直十字吸附参考线 (verticalLine)：鼠标跟随平滑移动，自动吸附最近数据点；
- 曲线就近吸附与多曲线高亮 (nearestLine)：悬停加粗高亮目标曲线，非焦点曲线自动柔和降透；
- 训练集(实线)与验证集(虚线)自动区分与平滑贝塞尔曲线 (Cubic Spline)；
- 优雅半透明面积渐变填充 (Translucent Area Gradient Fill)；
- 交互式浮层数值卡片 (Floating Tooltip)：智能避障不被视口裁切；
- 鼠标滚轮缩放 (Wheel Zoom) 与拖拽平移 (Pan)；
- 交互式图例胶囊 (Interactive Legend)：点击显示/隐藏，悬停关联高亮；
- 深度自适应 MonkeyQt 68 种内置主题与暗黑/亮色切换。
"""

import csv
import json
import math
from typing import Optional, List, Dict, Any, Union, Tuple, Sequence
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
    QFileDialog,
    QApplication,
    QDialog,
)
from PySide6.QtCore import Qt, QPoint, QPointF, QRect, QRectF, QSize, Signal, QTimer
from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QColor,
    QPen,
    QBrush,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QMouseEvent,
    QWheelEvent,
    QPixmap,
    QIcon,
)

from monkeyqt.components.layout.widget import MkQWidget
from monkeyqt.components.navigation.dropdown import MkDropdown
from monkeyqt.components.feedback.tooltip import MkTooltip
from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import qcolor, readable_text, parse_px, lighten, darken

# 默认优雅现代调色板 (Web Tailwind / Shadcn UI 风格)
DEFAULT_CHART_COLORS = [
    "#3B82F6",  # Electric Blue (经典蓝)
    "#10B981",  # Emerald Green (翡翠绿)
    "#F59E0B",  # Amber Gold (琥珀金)
    "#8B5CF6",  # Violet Purple (紫罗兰)
    "#EC4899",  # Hot Pink (霓虹粉)
    "#06B6D4",  # Cyan (青绿)
    "#EF4444",  # Coral Red (珊瑚红)
    "#6366F1",  # Indigo (靛蓝)
    "#14B8A6",  # Teal (水鸭青)
    "#F97316",  # Orange (落日橙)
]


class MkSeries:
    """折线图数据系列对象"""
    def __init__(
        self,
        name: str,
        data: Sequence[Union[float, int, Tuple[float, float]]],
        color: Optional[Union[str, QColor]] = None,
        line_style: str = "solid",
        line_width: float = 1.8,
        smooth: bool = True,
        area: bool = True,
        visible: bool = True,
        marker: bool = True,
        gradient_fill: Optional[bool] = None,
    ):
        self.name = str(name)
        self.raw_data = list(data)
        self.color = qcolor(color) if color else None
        self.line_style = line_style.lower()  # solid, dashed, dotted
        self.line_width = float(line_width)
        self.smooth = bool(smooth)
        if gradient_fill is not None:
            area = gradient_fill
        self.area = bool(area)
        self.visible = bool(visible)
        self.marker = bool(marker)

        # 渲染路径缓存 (页面上下滚动时不重复做样条几何计算)
        self._cached_bounds_key = None
        self._cached_line_path = None
        self._cached_area_path = None
        self._cached_pts = None

        # 解析为规范的 [(x, y), ...] 点列表
        self.points: List[Tuple[float, float]] = []
        self._parse_points()

    def _parse_points(self):
        self.points.clear()
        for idx, item in enumerate(self.raw_data):
            if item is None:
                continue
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                self.points.append((float(item[0]), float(item[1])))
            else:
                self.points.append((float(idx), float(item)))
        self.points.sort(key=lambda p: p[0])

    def set_data(self, data: Sequence[Union[float, int, Tuple[float, float]]]):
        self.raw_data = list(data)
        self._parse_points()
        self._cached_bounds_key = None
        self._cached_line_path = None
        self._cached_area_path = None
        self._cached_pts = None


class _ChartCanvas(QWidget):
    """
    核心图表绘制视口 (Canvas)
    负责高性能 2D 硬件绘图、网格刻度、十字吸附辅助线、曲线高亮与滚轮缩放
    """
    seriesHovered = Signal(str)
    pointHovered = Signal(str, float, float)
    viewReset = Signal()

    def __init__(self, parent_chart: "MkLineChart"):
        super().__init__(parent_chart)
        self.chart = parent_chart
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(240)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        # 视口边距 (留给坐标轴刻度文字)
        self.margin_left = 52
        self.margin_right = 24
        self.margin_top = 20
        self.margin_bottom = 34

        # 缩放平移交互状态
        self.zoom_x_min: Optional[float] = None
        self.zoom_x_max: Optional[float] = None
        self.zoom_y_min: Optional[float] = None
        self.zoom_y_max: Optional[float] = None
        self._is_panning = False
        self._pan_start_pos: Optional[QPointF] = None
        self._pan_start_x_range: Optional[Tuple[float, float]] = None
        self._pan_start_y_range: Optional[Tuple[float, float]] = None

        # 鼠标左键矩形框选放大状态 (对标 Ultralytics HUB Box Drag Zoom)
        self._is_box_selecting: bool = False
        self._box_start_pos: Optional[QPointF] = None
        self._box_current_pos: Optional[QPointF] = None

        # 悬停交互状态
        self.hover_pos: Optional[QPointF] = None
        self.hover_snapped_x: Optional[float] = None
        self.hover_active_series: Optional[str] = None

    def is_zoomed(self) -> bool:
        """判断当前图表视口是否处于缩放/放大状态"""
        return (
            self.zoom_x_min is not None or
            self.zoom_x_max is not None or
            self.zoom_y_min is not None or
            self.zoom_y_max is not None
        )

    def reset_view(self):
        """一键重置缩放与平移视口，回到全景数据视图"""
        self.zoom_x_min = None
        self.zoom_x_max = None
        self.zoom_y_min = None
        self.zoom_y_max = None
        self._is_box_selecting = False
        self._box_start_pos = None
        self._box_current_pos = None
        self._is_panning = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        self.viewReset.emit()

    def mousePressEvent(self, event: QMouseEvent):
        pos = event.position()
        plot_rect = self._get_plot_rect()

        if event.button() in (Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton):
            # 右键或中键：启动平移拖拽 (Pan)
            if plot_rect.contains(pos) and self.chart.series_list:
                self._is_panning = True
                self._pan_start_pos = pos
                x_min, x_max, y_min, y_max = self._get_active_bounds()
                self._pan_start_x_range = (x_min, x_max)
                self._pan_start_y_range = (y_min, y_max)
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
                return

        elif event.button() == Qt.MouseButton.LeftButton:
            # 左键：记录初始坐标，准备矩形框选放大 (Box Drag Zoom) 或 单击一键重置
            if plot_rect.contains(pos) and self.chart.series_list:
                self._box_start_pos = pos
                self._box_current_pos = pos
                self._is_box_selecting = False
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        self.hover_pos = pos
        plot_rect = self._get_plot_rect()

        # ── 1. 响应中键/右键平移拖拽 (Pan) ──
        if self._is_panning and self._pan_start_pos and self._pan_start_x_range and self._pan_start_y_range:
            dx_pix = pos.x() - self._pan_start_pos.x()
            dy_pix = pos.y() - self._pan_start_pos.y()

            orig_xmin, orig_xmax = self._pan_start_x_range
            orig_ymin, orig_ymax = self._pan_start_y_range
            x_span = orig_xmax - orig_xmin
            y_span = orig_ymax - orig_ymin

            val_dx = (dx_pix / max(1.0, plot_rect.width())) * x_span
            val_dy = (dy_pix / max(1.0, plot_rect.height())) * y_span

            self.zoom_x_min = orig_xmin - val_dx
            self.zoom_x_max = orig_xmax - val_dx
            self.zoom_y_min = orig_ymin + val_dy
            self.zoom_y_max = orig_ymax + val_dy
            self.update()
            event.accept()
            return

        # ── 2. 响应鼠标左键矩形框选拖拽 (Box Drag Zoom) ──
        if self._box_start_pos is not None:
            delta = pos - self._box_start_pos
            if abs(delta.x()) > 6 or abs(delta.y()) > 6:
                self._is_box_selecting = True
                self._box_current_pos = pos
                self.setCursor(Qt.CursorShape.CrossCursor)
                self.update()
                event.accept()
                return

        # ── 3. 普通鼠标移动：计算十字吸附与曲线就近高亮 ──
        if not plot_rect.contains(pos) or not self.chart.series_list:
            if self.hover_snapped_x is not None:
                self.hover_snapped_x = None
                self.hover_active_series = None
                self.seriesHovered.emit("")
                self.update()
            return

        # 3.1 计算鼠标光标对应的 X 数据值
        x_min, x_max, _, _ = self._get_active_bounds()
        x_val = self._pixel_to_val_x(pos.x(), plot_rect, x_min, x_max)

        # 3.2 寻找所有可见数据序列中最近的 X 数据点 (对标 verticalLine 吸附)
        snapped_x = None
        min_x_dist = float("inf")
        nearest_series_name = None
        nearest_pt_dist_sq = float("inf")

        for s in self.chart.series_list:
            if not s.visible or not s.points:
                continue
            for px, py in s.points:
                dist_x = abs(px - x_val)
                if dist_x < min_x_dist:
                    min_x_dist = dist_x
                    snapped_x = px

                # 同时计算鼠标到点位的欧氏距离，判断就近高亮曲线 (nearestLine)
                p_pix = self._val_to_pixel(px, py, plot_rect)
                dist_sq = (p_pix.x() - pos.x()) ** 2 + (p_pix.y() - pos.y()) ** 2
                if dist_sq < nearest_pt_dist_sq:
                    nearest_pt_dist_sq = dist_sq
                    nearest_series_name = s.name

        self.hover_snapped_x = snapped_x

        # 若鼠标离最近曲线在 32px 范围内，自动触发就近高亮
        if math.sqrt(nearest_pt_dist_sq) <= 32:
            if self.hover_active_series != nearest_series_name:
                self.hover_active_series = nearest_series_name
                self.seriesHovered.emit(nearest_series_name)
        else:
            if self.hover_active_series is not None:
                self.hover_active_series = None
                self.seriesHovered.emit("")

        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        # 1. 释放平移拖拽
        if self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        # 2. 释放左键
        if event.button() == Qt.MouseButton.LeftButton and self._box_start_pos is not None:
            start_pos = self._box_start_pos
            end_pos = event.position()
            plot_rect = self._get_plot_rect()

            self._box_start_pos = None
            self._box_current_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)

            if self._is_box_selecting:
                self._is_box_selecting = False
                # 判定框选有效区域 (至少大于 8x8 像素，避免误触)
                x1 = max(plot_rect.left(), min(start_pos.x(), end_pos.x()))
                x2 = min(plot_rect.right(), max(start_pos.x(), end_pos.x()))
                y1 = max(plot_rect.top(), min(start_pos.y(), end_pos.y()))
                y2 = min(plot_rect.bottom(), max(start_pos.y(), end_pos.y()))

                if (x2 - x1) >= 8 and (y2 - y1) >= 8:
                    x_min, x_max, y_min, y_max = self._get_active_bounds()
                    new_x_min = self._pixel_to_val_x(x1, plot_rect, x_min, x_max)
                    new_x_max = self._pixel_to_val_x(x2, plot_rect, x_min, x_max)
                    new_y_max = self._pixel_to_val_y(y1, plot_rect, y_min, y_max)
                    new_y_min = self._pixel_to_val_y(y2, plot_rect, y_min, y_max)

                    self.zoom_x_min = min(new_x_min, new_x_max)
                    self.zoom_x_max = max(new_x_min, new_x_max)
                    self.zoom_y_min = min(new_y_min, new_y_max)
                    self.zoom_y_max = max(new_y_min, new_y_max)
                    self.update()
                    event.accept()
                    return
            else:
                # 单纯点击 (Click without drag):
                # 对标 Ultralytics HUB：如果当前图表处于放大状态，单击一下空白处直接平滑重置全景！
                if self.is_zoomed():
                    self.reset_view()
                    event.accept()
                    return

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击快速重置缩放"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.reset_view()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def leaveEvent(self, event):
        self.hover_pos = None
        self.hover_snapped_x = None
        self.hover_active_series = None
        self._is_panning = False
        self._is_box_selecting = False
        self._box_start_pos = None
        self._box_current_pos = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.seriesHovered.emit("")
        self.update()

    def wheelEvent(self, event: QWheelEvent):
        """
        鼠标滚轮逻辑 (对标 Ultralytics HUB 专业数据大屏)：
        - 普通模式 (看板网格中)：默认不拦截滚轮 (event.ignore())，无损穿透至父级 QScrollArea，页面平滑滚动！
        - 缩放模式：当图表处于全屏独立弹窗 (is_fullscreen) OR 用户按住 Ctrl 键时，激活以光标为中心的高精度双向缩放。
        """
        plot_rect = self._get_plot_rect()
        if not plot_rect.contains(event.position()) or not self.chart.series_list:
            event.ignore()
            return

        # 检查是否满足图表缩放条件
        modifiers = event.modifiers()
        ctrl_pressed = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        can_zoom = self.chart.enable_zoom and (
            self.chart.wheel_zoom_enabled or
            self.chart.is_fullscreen or
            ctrl_pressed
        )

        if not can_zoom:
            # 关键：普通模式下直接忽略，确保父级 QScrollArea 能够正常上下滚动页面
            event.ignore()
            return

        delta = event.angleDelta().y()
        if delta == 0:
            return

        factor = 0.82 if delta > 0 else 1.22
        x_min, x_max, y_min, y_max = self._get_active_bounds()
        cursor_x_val = self._pixel_to_val_x(event.position().x(), plot_rect, x_min, x_max)
        cursor_y_val = self._pixel_to_val_y(event.position().y(), plot_rect, y_min, y_max)

        span_x = x_max - x_min
        span_y = y_max - y_min
        if span_x <= 0 or span_y <= 0:
            return

        new_span_x = span_x * factor
        new_span_y = span_y * factor

        # 限制最小缩放范围，防止缩到单个点
        if (new_span_x < 1.0 or new_span_y < 1e-6) and delta > 0:
            event.accept()
            return

        ratio_x = (cursor_x_val - x_min) / span_x
        ratio_y = (cursor_y_val - y_min) / span_y

        self.zoom_x_min = cursor_x_val - new_span_x * ratio_x
        self.zoom_x_max = cursor_x_val + new_span_x * (1.0 - ratio_x)
        self.zoom_y_min = cursor_y_val - new_span_y * ratio_y
        self.zoom_y_max = cursor_y_val + new_span_y * (1.0 - ratio_y)

        self.update()
        event.accept()

    def keyPressEvent(self, event):
        """支持 Esc 键快速退出框选或一键还原视口"""
        if event.key() == Qt.Key.Key_Escape:
            if self._is_box_selecting:
                self._is_box_selecting = False
                self._box_start_pos = None
                self._box_current_pos = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.update()
                event.accept()
                return
            if self.is_zoomed():
                self.reset_view()
                event.accept()
                return
        super().keyPressEvent(event)

    def _get_plot_rect(self) -> QRectF:
        w = max(10, self.width() - self.margin_left - self.margin_right)
        h = max(10, self.height() - self.margin_top - self.margin_bottom)
        return QRectF(self.margin_left, self.margin_top, w, h)

    def _get_data_bounds(self) -> Tuple[float, float, float, float]:
        """计算全量可见数据的极值边界"""
        all_pts: List[Tuple[float, float]] = []
        for s in self.chart.series_list:
            if s.visible and s.points:
                all_pts.extend(s.points)

        if not all_pts:
            return (0.0, 10.0, 0.0, 1.0)

        xs = [p[0] for p in all_pts]
        ys = [p[1] for p in all_pts]

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        # 增加 Y 轴微小呼吸裕量 (5%)
        y_span = max(1e-5, y_max - y_min)
        if self.chart.custom_y_min is not None:
            y_min = self.chart.custom_y_min
        else:
            y_min = max(0.0, y_min - y_span * 0.05) if y_min >= 0 else y_min - y_span * 0.05

        if self.chart.custom_y_max is not None:
            y_max = self.chart.custom_y_max
        else:
            y_max = y_max + y_span * 0.08

        if x_min == x_max:
            x_max = x_min + 1.0

        return (x_min, x_max, y_min, y_max)

    def _get_active_bounds(self) -> Tuple[float, float, float, float]:
        if getattr(self, "_active_bounds_cache", None) is not None:
            return self._active_bounds_cache
        d_xmin, d_xmax, d_ymin, d_ymax = self._get_data_bounds()
        x_min = self.zoom_x_min if self.zoom_x_min is not None else d_xmin
        x_max = self.zoom_x_max if self.zoom_x_max is not None else d_xmax
        y_min = self.zoom_y_min if self.zoom_y_min is not None else d_ymin
        y_max = self.zoom_y_max if self.zoom_y_max is not None else d_ymax
        return (x_min, x_max, y_min, y_max)

    def _val_to_pixel(
        self,
        x_val: float,
        y_val: float,
        rect: QRectF,
        bounds: Optional[Tuple[float, float, float, float]] = None,
    ) -> QPointF:
        if bounds is not None:
            x_min, x_max, y_min, y_max = bounds
        elif getattr(self, "_active_bounds_cache", None) is not None:
            x_min, x_max, y_min, y_max = self._active_bounds_cache
        else:
            x_min, x_max, y_min, y_max = self._get_active_bounds()
        px = rect.left() + ((x_val - x_min) / max(1e-6, x_max - x_min)) * rect.width()
        py = rect.bottom() - ((y_val - y_min) / max(1e-6, y_max - y_min)) * rect.height()
        return QPointF(px, py)

    def _pixel_to_val_x(self, px: float, rect: QRectF, x_min: float, x_max: float) -> float:
        ratio = max(0.0, min(1.0, (px - rect.left()) / max(1.0, rect.width())))
        return x_min + ratio * (x_max - x_min)

    def _pixel_to_val_y(self, py: float, rect: QRectF, y_min: float, y_max: float) -> float:
        ratio = max(0.0, min(1.0, (rect.bottom() - py) / max(1.0, rect.height())))
        return y_min + ratio * (y_max - y_min)

    # ──────────── 核心绘制逻辑 (paintEvent) ────────────

    def paintEvent(self, event):
        self._active_bounds_cache = self._get_active_bounds()
        try:
            self._do_paint(event)
        finally:
            self._active_bounds_cache = None

    def _do_paint(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        plot_rect = self._get_plot_rect()
        is_dark = ThemeEngine.is_dark()
        fg_color = qcolor(ThemeEngine.get("--fg", "#F4F4F5" if is_dark else "#0F172A"))
        muted_color = qcolor(ThemeEngine.get("--text-muted", "#A1A1AA" if is_dark else "#64748B"))
        border_color = qcolor(ThemeEngine.get("--border", "#27272A" if is_dark else "#E2E8F0"))

        x_min, x_max, y_min, y_max = self._get_active_bounds()
        x_factor = plot_rect.width() / max(1e-6, x_max - x_min)
        y_factor = plot_rect.height() / max(1e-6, y_max - y_min)
        r_left = plot_rect.left()
        r_bottom = plot_rect.bottom()

        # 1. 绘制极简网格线与 Y 轴刻度
        grid_alpha = 45 if is_dark else 35
        grid_pen = QPen(QColor(180, 180, 180, grid_alpha), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)

        font_label = QFont("Segoe UI", 9)
        font_label.setStyleHint(QFont.StyleHint.SansSerif)
        painter.setFont(font_label)

        y_ticks = 5
        for i in range(y_ticks):
            ratio = i / float(y_ticks - 1)
            y_val = y_min + ratio * (y_max - y_min)
            py = plot_rect.bottom() - ratio * plot_rect.height()

            # 水平虚线网格
            painter.setPen(grid_pen)
            painter.drawLine(QPointF(plot_rect.left(), py), QPointF(plot_rect.right(), py))

            # Y 轴文字标签
            painter.setPen(QPen(muted_color, 1))
            val_text = self.chart.format_y_val(y_val)
            painter.drawText(
                QRectF(0, py - 10, self.margin_left - 8, 20),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                val_text,
            )

        # 2. 绘制 X 轴刻度与文本
        x_ticks = 6
        for i in range(x_ticks):
            ratio = i / float(x_ticks - 1)
            x_val = x_min + ratio * (x_max - x_min)
            px = plot_rect.left() + ratio * plot_rect.width()

            # 垂直微弱虚线
            painter.setPen(grid_pen)
            painter.drawLine(QPointF(px, plot_rect.top()), QPointF(px, plot_rect.bottom()))

            # X 轴文字标签
            painter.setPen(QPen(muted_color, 1))
            x_text = self.chart.format_x_val(x_val)
            painter.drawText(
                QRectF(px - 30, plot_rect.bottom() + 6, 60, 20),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                x_text,
            )

        # 3. 绘制外边界框底线与左轴线
        axis_pen = QPen(border_color, 1, Qt.PenStyle.SolidLine)
        painter.setPen(axis_pen)
        painter.drawLine(QPointF(plot_rect.left(), plot_rect.bottom()), QPointF(plot_rect.right(), plot_rect.bottom()))
        painter.drawLine(QPointF(plot_rect.left(), plot_rect.top()), QPointF(plot_rect.left(), plot_rect.bottom()))

        # 裁剪视口，防止曲线在缩放平移时溢出画框
        painter.save()
        painter.setClipRect(plot_rect)

        # 4. 绘制折线曲线与面积渐变 (对标 Chart.js Smooth Spline)
        effective_highlight = self.chart.highlight_series or self.hover_active_series
        bounds_key = (
            round(plot_rect.width(), 1), round(plot_rect.height(), 1),
            round(plot_rect.left(), 1), round(plot_rect.top(), 1),
            round(x_min, 4), round(x_max, 4), round(y_min, 4), round(y_max, 4)
        )

        for s_idx, s in enumerate(self.chart.series_list):
            if not s.visible or len(s.points) < 2:
                continue

            s_color = s.color or qcolor(DEFAULT_CHART_COLORS[s_idx % len(DEFAULT_CHART_COLORS)])
            is_highlighted = (effective_highlight == s.name)
            is_dimmed = (effective_highlight is not None and not is_highlighted)

            # 透明度动态调权 (nearestLine 核心)
            alpha_line = 0.22 if is_dimmed else 1.0
            line_w = 2.8 if is_highlighted else (s.line_width * (0.8 if is_dimmed else 1.0))

            cur_color = QColor(s_color)
            cur_color.setAlphaF(alpha_line)

            # 高性能路径缓存：视口尺寸与数值范围未变时（如页面滚动），直接复用已编译路径
            if getattr(s, "_cached_bounds_key", None) == bounds_key and getattr(s, "_cached_line_path", None) is not None:
                line_path = s._cached_line_path
                area_path = s._cached_area_path
                pts = s._cached_pts
            else:
                pts = [
                    QPointF(r_left + (px - x_min) * x_factor, r_bottom - (py - y_min) * y_factor)
                    for px, py in s.points
                ]
                line_path = QPainterPath()
                line_path.moveTo(pts[0])

                if s.smooth and len(pts) > 2:
                    for i in range(1, len(pts)):
                        p0 = pts[i - 1]
                        p1 = pts[i]
                        dx = (p1.x() - p0.x()) / 2.0
                        cp1 = QPointF(p0.x() + dx, p0.y())
                        cp2 = QPointF(p1.x() - dx, p1.y())
                        line_path.cubicTo(cp1, cp2, p1)
                else:
                    for p in pts[1:]:
                        line_path.lineTo(p)

                area_path = None
                if s.area and self.chart.enable_area_fill:
                    area_path = QPainterPath(line_path)
                    area_path.lineTo(pts[-1].x(), plot_rect.bottom())
                    area_path.lineTo(pts[0].x(), plot_rect.bottom())
                    area_path.closeSubpath()

                s._cached_bounds_key = bounds_key
                s._cached_line_path = line_path
                s._cached_area_path = area_path
                s._cached_pts = pts

            # 4.2 绘制面积微光渐变 (Area Fill)
            if area_path is not None and self.chart.enable_area_fill and not is_dimmed:
                grad = QLinearGradient(0, plot_rect.top(), 0, plot_rect.bottom())
                c_top = QColor(s_color)
                c_top.setAlphaF(0.24 if is_highlighted else 0.12)
                c_bot = QColor(s_color)
                c_bot.setAlphaF(0.0)
                grad.setColorAt(0.0, c_top)
                grad.setColorAt(1.0, c_bot)
                painter.fillPath(area_path, QBrush(grad))

            # 4.3 绘制主线条
            pen_style = Qt.PenStyle.SolidLine
            if s.line_style == "dashed":
                pen_style = Qt.PenStyle.DashLine
            elif s.line_style == "dotted":
                pen_style = Qt.PenStyle.DotLine

            painter.setPen(QPen(cur_color, line_w, pen_style, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(line_path)

            # 4.4 绘制数据散点 (点数极少或高亮时突出显示，对标 Ultralytics 规避海量离散圆点绘制)
            if s.marker and (len(pts) <= 15 or is_highlighted) and not is_dimmed:
                radius = 3.5 if is_highlighted else 2.2
                painter.setPen(QPen(cur_color, 1.2))
                painter.setBrush(QBrush(QColor("#FFFFFF" if not is_dark else "#18181B")))
                for pt in pts:
                    if plot_rect.left() - 5 <= pt.x() <= plot_rect.right() + 5:
                        painter.drawEllipse(pt, radius, radius)

        # 5. 绘制垂直十字吸附参考线与吸附点 (对标 verticalLine 插件)
        snapped_x = self.hover_snapped_x
        hover_data_points: List[Tuple[str, QColor, float, float]] = []

        if snapped_x is not None:
            snap_px = plot_rect.left() + ((snapped_x - x_min) / max(1e-6, x_max - x_min)) * plot_rect.width()
            if plot_rect.left() <= snap_px <= plot_rect.right():
                cross_pen = QPen(QColor(130, 130, 140, 160), 1, Qt.PenStyle.DashLine)
                painter.setPen(cross_pen)
                painter.drawLine(QPointF(snap_px, plot_rect.top()), QPointF(snap_px, plot_rect.bottom()))

                # 寻找每个可见曲线在当前 snapped_x 下的 Y 值，绘制光斑圆点
                for s_idx, s in enumerate(self.chart.series_list):
                    if not s.visible:
                        continue
                    # 精确查找对应的 x
                    pt_val = next((py for px, py in s.points if abs(px - snapped_x) < 1e-4), None)
                    if pt_val is not None:
                        s_color = s.color or qcolor(DEFAULT_CHART_COLORS[s_idx % len(DEFAULT_CHART_COLORS)])
                        dot_pt = self._val_to_pixel(snapped_x, pt_val, plot_rect)
                        is_curr_h = (effective_highlight == s.name)
                        dot_r = 5.0 if is_curr_h else 3.5

                        # 外发光光晕
                        glow_c = QColor(s_color)
                        glow_c.setAlphaF(0.35)
                        painter.setPen(Qt.PenStyle.NoPen)
                        painter.setBrush(QBrush(glow_c))
                        painter.drawEllipse(dot_pt, dot_r + 3, dot_r + 3)

                        # 核心圆点
                        painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
                        painter.setBrush(QBrush(s_color))
                        painter.drawEllipse(dot_pt, dot_r, dot_r)

                        hover_data_points.append((s.name, s_color, snapped_x, pt_val))

        painter.restore()

        # 6. 绘制鼠标框选半透明选框 (对标 Ultralytics HUB Box Drag Zoom)
        if self._is_box_selecting and self._box_start_pos and self._box_current_pos:
            sp = self._box_start_pos
            cp = self._box_current_pos
            x1 = max(plot_rect.left(), min(sp.x(), cp.x()))
            x2 = min(plot_rect.right(), max(sp.x(), cp.x()))
            y1 = max(plot_rect.top(), min(sp.y(), cp.y()))
            y2 = min(plot_rect.bottom(), max(sp.y(), cp.y()))
            box_rect = QRectF(x1, y1, x2 - x1, y2 - y1)

            # 半透明淡蓝色选框与精致描边
            box_bg = QColor(59, 130, 246, 35)
            box_border = QColor(59, 130, 246, 190)
            painter.setBrush(QBrush(box_bg))
            painter.setPen(QPen(box_border, 1, Qt.PenStyle.SolidLine))
            painter.drawRect(box_rect)

        # 7. 绘制高颜值毛玻璃/暗色半透明 Tooltip 卡片浮层 (框选或平移期间自动隐藏避障)
        if (
            hover_data_points
            and self.hover_pos
            and not self._is_box_selecting
            and not self._is_panning
        ):
            self._draw_floating_tooltip(painter, hover_data_points, snapped_x, plot_rect, is_dark)

        painter.end()

    def _draw_floating_tooltip(
        self,
        painter: QPainter,
        hover_points: List[Tuple[str, QColor, float, float]],
        snapped_x: float,
        plot_rect: QRectF,
        is_dark: bool,
    ):
        """绘制优雅的悬浮 Tooltip 气泡卡片，智能避让图表边缘"""
        title_text = f"X: {self.chart.format_x_val(snapped_x)}"
        effective_highlight = self.chart.highlight_series or self.hover_active_series

        # 计算尺寸
        font_title = QFont("Segoe UI", 9, QFont.Weight.Bold)
        font_row = QFont("Segoe UI", 9)
        fm_row = QFontMetrics(font_row)

        max_row_w = QFontMetrics(font_title).horizontalAdvance(title_text)
        for name, _, _, y_val in hover_points:
            line_str = f"●  {name}: {self.chart.format_y_val(y_val)}"
            max_row_w = max(max_row_w, fm_row.horizontalAdvance(line_str))

        pad_x = 12
        pad_y = 10
        card_w = max_row_w + pad_x * 2 + 10
        card_h = pad_y * 2 + 18 + len(hover_points) * 19

        # 智能位置计算：默认在光标右侧，若溢出右侧则翻转到左侧
        cur_pos = self.hover_pos
        tooltip_x = cur_pos.x() + 16
        if tooltip_x + card_w > self.width() - 8:
            tooltip_x = cur_pos.x() - card_w - 16

        tooltip_y = max(8.0, min(float(self.height() - card_h - 8), cur_pos.y() - card_h / 2.0))
        tip_rect = QRectF(tooltip_x, tooltip_y, card_w, card_h)

        # 绘制半透明卡片圆角背景与发光描边
        bg_color = QColor(24, 24, 27, 235) if is_dark else QColor(255, 255, 255, 240)
        border_c = QColor(63, 63, 70, 200) if is_dark else QColor(226, 232, 240, 240)

        card_path = QPainterPath()
        card_path.addRoundedRect(tip_rect, 8.0, 8.0)
        painter.fillPath(card_path, QBrush(bg_color))
        painter.setPen(QPen(border_c, 1))
        painter.drawPath(card_path)

        # 绘制标题 (X 坐标)
        painter.setFont(font_title)
        title_color = QColor("#F4F4F5") if is_dark else QColor("#0F172A")
        painter.setPen(QPen(title_color, 1))
        painter.drawText(
            QRectF(tip_rect.left() + pad_x, tip_rect.top() + pad_y, card_w - pad_x * 2, 18),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            title_text,
        )

        # 绘制每条曲线的指示圆点与数值
        painter.setFont(font_row)
        curr_y = tip_rect.top() + pad_y + 22
        for name, col, _, y_val in hover_points:
            is_h = (effective_highlight == name)
            # 圆点
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(col))
            painter.drawEllipse(QPointF(tip_rect.left() + pad_x + 4, curr_y + 8), 3.5, 3.5)

            # 序列名与数值
            text_c = QColor("#FFFFFF" if is_dark else "#0F172A") if is_h else (QColor("#A1A1AA") if is_dark else QColor("#475569"))
            painter.setPen(QPen(text_c, 1))
            val_formatted = self.chart.format_y_val(y_val)
            painter.drawText(
                QRectF(tip_rect.left() + pad_x + 14, curr_y, card_w - pad_x * 2 - 14, 18),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                f"{name}: {val_formatted}",
            )
            curr_y += 19


class _LegendItemPill(QPushButton):
    """交互式图例胶囊按钮：支持点击隐藏/展示，悬停关联高亮"""
    def __init__(self, series: MkSeries, chart: "MkLineChart", parent=None):
        super().__init__(parent)
        self.series = series
        self.chart = chart
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(24)
        self.setIconSize(QSize(10, 10))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setToolTip(f"点击切换显示/隐藏 [{series.name}] 曲线")

        font = QFont("Segoe UI", 9, QFont.Weight.DemiBold)
        self.setFont(font)
        self.clicked.connect(self._toggle_visibility)
        self._update_appearance()

    def _toggle_visibility(self):
        self.series.visible = not self.series.visible
        self._update_appearance()
        self.chart.canvas.update()

    def enterEvent(self, event):
        self.chart.set_highlight_series(self.series.name)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.chart.clear_highlight()
        super().leaveEvent(event)

    def _update_appearance(self):
        is_dark = ThemeEngine.is_dark()
        col = self.series.color or QColor("#3B82F6")
        col_hex = col.name()

        if self.series.visible:
            if is_dark:
                qss = f"""
                QPushButton {{
                    background-color: rgba(255, 255, 255, 0.06);
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    border-radius: 12px;
                    padding: 1px 8px;
                    color: #F4F4F5;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 0.12);
                    border-color: {col_hex};
                }}
                """
            else:
                qss = f"""
                QPushButton {{
                    background-color: #F8FAFC;
                    border: 1px solid #E2E8F0;
                    border-radius: 12px;
                    padding: 1px 8px;
                    color: #0F172A;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: #F1F5F9;
                    border-color: {col_hex};
                }}
                """
            # 采用全矢量 High-DPI 圆点图标 (自适应屏幕缩放，杜绝模糊毛刺)
            try:
                from monkeyqt.icons import PhCircle
                self.setIcon(PhCircle.icon(color=col_hex, weight="fill", size=10))
            except Exception:
                pix = QPixmap(20, 20)
                pix.setDevicePixelRatio(2.0)
                pix.fill(Qt.GlobalColor.transparent)
                p = QPainter(pix)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(col))
                p.drawEllipse(2, 2, 16, 16)
                p.end()
                self.setIcon(QIcon(pix))
            self.setText(f"{self.series.name}")
        else:
            # 隐藏状态：置灰与矢量斜线眼标 (虚线边框由 paintEvent 统一高清绘制，杜绝两端变粗上下变细的 Qt QSS 缺陷)
            is_dark = ThemeEngine.is_dark()
            text_muted = ThemeEngine.get("--text-muted", "#71717A" if is_dark else "#64748B")
            hover_bg = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.04)"
            qss = f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 12px;
                padding: 1px 8px;
                color: {text_muted};
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
            """
            try:
                from monkeyqt.icons import PhEyeSlash
                self.setIcon(PhEyeSlash.icon(color=text_muted, size=10))
            except Exception:
                self.setIcon(QIcon())
            self.setText(f"{self.series.name}")

        self.setStyleSheet(qss)

    def paintEvent(self, event):
        super().paintEvent(event)
        # 当曲线为隐藏状态时，采用 QPainter 全局亚像素抗锯齿绘制 100% 均匀精细的虚线胶囊边框
        if not self.series.visible:
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            is_dark = ThemeEngine.is_dark()
            border_col = QColor(ThemeEngine.get("--text-muted", "#71717A" if is_dark else "#94A3B8"))
            pen = QPen(border_col, 1.0, Qt.PenStyle.CustomDashLine)
            pen.setDashPattern([3, 3])
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
            p.drawRoundedRect(rect, 11.5, 11.5)
            p.end()


class _ChartActionBar(QWidget):
    """
    右上角悬浮操作栏胶囊 (Capsule Floating Toolbar)
    对标 Ultralytics HUB (参考图一、图二、图三):
    - 全屏放大按钮 (Fullscreen) + 现代微泡提示 (MkTooltip)
    - 更多操作按钮 (···) + MkDropdown 下拉菜单 (Download PNG / CSV / JSON / 平滑 / 还原)
    - 全屏状态下支持一键退出全屏 (✕)
    """
    def __init__(self, chart: "MkLineChart", is_fullscreen: bool = False, parent=None):
        super().__init__(parent or chart)
        self.chart = chart
        self.is_fullscreen = is_fullscreen
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("MkChartActionBar")
        self.setFixedHeight(30)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 2, 4, 2)
        self._layout.setSpacing(2)

        if not self.is_fullscreen:
            # 1. 全屏放大按钮 (⤢)
            self.btn_fs = QPushButton(self)
            self.btn_fs.setFixedSize(26, 26)
            self.btn_fs.setIconSize(QSize(14, 14))
            self.btn_fs.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_fs.clicked.connect(self.chart.open_fullscreen)
            MkTooltip.attach(self.btn_fs, "Fullscreen")
            self._layout.addWidget(self.btn_fs)

        # 2. 更多操作下拉菜单 (基于内置 MkDropdown)
        self.dropdown = MkDropdown(
            trigger="more",
            size="small",
            placement="bottom-end",
            parent=self,
        )
        self.dropdown.setFixedSize(26, 26)
        self.dropdown.add_item("Download PNG", "png", icon="image", callback=self.chart.export_image)
        self.dropdown.add_item("Download CSV", "csv", icon="table", callback=self.chart.export_csv)
        self.dropdown.add_item("Download JSON", "json", icon="code", callback=self.chart.export_json)
        self.dropdown.add_separator()
        self.action_smooth = self.dropdown.add_check_item(
            "平滑曲线",
            "smooth",
            checked=self.chart.enable_smooth,
            callback=self._on_toggle_smooth_menu
        )
        self.dropdown.add_item("还原视口", "reset", icon="arrow-counter-clockwise", callback=self.chart.reset_zoom)
        self.dropdown.menu.aboutToHide.connect(self._on_dropdown_about_to_hide)
        self._layout.addWidget(self.dropdown)

        if self.is_fullscreen:
            # 全屏模式下的退出按钮 (✕)
            self.btn_close = QPushButton(self)
            self.btn_close.setFixedSize(26, 26)
            self.btn_close.setIconSize(QSize(14, 14))
            self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_close.clicked.connect(self.chart.close_fullscreen)
            MkTooltip.attach(self.btn_close, "Exit Fullscreen")
            self._layout.addWidget(self.btn_close)

        self._update_theme_style()

    def sizeHint(self) -> QSize:
        return QSize(64, 30)

    def _on_toggle_smooth_menu(self):
        self.chart.toggle_smooth()
        self.action_smooth.setChecked(self.chart.enable_smooth)

    def _on_dropdown_about_to_hide(self):
        # 当下拉菜单关闭时，若鼠标不在图表卡片内，则触发隐藏悬浮栏
        if self.chart.auto_hide_actions and not self.chart.underMouse():
            self.setVisible(False)

    def is_menu_open(self) -> bool:
        return self.dropdown.menu.isVisible()

    def _update_theme_style(self):
        is_dark = ThemeEngine.is_dark()
        fg = ThemeEngine.get("--fg", "#F4F4F5" if is_dark else "#0F172A")
        capsule_bg = "rgba(255, 255, 255, 0.08)" if is_dark else "#F1F5F9"
        capsule_border = "rgba(255, 255, 255, 0.14)" if is_dark else "#E2E8F0"
        btn_hover_bg = "rgba(255, 255, 255, 0.14)" if is_dark else "rgba(0, 0, 0, 0.06)"

        self.setStyleSheet(f"""
        #MkChartActionBar {{
            background-color: {capsule_bg};
            border: 1px solid {capsule_border};
            border-radius: 8px;
        }}
        QPushButton {{
            background: transparent;
            border: none;
            border-radius: 6px;
        }}
        QPushButton:hover {{
            background: {btn_hover_bg};
        }}
        """)

        try:
            from monkeyqt.icons import PhCornersOut, PhX
            if hasattr(self, "btn_fs"):
                self.btn_fs.setIcon(PhCornersOut.icon(size=14, color=fg))
            if hasattr(self, "btn_close"):
                self.btn_close.setIcon(PhX.icon(size=14, color=fg))
        except Exception:
            pass


class _ChartFullscreenModal(QDialog):
    """
    全屏图表模态窗口 (对标 Ultralytics HUB 全屏图表，参考图二)
    - 沉浸全屏画幅展示
    - 右上角包含 [···] 导出菜单与 [✕] 退出全屏按钮
    - 支持 Esc 键或 F11 键快速退出
    """
    def __init__(self, source_chart: "MkLineChart", parent=None):
        super().__init__(parent)
        self.source_chart = source_chart
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(0)

        # 构建全屏图表
        self.chart = MkLineChart(
            title=source_chart._title_text,
            subtitle=source_chart._subtitle_text,
            smooth=source_chart.enable_smooth,
            area=source_chart.enable_area_fill,
            x_label=source_chart.x_label,
            y_label=source_chart.y_label,
            custom_y_min=source_chart.custom_y_min,
            custom_y_max=source_chart.custom_y_max,
            title_alignment=source_chart.title_alignment,
            show_legend=source_chart.show_legend,
            legend_position=source_chart.legend_position,
            auto_hide_actions=False,
            enable_actions=True,
            show_legacy_toolbar=False,
            is_fullscreen=True,
            fullscreen_parent_dialog=self,
            enable_zoom=source_chart.enable_zoom,
            wheel_zoom_enabled=True,
            parent=self,
        )

        for s in source_chart.series_list:
            self.chart.add_series(
                name=s.name,
                data=s.raw_data,
                color=s.color,
                line_style=s.line_style,
                line_width=s.line_width,
                smooth=s.smooth,
                area=s.area,
                marker=s.marker,
            )

        self._layout.addWidget(self.chart)
        self._apply_theme()
        ThemeEngine.instance().themeChanged.connect(self._apply_theme)

    def _apply_theme(self):
        is_dark = ThemeEngine.is_dark()
        bg = ThemeEngine.get("--bg", "#09090B" if is_dark else "#F8FAFC")
        self.setStyleSheet(f"QDialog {{ background-color: {bg}; }}")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_F11):
            self.close()
            event.accept()
            return
        super().keyPressEvent(event)


class MkLineChart(MkQWidget):
    """
    MkLineChart - 现代化高性能折线图与指标监控看板组件 (MonkeyQt Core)

    特性:
      1. 【满帧 60 FPS 极速绘制】：基于 PySide6 原生 QPainter 硬件加速，零外部重量级三方库依赖；
      2. 【对标 Ultralytics HUB】：
         - 垂直吸附参考线 (`verticalLine`)：光标平滑移动，自动吸附最近数据点；
         - 曲线就近高亮 (`nearestLine`)：鼠标靠近或列表悬停时，目标曲线自动加粗并聚焦；
         - 鼠标矩形框选放大 (Box Drag Zoom) 与单机一键平滑重置全貌 (Single Click Reset)；
         - 实线(Train)与虚线(Val)自动分离；
         - 优雅平滑贝塞尔曲线 (Cubic Spline) 与半透明微光面积渐变 (Area Gradient)；
      3. 【全功能交互】：滚轮穿透保护 (普通模式顺畅滚动页面，全屏或 Ctrl+滚轮高精度缩放)、拖拽平移 (Pan)、交互式图例隐藏、高清图片导出；
      4. 【现代悬浮胶囊工具栏】：右上角浮层全屏放大 (Fullscreen)、更多菜单 (MkDropdown)、一键下载 PNG/CSV/JSON；
      5. 【68 种主题深度自适应】：动态响应深色/浅色/毛玻璃等全系 Design Token。
    """
    seriesHovered = Signal(str)
    pointHovered = Signal(str, float, float)

    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        parent: Optional[QWidget] = None,
        *,
        smooth: bool = True,
        area: bool = True,
        x_label: str = "",
        y_label: str = "",
        custom_y_min: Optional[float] = None,
        custom_y_max: Optional[float] = None,
        title_alignment: str = "center",
        show_legend: bool = True,
        legend_position: str = "header-left",
        auto_hide_actions: bool = True,
        enable_actions: bool = True,
        show_legacy_toolbar: bool = False,
        is_fullscreen: bool = False,
        fullscreen_parent_dialog: Optional[QDialog] = None,
        enable_zoom: bool = True,
        wheel_zoom_enabled: bool = False,
    ):
        super().__init__(parent=parent, role="card", radius=12, border=True, margins=(16, 14, 16, 14), spacing=10)
        self._title_text = title
        self._subtitle_text = subtitle
        self.enable_smooth = bool(smooth)
        self.enable_area_fill = bool(area)
        self.x_label = x_label
        self.y_label = y_label
        self.custom_y_min = custom_y_min
        self.custom_y_max = custom_y_max
        self.title_alignment = str(title_alignment).lower()
        self.show_legend = bool(show_legend)
        self.legend_position = str(legend_position).lower()
        self.auto_hide_actions = bool(auto_hide_actions)
        self.enable_actions = bool(enable_actions)
        self.show_legacy_toolbar = bool(show_legacy_toolbar)
        self.is_fullscreen = bool(is_fullscreen)
        self.fullscreen_parent_dialog = fullscreen_parent_dialog
        self.enable_zoom = bool(enable_zoom)
        self.wheel_zoom_enabled = bool(wheel_zoom_enabled)

        self.series_list: List[MkSeries] = []
        self.highlight_series: Optional[str] = None
        self._legend_pills: List[_LegendItemPill] = []

        self._setup_ui()
        self._update_theme_style()

        ThemeEngine.instance().themeChanged.connect(self._on_theme_changed)

    def wheelEvent(self, event: QWheelEvent):
        """卡片外围滚轮透传，确保光标在卡片内边距等空白处时也能平滑驱动外层页面"""
        event.ignore()

    def _setup_ui(self):
        is_header_legend = self.show_legend and self.legend_position in ("header-left", "top-left", "header", "auto")

        # ── 1. 顶部标题栏与工具/图例按钮 ──
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 4)
        self.header_layout.setSpacing(10)

        # 顶部左侧图例容器 (对标顶部左侧紧凑显示需求)
        self.legend_container = QWidget(self)
        self.legend_layout = QHBoxLayout(self.legend_container)
        self.legend_layout.setContentsMargins(0, 0, 0, 0)
        self.legend_layout.setSpacing(6)

        if is_header_legend:
            self.header_layout.addWidget(self.legend_container)

        # 标题与副标题
        self.title_box = QVBoxLayout()
        self.title_box.setSpacing(2)

        self.title_label = QLabel(self._title_text, self)
        font_title = QFont("Segoe UI", 11, QFont.Weight.Bold)
        self.title_label.setFont(font_title)
        if self.title_alignment == "center":
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_box.addWidget(self.title_label)
        self.title_label.setVisible(bool(self._title_text))

        self.subtitle_label = QLabel(self._subtitle_text, self)
        font_sub = QFont("Segoe UI", 9)
        self.subtitle_label.setFont(font_sub)
        if self.title_alignment == "center":
            self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_box.addWidget(self.subtitle_label)
        self.subtitle_label.setVisible(bool(self._subtitle_text))

        self.header_layout.addLayout(self.title_box, 1)

        # 若是居中标题且图例在左侧，在右侧添加占位保持标题在卡片中精确对称居中
        if is_header_legend and self.title_alignment == "center" and self.enable_actions:
            self.header_right_spacer = QWidget(self)
            self.header_right_spacer.setFixedWidth(64)
            self.header_layout.addWidget(self.header_right_spacer)

        # 工具栏操作按钮 (全矢量图标驱动)
        self.btn_reset_zoom = QPushButton("还原", self)
        self.btn_reset_zoom.setIconSize(QSize(14, 14))
        self.btn_reset_zoom.setToolTip("重置图表缩放与平移 (亦可双击画板重置)")
        self.btn_reset_zoom.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset_zoom.setFixedHeight(26)
        self.btn_reset_zoom.clicked.connect(self.reset_zoom)
        self.header_layout.addWidget(self.btn_reset_zoom)

        self.btn_toggle_smooth = QPushButton("平滑", self)
        self.btn_toggle_smooth.setIconSize(QSize(14, 14))
        self.btn_toggle_smooth.setCheckable(True)
        self.btn_toggle_smooth.setChecked(self.enable_smooth)
        self.btn_toggle_smooth.setToolTip("开启/关闭三阶样条贝塞尔平滑曲线")
        self.btn_toggle_smooth.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_smooth.setFixedHeight(26)
        self.btn_toggle_smooth.clicked.connect(self._toggle_smooth_curve)
        self.header_layout.addWidget(self.btn_toggle_smooth)

        self.btn_export = QPushButton("导出图片", self)
        self.btn_export.setIconSize(QSize(14, 14))
        self.btn_export.setToolTip("将图表无损保存为高清图片")
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.setFixedHeight(26)
        self.btn_export.clicked.connect(self.export_image)
        self.header_layout.addWidget(self.btn_export)

        if not self.show_legacy_toolbar:
            self.btn_reset_zoom.hide()
            self.btn_toggle_smooth.hide()
            self.btn_export.hide()

        self.add_layout(self.header_layout)

        if not is_header_legend:
            # 独立第 2 行图例栏
            self.legend_layout.addStretch(1)
            self.add_widget(self.legend_container)

        # ── 2. 核心图表画板 (Canvas) ──
        self.canvas = _ChartCanvas(self)
        self.canvas.seriesHovered.connect(self._on_canvas_series_hovered)
        self.canvas.pointHovered.connect(self.pointHovered)
        self.add_widget(self.canvas, stretch=1)

        # ── 3. 右上角现代悬浮操作胶囊栏 (Floating Action Capsule，对标图一、图二、图三) ──
        if self.enable_actions:
            self.action_bar = _ChartActionBar(self, is_fullscreen=self.is_fullscreen, parent=self)
            if self.auto_hide_actions and not self.is_fullscreen:
                self.action_bar.setVisible(False)
            else:
                self.action_bar.setVisible(True)

    def minimumSizeHint(self) -> QSize:
        return QSize(180, 160)

    def sizeHint(self) -> QSize:
        return QSize(320, 240)

    # ──────────── 数据管理与 API ────────────

    def add_series(
        self,
        name: str,
        data: Sequence[Union[float, int, Tuple[float, float]]],
        color: Optional[Union[str, QColor]] = None,
        line_style: str = "solid",
        line_width: float = 1.8,
        smooth: Optional[bool] = None,
        area: Optional[bool] = None,
        marker: bool = True,
        gradient_fill: Optional[bool] = None,
    ) -> MkSeries:
        """
        向图表添加一条数据折线/曲线
        
        参数:
            name: 系列名称 (如 "train/loss", "yolov11n")
            data: 数据列表，支持纯数值列表 [0.2, 0.4, 0.6] 或坐标元组列表 [(0, 0.2), (10, 0.4)]
            color: 自定义颜色 (16进制/QColor)，未指定时自动从现代调色板选取
            line_style: "solid" (实线), "dashed" (虚线), "dotted" (点线)
            line_width: 线条粗细
            smooth: 是否启用贝塞尔平滑曲线 (默认继承图表全局设置)
            area: 是否启用半透明面积渐变填充
            marker: 是否绘制数据小圆点标记
            gradient_fill: 面积渐变填充别名 (等同于 area)
        """
        if color is None:
            idx = len(self.series_list)
            color = DEFAULT_CHART_COLORS[idx % len(DEFAULT_CHART_COLORS)]

        is_smooth = self.enable_smooth if smooth is None else bool(smooth)
        if gradient_fill is not None:
            area = gradient_fill
        is_area = self.enable_area_fill if area is None else bool(area)

        series = MkSeries(
            name=name,
            data=data,
            color=color,
            line_style=line_style,
            line_width=line_width,
            smooth=is_smooth,
            area=is_area,
            marker=marker,
        )
        self.series_list.append(series)
        self._rebuild_legend()
        self.canvas.update()
        return series

    def set_series_data(self, name: str, data: Sequence[Union[float, int, Tuple[float, float]]]):
        """更新指定名称系列的数据点"""
        for s in self.series_list:
            if s.name == name:
                s.set_data(data)
                self.canvas.update()
                return

    def clear_series(self):
        """清空所有数据系列"""
        self.series_list.clear()
        self.highlight_series = None
        self._rebuild_legend()
        self.canvas.reset_view()

    def set_highlight_series(self, name: Optional[str]):
        """对标 nearestLine：从外部联动高亮指定曲线（如左侧模型列表悬停时）"""
        if self.highlight_series != name:
            self.highlight_series = name
            self.canvas.update()

    def clear_highlight(self):
        """清除高亮状态"""
        self.set_highlight_series(None)

    def set_series_visible(self, name: str, visible: bool):
        """设置某条曲线是否可见"""
        for s in self.series_list:
            if s.name == name:
                s.visible = bool(visible)
                self._update_legend_states()
                self.canvas.update()
                break

    def reset_zoom(self):
        """重置视口到完整数据全景"""
        self.canvas.reset_view()

    def is_zoomed(self) -> bool:
        """判断当前图表视口是否处于缩放/放大状态"""
        return self.canvas.is_zoomed()

    @property
    def display_title(self) -> str:
        """获取图表显示标题"""
        return self._title_text

    @property
    def series_data(self) -> Dict[str, Dict]:
        """获取已加载的数据系列字典，方便外部检查与测试断言"""
        return {
            s.name: {
                "values": [p[1] for p in s.points],
                "epochs": [p[0] for p in s.points],
                "color": s.color,
                "linestyle": s.line_style,
            }
            for s in self.series_list
        }

    def update_series(self, series_dict: Dict[str, Dict]):
        """
        批量更新图表中的多条数据系列 (便捷适配器)
        series_dict 格式: {
            "model_name": {
                "values": [0.1, 0.8, 0.3],
                "epochs": [1, 2, 3], # 可选
                "color": "#2563EB",  # 可选
                "linestyle": "-",     # 可选 ("-" 或 "--")
            }
        }
        """
        self.clear_series()
        for name, s_info in series_dict.items():
            vals = s_info.get("values", [])
            epochs = s_info.get("epochs")
            if epochs and len(epochs) == len(vals):
                data = list(zip(epochs, vals))
            else:
                data = list(vals)
            color = s_info.get("color")
            ls = s_info.get("linestyle", "-")
            line_style = "dashed" if ls in ("--", "dashed") else "solid"
            # 单模型时开启微光渐变，多模型对比时关闭面积以防止遮挡重叠
            has_area = (len(series_dict) == 1 and self.enable_area_fill)
            self.add_series(
                name=name,
                data=data,
                color=color,
                line_style=line_style,
                smooth=self.enable_smooth,
                area=has_area,
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "action_bar") and self.enable_actions:
            bar_w = self.action_bar.sizeHint().width()
            bar_h = self.action_bar.sizeHint().height()
            self.action_bar.setGeometry(self.width() - bar_w - 14, 12, bar_w, bar_h)
            self.action_bar.raise_()

    def enterEvent(self, event):
        if self.auto_hide_actions and self.enable_actions and hasattr(self, "action_bar"):
            self.action_bar.setVisible(True)
            self.action_bar.raise_()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if (
            self.auto_hide_actions
            and self.enable_actions
            and hasattr(self, "action_bar")
            and not self.is_fullscreen
            and not self.action_bar.is_menu_open()
        ):
            self.action_bar.setVisible(False)
        super().leaveEvent(event)

    def open_fullscreen(self):
        """进入全屏放大视图 (对标 Ultralytics HUB，参考图二)"""
        dialog = _ChartFullscreenModal(self, parent=self.window())
        dialog.showMaximized()
        dialog.exec()

    def close_fullscreen(self):
        """退出全屏放大视图"""
        if self.fullscreen_parent_dialog:
            self.fullscreen_parent_dialog.close()

    def toggle_smooth(self, state: Optional[bool] = None):
        """切换曲线平滑 (Smooth Spline) 模式"""
        if state is None:
            self.enable_smooth = not self.enable_smooth
        else:
            self.enable_smooth = bool(state)
        self.btn_toggle_smooth.setChecked(self.enable_smooth)
        for s in self.series_list:
            s.smooth = self.enable_smooth
        if hasattr(self, "action_bar") and hasattr(self.action_bar, "action_smooth"):
            self.action_bar.action_smooth.setChecked(self.enable_smooth)
        self._update_theme_style()
        self.canvas.update()

    def _toggle_smooth_curve(self):
        self.toggle_smooth(self.btn_toggle_smooth.isChecked())

    def export_image(self, save_path: Optional[str] = None) -> QPixmap:
        """导出当前图表为高清 PNG 图像 (Download PNG)"""
        pix = self.grab()
        if not save_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出图表图像",
                f"{self._title_text or 'chart'}.png",
                "PNG Images (*.png);;JPEG Images (*.jpg)",
            )
            if file_path:
                pix.save(file_path)
        else:
            pix.save(save_path)
        return pix

    def export_csv(self, file_path: Optional[str] = None) -> str:
        """导出当前图表数据为 CSV 文件 (Download CSV)"""
        if not file_path:
            default_name = f"{self._title_text or 'chart_data'}.csv"
            safe_name = "".join(c for c in default_name if c.isalnum() or c in "._- ")
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出图表数据为 CSV",
                safe_name,
                "CSV Files (*.csv);;All Files (*.*)",
            )
            if not file_path:
                return ""

        all_x = sorted(list({pt[0] for s in self.series_list for pt in s.points}))
        series_maps = {s.name: dict(s.points) for s in self.series_list}

        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                headers = [self.x_label or "Epoch / X"] + [s.name for s in self.series_list]
                writer.writerow(headers)
                for x in all_x:
                    row = [x] + [series_maps[s.name].get(x, "") for s in self.series_list]
                    writer.writerow(row)
        except Exception as e:
            print(f"Failed to export CSV: {e}")
        return file_path

    def export_json(self, file_path: Optional[str] = None) -> str:
        """导出当前图表数据为 JSON 文件 (Download JSON)"""
        if not file_path:
            default_name = f"{self._title_text or 'chart_data'}.json"
            safe_name = "".join(c for c in default_name if c.isalnum() or c in "._- ")
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出图表数据为 JSON",
                safe_name,
                "JSON Files (*.json);;All Files (*.*)",
            )
            if not file_path:
                return ""

        data = {
            "title": self._title_text,
            "subtitle": self._subtitle_text,
            "x_label": self.x_label,
            "y_label": self.y_label,
            "series": [
                {
                    "name": s.name,
                    "color": s.color.name() if s.color else "",
                    "line_style": s.line_style,
                    "data": s.points,
                }
                for s in self.series_list
            ],
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to export JSON: {e}")
        return file_path

    def format_y_val(self, val: float) -> str:
        """数值格式化展示"""
        if abs(val) < 1e-4:
            return "0.00"
        elif abs(val) >= 1000:
            return f"{val:.0f}"
        elif abs(val) >= 10:
            return f"{val:.1f}"
        elif abs(val) >= 1:
            return f"{val:.2f}"
        else:
            return f"{val:.3f}"

    def format_x_val(self, val: float) -> str:
        if abs(val - round(val)) < 1e-4:
            return f"{int(round(val))}"
        return f"{val:.1f}"

    def _rebuild_legend(self):
        # 清除旧图例
        while self.legend_layout.count() > 0:
            item = self.legend_layout.takeAt(0)
            if item.widget():
                w = item.widget()
                w.setParent(None)
                w.deleteLater()
        self._legend_pills.clear()

        is_header = self.legend_position in ("header-left", "top-left", "header", "auto")

        # 重新生成图例胶囊
        for s in self.series_list:
            pill = _LegendItemPill(s, self, self.legend_container)
            self.legend_layout.addWidget(pill)
            self._legend_pills.append(pill)

        if not is_header:
            self.legend_layout.addStretch(1)

        self.legend_container.setVisible(bool(self.series_list) and self.show_legend and self.legend_position != "none")

    def _update_legend_states(self):
        for pill in self._legend_pills:
            pill._update_appearance()

    def _on_canvas_series_hovered(self, name: str):
        self.seriesHovered.emit(name)

    def _on_theme_changed(self, theme_name: str = ""):
        self._update_theme_style()

    def _update_theme_style(self):
        is_dark = ThemeEngine.is_dark()
        fg = ThemeEngine.get("--fg", "#F4F4F5" if is_dark else "#0F172A")
        muted = ThemeEngine.get("--text-muted", "#A1A1AA" if is_dark else "#64748B")
        border = ThemeEngine.get("--border", "#27272A" if is_dark else "#E2E8F0")
        primary = ThemeEngine.get("--primary", "#3B82F6")
        primary_text = readable_text(primary)

        self.title_label.setStyleSheet(f"color: {fg}; background: transparent;")
        self.subtitle_label.setStyleSheet(f"color: {muted}; background: transparent;")

        # 小工具栏按钮通用样式
        btn_qss = f"""
        QPushButton {{
            background-color: {"rgba(255, 255, 255, 0.06)" if is_dark else "#FFFFFF"};
            border: 1px solid {border};
            border-radius: 6px;
            color: {fg};
            padding: 2px 10px;
            font-size: 11px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {"rgba(255, 255, 255, 0.12)" if is_dark else "#F1F5F9"};
        }}
        QPushButton:checked {{
            background-color: {primary};
            color: {primary_text};
            border-color: transparent;
        }}
        """
        for b in [self.btn_reset_zoom, self.btn_toggle_smooth, self.btn_export]:
            b.setStyleSheet(btn_qss)

        # 动态更新高分辨率矢量图标
        try:
            from monkeyqt.icons import PhArrowCounterClockwise, PhWaveSine, PhDownloadSimple
            self.btn_reset_zoom.setIcon(PhArrowCounterClockwise.icon(size=14, color=fg))
            smooth_col = primary_text if self.btn_toggle_smooth.isChecked() else fg
            self.btn_toggle_smooth.setIcon(PhWaveSine.icon(size=14, color=smooth_col))
            self.btn_export.setIcon(PhDownloadSimple.icon(size=14, color=fg))
        except Exception:
            pass

        if hasattr(self, "action_bar") and self.action_bar:
            self.action_bar._update_theme_style()

        self._update_legend_states()
        self.canvas.update()

    def wheelEvent(self, event):
        """确保外层卡片与留白区域滚轮事件无损向上传播至父级 QScrollArea"""
        event.ignore()
