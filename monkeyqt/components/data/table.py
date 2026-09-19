# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import readable_text


class MkTableHeaderView(QHeaderView):
    """
    MkTableHeaderView - 自适应圆角表头视图。
    精准绘制顶部左、右圆角背景，彻底解决 QTableView / QTableWidget 顶部左右圆角被直角表头遮挡模糊的问题。
    """
    def __init__(self, orientation=Qt.Orientation.Horizontal, radius=6.0, bg_color="#F1F5F9", border_color="#E2E8F0", parent=None):
        super().__init__(orientation, parent)
        self._radius = float(radius)
        self._bg_color = QColor(bg_color) if isinstance(bg_color, str) else bg_color
        self._border_color = QColor(border_color) if isinstance(border_color, str) else border_color
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_radius(self, radius: float):
        self._radius = float(radius)
        self.viewport().update()

    def set_bg_color(self, color):
        self._bg_color = QColor(color) if isinstance(color, str) else color
        self.viewport().update()

    def set_border_color(self, color):
        self._border_color = QColor(color) if isinstance(color, str) else color
        self.viewport().update()

    def paintEvent(self, event):
        # 1. 绘制平滑抗锯齿的顶部圆角背景（仅左上和右上带圆角，右下和左下为平直边缘）
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.viewport().rect())
        r = float(max(0.0, self._radius - 1.0))

        if r > 0.5:
            path = QPainterPath()
            path.moveTo(rect.left(), rect.bottom())
            path.lineTo(rect.left(), rect.top() + r)
            path.quadTo(rect.left(), rect.top(), rect.left() + r, rect.top())
            path.lineTo(rect.right() - r, rect.top())
            path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + r)
            path.lineTo(rect.right(), rect.bottom())
            path.closeSubpath()
            painter.fillPath(path, self._bg_color)
        else:
            painter.fillRect(rect, self._bg_color)

        painter.end()

        # 2. 调用基类绘制表头内容（文本、排序箭头等）
        super().paintEvent(event)

        # 3. 绘制表头底部分割线
        if self._border_color.isValid() and self._border_color.alpha() > 0:
            p2 = QPainter(self.viewport())
            p2.setPen(QPen(self._border_color, 1.0))
            y = self.viewport().rect().height() - 1
            p2.drawLine(0, y, self.viewport().rect().width(), y)
            p2.end()


class MkTable(QTableWidget):
    """
    MkTable 组件 - 继承自 QTableWidget，支持 68 种主题风格的自适应表格绘制。
    """
    def __init__(self, rows=0, columns=0, parent=None):
        super().__init__(rows, columns, parent)
        self._header_view = MkTableHeaderView(Qt.Orientation.Horizontal, parent=self)
        self.setHorizontalHeader(self._header_view)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setShowGrid(False)
        self.setAlternatingRowColors(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setMinimumSectionSize(90)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setMinimumHeight(180)
        
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def set_headers(self, headers):
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        for col_idx, header in enumerate(headers):
            item = self.horizontalHeaderItem(col_idx)
            if item:
                item.setToolTip(header)

    def set_data(self, data):
        self.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                val_str = str(value)
                item = QTableWidgetItem(val_str)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                # item.setToolTip(val_str) will be called automatically via setItem override
                self.setItem(row_idx, col_idx, item)

    def setItem(self, row, column, item):
        if item and not item.toolTip():
            item.setToolTip(item.text())
        super().setItem(row, column, item)

    def auto_fit_columns(self):
        """
        根据当前单元格内容的长度，自动调整所有列宽，并允许用户后续手动拖拽调整。
        """
        for col_idx in range(self.columnCount()):
            self.horizontalHeader().setSectionResizeMode(col_idx, QHeaderView.ResizeMode.ResizeToContents)
        
        # 强制更新布局计算，以便 columnWidth 获得实际数值
        self.horizontalHeader().updateGeometries()
        
        # 换回 Interactive 模式，以便用户能够手动拖拉调整
        for col_idx in range(self.columnCount()):
            width = self.columnWidth(col_idx)
            self.horizontalHeader().setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Interactive)
            self.setColumnWidth(col_idx, max(width, 90))

    def update(self, *args):
        """Safely handle update() without arguments (like QWidget.update) or with QModelIndex."""
        if not args:
            self.viewport().update()
            super(QAbstractItemView, self).update()
        else:
            super().update(*args)

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        border = t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0")
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        surface_muted = t.get("--surface-muted", "#F1F5F9")
        radius_val = 0.0 if t.is_brutal() or t.is_pixel() else float(str(t.get("--radius", "6px")).replace("px", ""))
        radius = f"{int(radius_val)}px"
        active_fg = readable_text(primary)
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        grid_rule = "#000000" if t.is_brutal() or t.is_pixel() else border
        family = "Consolas" if t.is_pixel() else '"Segoe UI", "Microsoft YaHei"'
        weight = "900" if t.is_brutal() else "700"

        if t.is_glow():
            surface = "#10121C"
            surface_muted = "#182033"
            fg = "#E5F6FF"

        if hasattr(self, "_header_view") and self._header_view is not None:
            self._header_view.set_radius(radius_val)
            self._header_view.set_bg_color(surface_muted)
            self._header_view.set_border_color(grid_rule)

        self.setStyleSheet(f"""
            QTableWidget {{
                background: {surface};
                color: {fg};
                border: {border_rule};
                border-radius: {radius};
                gridline-color: transparent;
                font-family: {family};
                font-size: 13px;
                outline: none;
                selection-background-color: {primary};
                selection-color: {active_fg};
            }}
            QHeaderView {{
                background-color: transparent;
                background: transparent;
                border: none;
            }}
            QHeaderView::section {{
                background-color: transparent;
                background: transparent;
                color: {muted if not t.is_brutal() else '#000000'};
                border: none;
                padding: 10px 9px;
                font-weight: {weight};
            }}
            QTableWidget::item {{
                border-bottom: 1px solid {grid_rule};
                padding: 8px 9px;
            }}
            QTableWidget::item:hover {{
                background: {surface_muted};
            }}
            QTableWidget::item:selected {{
                background: {primary};
                color: {active_fg};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 9px;
                margin: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {muted};
                border-radius: 4px;
                min-height: 26px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
                border: none;
            }}
        """)
        self.viewport().update()
