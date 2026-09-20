# -*- coding: utf-8 -*-
"""
MkProTable - 现代化前端仪表盘数据表格组件 (Modern Dashboard Pro Table)
基于 Shadcn-UI / Tailwind 设计美学封装的高级数据表格。

主要特性：
- 继承 MkQWidget(role="card")，完美自适应 68 种主题风格；
- 自由调节外边框线粗细 (border_width)、颜色 (border_color) 与圆角 (border_radius)；
- 顶部主标题 (title)、副标题 (description) 与快速模糊搜索框 (searchable) 纯参数化按需开启；
- 复选框多选列 (selectable=True)：支持表头全选/反选、跨分页多选状态持久化与 selectionChanged 信号；
- 多媒体单元格：
  * type="image": 6px 圆角缩略图，悬停眼眸浮层，点击自动弹出 MkLightboxDialog 高清大图查看器；
  * type="video": 6px 圆角缩略图与播放角标，点击自动弹出 MkVideoPlayerDialog 视频播放器；
- 丰富富文本单元格渲染：
  * avatar_text: 圆形头像 (图片缩略图或首字母彩色徽章) + 蓝色超链接文字标题；
  * badge / tag: 胶囊分类标签 (内置文件夹 Project、数据库 Dataset、文件等 Phosphor 图标)；
  * status: 柔和背景状态药丸 (带打勾/状态点，支持 Completed, Ready, Running, Pending, Failed 等状态)；
  * text / date: 基础文本与日期展示 (支持相对时间与标准格式，超出自动省略与 Tooltip)；
  * action: 操作列 (编辑、删除、查看等图标按钮组)；
- 表头多列排序指示器 (↑↓ 待选、↑ 升序、↓ 降序，点击循环切换排序)；
- 底部现代化控制栏：每页行数下拉切换 (10/20/50/100 行/页)、总条数统计与前后翻页器。
"""

import os
import re
from typing import List, Dict, Any, Optional
from PySide6.QtCore import Qt, Signal, QRectF, QRect, QSize, QPoint, QEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QHeaderView, QPushButton, QSizePolicy,
    QComboBox, QGraphicsDropShadowEffect, QApplication, QMenu
)
from PySide6.QtGui import (
    QPainter, QPainterPath, QColor, QPen, QFont, QPixmap, QCursor,
    QKeySequence, QAction
)

from monkeyqt.components.layout.widget import MkQWidget
from monkeyqt.components.basic.checkbox import MkCheckBox
from monkeyqt.components.form.input import MkInput
from monkeyqt.core.icons import MkPhosphorIcon
from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import readable_text


class MkPageSizeDropdownPopup(MkQWidget):
    """
    轻量无边框浮动卡片下拉弹窗 (Frameless Floating Card Dropdown)
    彻底消除 Windows 原生 HWND 矩形黑角，支持平滑抗锯齿圆角、柔和外发散阴影与对勾指示器。
    """
    MARGIN = 8

    def __init__(self, combo: "MkPageSizeComboBox"):
        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.combo = combo
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        root_layout.setSpacing(0)

        self.card = QFrame(self)
        self.card.setObjectName("MkPageSizeDropdownCard")
        self._card_layout = QVBoxLayout(self.card)
        self._card_layout.setContentsMargins(4, 4, 4, 4)
        self._card_layout.setSpacing(2)

        self.shadow = QGraphicsDropShadowEffect(self.card)
        self.shadow.setBlurRadius(16)
        self.shadow.setOffset(0, 3)
        self.shadow.setColor(QColor(0, 0, 0, 35))
        self.card.setGraphicsEffect(self.shadow)

        root_layout.addWidget(self.card)
        self.item_buttons = []

    def refresh_items(self):
        while self._card_layout.count() > 0:
            item = self._card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.item_buttons.clear()

        t = ThemeEngine
        is_dark = t.is_dark()
        primary = t.get("--primary", "#3B82F6")
        fg = t.get("--fg", "#1E293B")
        surface_muted = t.get("--surface-muted", "#F1F5F9")
        curr_idx = self.combo.currentIndex()

        for idx in range(self.combo.count()):
            text = self.combo.itemText(idx)
            is_selected = (idx == curr_idx)

            btn = QPushButton(self.card)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(28)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            btn_lay = QHBoxLayout(btn)
            btn_lay.setContentsMargins(8, 0, 8, 0)
            btn_lay.setSpacing(6)

            lbl_txt = QLabel(text, btn)
            lbl_txt.setFont(QFont('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif', 9, QFont.Weight.Medium if is_selected else QFont.Weight.Normal))
            lbl_txt.setStyleSheet(f"color: {primary if is_selected else fg}; background: transparent;")
            btn_lay.addWidget(lbl_txt)
            btn_lay.addStretch()

            if is_selected:
                lbl_check = QLabel("✓", btn)
                lbl_check.setFont(QFont('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 9, QFont.Weight.Bold))
                lbl_check.setStyleSheet(f"color: {primary}; background: transparent;")
                btn_lay.addWidget(lbl_check)

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {surface_muted if is_selected else 'transparent'};
                    border: none;
                    border-radius: 4px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {surface_muted};
                }}
            """)
            btn.clicked.connect(lambda checked=False, i=idx: self._on_item_selected(i))
            self._card_layout.addWidget(btn)
            self.item_buttons.append(btn)

    def _on_item_selected(self, index: int):
        self.hide()
        self.combo.setCurrentIndex(index)

    def update_theme_style(self):
        t = ThemeEngine
        is_dark = t.is_dark()
        surface = t.get("--surface", "#FFFFFF")
        border = t.get("--border", "#E2E8F0")
        radius = 0 if t.is_brutal() or t.is_pixel() else 6

        if is_dark:
            self.shadow.setColor(QColor(0, 0, 0, 120))
        else:
            self.shadow.setColor(QColor(0, 0, 0, 35))

        self.card.setStyleSheet(f"""
            QFrame#MkPageSizeDropdownCard {{
                background-color: {surface};
                border: 1px solid {border};
                border-radius: {radius}px;
            }}
        """)

    def show_at_combo(self):
        self.update_theme_style()
        self.refresh_items()

        combo = self.combo
        count = combo.count()
        if count == 0:
            return

        item_h = 28 + 2
        content_h = count * item_h + 8
        total_h = content_h + self.MARGIN * 2
        card_w = max(combo.width() + 10, 86)
        total_w = card_w + self.MARGIN * 2

        self.resize(total_w, total_h)

        screen = combo.screen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)
        global_pos = combo.mapToGlobal(QPoint(0, 0))

        space_below = avail.bottom() - (global_pos.y() + combo.height())
        space_above = global_pos.y() - avail.top()

        if space_below < content_h + 10 and space_above > space_below:
            popup_y = global_pos.y() - total_h + self.MARGIN + 3
        else:
            popup_y = global_pos.y() + combo.height() - self.MARGIN - 3

        popup_x = global_pos.x() - self.MARGIN
        if popup_x + total_w > avail.right():
            popup_x = avail.right() - total_w
        if popup_x < avail.left():
            popup_x = avail.left()

        self.move(popup_x, popup_y)
        self.show()


class MkPageSizeComboBox(QComboBox):
    """
    轻量紧凑型分页行数选择下拉框，自带抗锯齿居中下箭头 ∨。
    采用 MkPageSizeDropdownPopup 彻底解决 Windows 原生弹窗 4 个黑角问题。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MkProTablePageSizeCombo")
        self.setFixedHeight(30)
        self.setFixedWidth(78)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._popup = MkPageSizeDropdownPopup(self)
        self.update_theme_style()

    def update_theme_style(self):
        t = ThemeEngine
        border = t.get("--border", "#E2E8F0")
        surface = t.get("--surface", "#FFFFFF")
        fg = t.get("--fg", "#1E293B")
        surface_muted = t.get("--surface-muted", "#F8FAFC")
        focus_border = t.get("--input-focus-border", "#FFFFFF" if t.is_dark() else "#0F172A")
        radius = 0 if t.is_brutal() or t.is_pixel() else 6

        self.setStyleSheet(f"""
            QComboBox#MkProTablePageSizeCombo {{
                background-color: {surface};
                border: 1px solid {border};
                border-radius: {radius}px;
                padding-left: 8px;
                padding-right: 20px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
                font-size: 12px;
                color: {fg};
                font-weight: 500;
            }}
            QComboBox#MkProTablePageSizeCombo:hover {{
                border-color: {focus_border};
                background-color: {surface_muted};
            }}
            QComboBox#MkProTablePageSizeCombo::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 18px;
                border-left: none;
                background: transparent;
            }}
            QComboBox#MkProTablePageSizeCombo::down-arrow {{
                image: none;
            }}
        """)
        if hasattr(self, "_popup"):
            self._popup.update_theme_style()

    def showPopup(self):
        self._popup.show_at_combo()

    def hidePopup(self):
        self._popup.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._popup.isVisible():
                self._popup.hide()
            else:
                self.showPopup()
            event.accept()
            return
        super().mousePressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_dark = ThemeEngine.is_dark()
        arrow_color = QColor(ThemeEngine.get("--input-focus-border", "#FFFFFF" if is_dark else "#0F172A") if self.underMouse() else ThemeEngine.get("--text-muted", "#64748B"))
        painter.setPen(QPen(arrow_color, 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        
        cx = self.width() - 13
        cy = self.height() // 2 - 1
        path = QPainterPath()
        path.moveTo(cx - 3.5, cy - 1.5)
        path.lineTo(cx, cy + 2)
        path.lineTo(cx + 3.5, cy - 1.5)
        painter.drawPath(path)
        painter.end()


class MkProTableWidget(QTableWidget):
    """
    高级整行悬停高亮与划词复制数据表格主视口 (Whole-Row Hover Pro Table Viewport)
    鼠标移动或点击某一行时，整行背景无缝高亮（参考 Web 前端 tr:hover），完美支持所有 68 种主题风格。
    支持鼠标划词选择文本与 Ctrl+C 快捷复制。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hovered_row = -1
        self._active_row = -1
        self._hover_bg_color = QColor("#F8FAFC")
        self._divider_color = QColor("#E2E8F0")
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.viewport().installEventFilter(self)

    def set_hover_color(self, color: QColor):
        self._hover_bg_color = color
        self.viewport().update()

    def set_divider_color(self, color: QColor):
        self._divider_color = color
        self.viewport().update()

    def set_hovered_row(self, row: int):
        if self._hovered_row != row:
            self._hovered_row = row
            self.viewport().update()

    def set_active_row(self, row: int):
        if self._active_row != row:
            self._active_row = row
            self.viewport().update()

    def bind_cell_widget(self, widget: QWidget, row_idx: int):
        """递归绑定悬停事件过滤与透明背景透传"""
        widget.setProperty("table_row_idx", row_idx)
        widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        widget.setStyleSheet("background: transparent;")
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.setProperty("table_row_idx", row_idx)
            child.installEventFilter(self)

    def eventFilter(self, obj, event):
        t = event.type()
        if t in (QEvent.Type.MouseMove, QEvent.Type.Enter):
            row_idx = obj.property("table_row_idx")
            if row_idx is not None:
                self.set_hovered_row(row_idx)
            elif obj == self.viewport():
                pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                r = self.rowAt(pos.y())
                self.set_hovered_row(r)
        elif t == QEvent.Type.MouseButtonPress:
            row_idx = obj.property("table_row_idx")
            if row_idx is not None:
                self.set_active_row(row_idx)
            elif obj == self.viewport():
                pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                r = self.rowAt(pos.y())
                if r >= 0:
                    self.set_active_row(r)
        elif t == QEvent.Type.Leave:
            if obj == self.viewport():
                self.set_hovered_row(-1)
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Copy):
            # 1. 优先复制当前获得焦点且有选中文本的控件 (如划词选中的 QLabel)
            focus_w = QApplication.focusWidget()
            if isinstance(focus_w, QLabel) and focus_w.hasSelectedText():
                QApplication.clipboard().setText(focus_w.selectedText())
                event.accept()
                return

            # 2. 检查是否有任一可见文本单元格当前处于划词选中状态
            for r in range(self.rowCount()):
                for c in range(self.columnCount()):
                    w = self.cellWidget(r, c)
                    if w:
                        for lbl in w.findChildren(QLabel):
                            if lbl.hasSelectedText():
                                QApplication.clipboard().setText(lbl.selectedText())
                                event.accept()
                                return

            # 3. 若无局部划词，则复制当前激活行或悬停行的整行数据 (制表符分隔，便于粘贴至 Excel/代码)
            target_row = self._hovered_row if self._hovered_row >= 0 else self._active_row
            if 0 <= target_row < self.rowCount():
                row_texts = []
                for c in range(self.columnCount()):
                    w = self.cellWidget(target_row, c)
                    if w:
                        cell_txt = ""
                        for lbl in w.findChildren(QLabel):
                            t_str = lbl.text().strip()
                            if t_str and not lbl.pixmap():
                                cell_txt = t_str
                                break
                        if cell_txt:
                            row_texts.append(cell_txt)
                    else:
                        item = self.item(target_row, c)
                        if item and item.text().strip():
                            row_texts.append(item.text().strip())
                if row_texts:
                    QApplication.clipboard().setText("\t".join(row_texts))
                    event.accept()
                    return

        super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        # 右键上下文菜单：支持划词复制与整行复制
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #18181B;
                color: #F8FAFC;
                border: 1px solid #27272A;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 0.12);
            }
        """)

        # 检查是否有划词选中
        selected_text = ""
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                w = self.cellWidget(r, c)
                if w:
                    for lbl in w.findChildren(QLabel):
                        if lbl.hasSelectedText():
                            selected_text = lbl.selectedText()
                            break
            if selected_text:
                break

        if selected_text:
            act_copy_sel = menu.addAction(f"复制选中文本 (\"{selected_text[:16]}{'...' if len(selected_text) > 16 else ''}\")")
            act_copy_sel.triggered.connect(lambda: QApplication.clipboard().setText(selected_text))
            menu.addSeparator()

        target_row = self.rowAt(event.pos().y())
        if target_row >= 0:
            act_copy_row = menu.addAction("复制整行文本")
            def _copy_row():
                row_texts = []
                for c in range(self.columnCount()):
                    w = self.cellWidget(target_row, c)
                    if w:
                        for lbl in w.findChildren(QLabel):
                            t_str = lbl.text().strip()
                            if t_str and not lbl.pixmap():
                                row_texts.append(t_str)
                                break
                    else:
                        item = self.item(target_row, c)
                        if item and item.text().strip():
                            row_texts.append(item.text().strip())
                if row_texts:
                    QApplication.clipboard().setText("\t".join(row_texts))
            act_copy_row.triggered.connect(_copy_row)

        if not menu.isEmpty():
            menu.exec(event.globalPos())

    def paintEvent(self, event):
        # 1. 绘制整行悬停或激活高亮背景 (Whole-Row Hover / Active Highlight)
        row_to_highlight = self._hovered_row if self._hovered_row >= 0 else self._active_row
        if 0 <= row_to_highlight < self.rowCount():
            y = self.rowViewportPosition(row_to_highlight)
            h = self.rowHeight(row_to_highlight)
            if h > 0 and self._hover_bg_color.isValid():
                painter = QPainter(self.viewport())
                painter.fillRect(QRect(0, y, self.viewport().width(), h), self._hover_bg_color)
                painter.end()

        # 2. 调用基类绘制所有 items 与 widgets
        super().paintEvent(event)

        # 3. 绘制行底部分隔线 (Subtle Row Dividers)
        painter = QPainter(self.viewport())
        painter.setPen(QPen(self._divider_color, 1.0))
        w = self.viewport().width()
        for r in range(self.rowCount()):
            y = self.rowViewportPosition(r) + self.rowHeight(r) - 1
            painter.drawLine(0, y, w, y)
        painter.end()


class MkProTableHeaderView(QHeaderView):
    """
    可排列表头视图 (Sortable HeaderView)
    支持列多选复选框、排序指示箭头 (↑↓ 未激活态、↑ 升序、↓ 降序)，点击循环排序。
    """
    sortRequested = Signal(int)  # logicalIndex
    headerCheckboxClicked = Signal(bool)

    def __init__(
        self,
        orientation=Qt.Orientation.Horizontal,
        radius: float = 12.0,
        border_width: int = 1,
        bg_color="#F8FAFC",
        border_color="#E2E8F0",
        fg_color="#475569",
        parent=None
    ):
        super().__init__(orientation, parent)
        self._radius = float(radius)
        self._border_width = border_width
        self._bg_color = QColor(bg_color)
        self._border_color = QColor(border_color)
        self._fg_color = QColor(fg_color)
        
        # 排序与复选框状态
        self._sort_index: Optional[int] = None
        self._sort_order: Optional[Qt.SortOrder] = None
        self._sortable_map: Dict[int, bool] = {}
        self._align_map: Dict[int, Qt.AlignmentFlag] = {}
        self._has_checkbox = False
        self._header_checked = False

        self.setSectionsClickable(True)
        self.sectionClicked.connect(self._on_section_clicked)
        self.setDefaultSectionSize(40)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 表头内置原生 MkCheckBox，与所有行内复选框 100% 相同尺寸 (18x18) 与相同 SVG/高对比度样式
        self.header_checkbox = MkCheckBox(parent=self.viewport())
        self.header_checkbox.setFixedSize(18, 18)
        self.header_checkbox.hide()
        self.header_checkbox.toggled.connect(self._on_header_checkbox_toggled)

    def _on_header_checkbox_toggled(self, checked: bool):
        self.headerCheckboxClicked.emit(checked)

    def set_has_checkbox(self, has_checkbox: bool):
        self._has_checkbox = bool(has_checkbox)
        self.update_checkbox_geometry()
        self.viewport().update()

    def set_header_checked(self, checked: bool):
        if hasattr(self, "header_checkbox"):
            self.header_checkbox.blockSignals(True)
            self.header_checkbox.setChecked(checked)
            self.header_checkbox.blockSignals(False)
            self.viewport().update()

    def update_checkbox_geometry(self):
        if not hasattr(self, "header_checkbox"):
            return
        if not self._has_checkbox or self.count() == 0:
            self.header_checkbox.hide()
            return
        col_w = self.sectionSize(0)
        col_x = self.sectionViewportPosition(0)
        cx = col_x + (col_w - 18) // 2
        cy = (self.height() - 18) // 2
        self.header_checkbox.move(cx, cy)
        self.header_checkbox.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_checkbox_geometry()

    def set_column_alignment(self, logical_index: int, alignment: Qt.AlignmentFlag):
        self._align_map[logical_index] = alignment
        self.viewport().update()

    def set_sort_state(self, logical_index: Optional[int], order: Optional[Qt.SortOrder]):
        self._sort_index = logical_index
        self._sort_order = order
        self.viewport().update()

    def set_sortable(self, logical_index: int, sortable: bool = True):
        self._sortable_map[logical_index] = sortable

    def set_theme_props(self, radius: float, border_width: int, bg_color: str, border_color: str, fg_color: str):
        self._radius = float(radius)
        self._border_width = border_width
        self._bg_color = QColor(bg_color)
        self._border_color = QColor(border_color)
        self._fg_color = QColor(fg_color)
        if hasattr(self, "header_checkbox"):
            self.header_checkbox._apply_style()
        self.viewport().update()

    def _on_section_clicked(self, logicalIndex: int):
        if logicalIndex == 0 and self._has_checkbox:
            self.header_checkbox.toggle()
            return

        if self._sortable_map.get(logicalIndex, True):
            self.sortRequested.emit(logicalIndex)

    def paintEvent(self, event):
        # 1. 绘制表头背景
        if self._bg_color.isValid() and self._bg_color.alpha() > 0:
            painter = QPainter(self.viewport())
            painter.fillRect(self.viewport().rect(), self._bg_color)
            painter.end()

        # 2. 调用基类绘制 sections
        super().paintEvent(event)

        # 保持复选框几何位置精确同步
        self.update_checkbox_geometry()

        # 3. 绘制表头底部分割线
        if self._border_color.isValid() and self._border_color.alpha() > 0:
            p2 = QPainter(self.viewport())
            p2.setPen(QPen(self._border_color, 1.0))
            y = self.viewport().rect().height() - 1
            p2.drawLine(0, y, self.viewport().rect().width(), y)
            p2.end()

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 若是复选框列，由原生的 self.header_checkbox 呈现，无需重复绘制
        if logicalIndex == 0 and self._has_checkbox:
            self.update_checkbox_geometry()
            painter.restore()
            return

        # 1. 取得文本与对齐方式
        model = self.model()
        header_text = ""
        if model:
            val = model.headerData(logicalIndex, self.orientation(), Qt.ItemDataRole.DisplayRole)
            if val is not None:
                header_text = str(val)

        align_flag = self._align_map.get(logicalIndex, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        is_sortable = self._sortable_map.get(logicalIndex, True)

        pad_left = 14
        pad_right = 28 if is_sortable else 14
        text_rect = rect.adjusted(pad_left, 0, -pad_right, 0)

        painter.setPen(self._fg_color)
        font = QFont('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif', 9, QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.drawText(text_rect, align_flag | Qt.TextFlag.TextSingleLine, header_text)

        # 2. 绘制右侧排序指示箭头
        if is_sortable:
            self._draw_sort_indicator(painter, rect, logicalIndex)

        painter.restore()

    def _draw_sort_indicator(self, painter: QPainter, rect, logicalIndex: int):
        is_active = (self._sort_index == logicalIndex and self._sort_order is not None)
        order = self._sort_order if is_active else None

        arrow_w = 12
        arrow_h = 14
        ax = rect.right() - arrow_w - 8
        ay = rect.top() + (rect.height() - arrow_h) / 2.0

        if not is_active:
            arrow_color = QColor(self._fg_color)
            arrow_color.setAlpha(120)
            painter.setPen(QPen(arrow_color, 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

            # 上箭头 ↑
            cx1 = ax + 3
            painter.drawLine(cx1, ay + 5, cx1, ay + 1)
            painter.drawLine(cx1 - 2, ay + 3, cx1, ay + 1)
            painter.drawLine(cx1 + 2, ay + 3, cx1, ay + 1)

            # 下箭头 ↓
            cx2 = ax + 9
            painter.drawLine(cx2, ay + 8, cx2, ay + 12)
            painter.drawLine(cx2 - 2, ay + 10, cx2, ay + 12)
            painter.drawLine(cx2 + 2, ay + 10, cx2, ay + 12)
        else:
            active_color = QColor(ThemeEngine.get("--primary", "#0284C7"))
            painter.setPen(QPen(active_color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            cx = ax + 6
            if order == Qt.SortOrder.AscendingOrder:
                # 升序 ↑
                painter.drawLine(cx, ay + 11, cx, ay + 3)
                painter.drawLine(cx - 3, ay + 6, cx, ay + 3)
                painter.drawLine(cx + 3, ay + 6, cx, ay + 3)
            else:
                # 降序 ↓
                painter.drawLine(cx, ay + 3, cx, ay + 11)
                painter.drawLine(cx - 3, ay + 8, cx, ay + 11)
                painter.drawLine(cx + 3, ay + 8, cx, ay + 11)


# ─────────────────────────────────────────────────────────────
# 现代化富单元格渲染控件
# ─────────────────────────────────────────────────────────────

class MkAvatarTextCell(MkQWidget):
    """带圆形头像 (首字母或图片) + 标题主链接的复合单元格"""
    clicked = Signal(str)

    def __init__(self, text: str, avatar: Optional[str] = None, color: Optional[str] = None, align=None, parent=None):
        super().__init__(parent)
        self.text = text
        self.avatar = avatar
        self.color = color or "#0284C7"
        self.align = align or (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(10)
        layout.setAlignment(self.align)

        # 头像组件
        self.avatar_label = QLabel(self)
        self.avatar_label.setFixedSize(32, 32)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._render_avatar()
        layout.addWidget(self.avatar_label)

        # 文字标签 (支持划词高亮与复制)
        self.text_label = QLabel(self.text, self)
        self.text_label.setFont(QFont('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif', 10, QFont.Weight.Medium))
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        layout.addWidget(self.text_label)

    def _render_avatar(self):
        pix = QPixmap(32, 32)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.avatar and os.path.exists(self.avatar):
            src = QPixmap(self.avatar).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            clip = QPainterPath()
            clip.addEllipse(0, 0, 32, 32)
            p.setClipPath(clip)
            p.drawPixmap(0, 0, src)
        else:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(self.color))
            p.drawEllipse(0, 0, 32, 32)

            initial = (self.text[0] if self.text else "?").upper()
            p.setPen(QColor("#FFFFFF"))
            p.setFont(QFont('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 10, QFont.Weight.Bold))
            p.drawText(QRectF(0, 0, 32, 32), Qt.AlignmentFlag.AlignCenter, initial)

        p.end()
        self.avatar_label.setPixmap(pix)


class MkBadgeCell(MkQWidget):
    """优雅胶囊标签单元格 (Tag / Badge)，支持可选 Phosphor 矢量小图标"""
    def __init__(self, text: str, icon: Optional[str] = None, align=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(0)
        layout.setAlignment(align or (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))

        pill = QFrame(self)
        pill.setObjectName("BadgePill")
        pill_layout = QHBoxLayout(pill)
        pill_layout.setContentsMargins(8, 3, 8, 3)
        pill_layout.setSpacing(5)

        if icon:
            ic_lbl = QLabel(pill)
            ic_lbl.setPixmap(MkPhosphorIcon.get_pixmap(icon, "#64748B", 14))
            pill_layout.addWidget(ic_lbl)

        txt_lbl = QLabel(text, pill)
        txt_lbl.setFont(QFont('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif', 9, QFont.Weight.Medium))
        txt_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        txt_lbl.setStyleSheet("color: #475569; background: transparent;")
        pill_layout.addWidget(txt_lbl)

        pill.setStyleSheet("""
            QFrame#BadgePill {
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        layout.addWidget(pill)


class MkStatusCell(MkQWidget):
    """状态药丸单元格，带柔和色块与微脉冲圆点指示器"""
    STATUS_MAP = {
        "completed": {"bg": "#ECFDF5", "border": "#A7F3D0", "dot": "#10B981", "text": "#047857", "label": "Completed"},
        "ready": {"bg": "#EFF6FF", "border": "#BFDBFE", "dot": "#3B82F6", "text": "#1D4ED8", "label": "Ready"},
        "running": {"bg": "#F5F3FF", "border": "#DDD6FE", "dot": "#8B5CF6", "text": "#6D28D9", "label": "Running"},
        "pending": {"bg": "#FFFBEB", "border": "#FDE68A", "dot": "#F59E0B", "text": "#B45309", "label": "Pending"},
        "failed": {"bg": "#FEF2F2", "border": "#FECACA", "dot": "#EF4444", "text": "#B91C1C", "label": "Failed"},
    }

    def __init__(self, raw_status: str, align=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(0)
        layout.setAlignment(align or (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))

        st_key = str(raw_status).lower().strip()
        cfg = self.STATUS_MAP.get(st_key, {
            "bg": "#F8FAFC", "border": "#E2E8F0", "dot": "#94A3B8", "text": "#475569", "label": str(raw_status).capitalize()
        })

        pill = QFrame(self)
        pill_layout = QHBoxLayout(pill)
        pill_layout.setContentsMargins(8, 4, 10, 4)
        pill_layout.setSpacing(6)

        dot = QFrame(pill)
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(f"background-color: {cfg['dot']}; border-radius: 3px;")
        pill_layout.addWidget(dot)

        txt = QLabel(cfg["label"], pill)
        txt.setFont(QFont('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif', 9, QFont.Weight.Medium))
        txt.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        txt.setStyleSheet(f"color: {cfg['text']}; background: transparent; border: none;")
        pill_layout.addWidget(txt)

        pill.setStyleSheet(f"""
            QFrame {{
                background-color: {cfg['bg']};
                border: 1px solid {cfg['border']};
                border-radius: 12px;
            }}
        """)
        layout.addWidget(pill)


class MkTextCell(MkQWidget):
    """支持鼠标滑选文本与快捷键复制的纯文本单元格 (Selectable Plain Text Cell)"""
    def __init__(self, text: str, align=None, parent=None):
        super().__init__(parent)
        self.text_value = str(text) if text is not None else ""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(0)
        align_flag = align or (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.setAlignment(align_flag)

        self.label = QLabel(self.text_value, self)
        self.label.setAlignment(align_flag)
        self.label.setFont(QFont('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif', 9))
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        self.label.setToolTip(self.text_value)
        self.label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.label)


class MkImageCellWidget(MkQWidget):
    """现代化图片缩略图单元格容器，支持圆角裁剪与悬停眼眸大图预览浮层"""
    clicked = Signal(str)

    def __init__(self, img_path: str, size: int = 36, radius: int = 6, parent=None):
        super().__init__(parent)
        self.img_path = img_path or ""
        self.box_size = size
        self.radius = radius
        self._is_hovered = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(size, size)
        self.pixmap = QPixmap(self.img_path) if (self.img_path and os.path.exists(self.img_path)) else QPixmap()

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        try:
            super().enterEvent(event)
        except Exception:
            pass

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        try:
            super().leaveEvent(event)
        except Exception:
            pass

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.img_path)
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        painter.setClipPath(path)

        if not self.pixmap.isNull():
            scaled = self.pixmap.scaled(
                self.rect().size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            is_dark = ThemeEngine.is_dark()
            bg = QColor("#1E293B" if is_dark else "#F1F5F9")
            fg = QColor("#94A3B8" if is_dark else "#64748B")
            painter.fillRect(self.rect(), bg)
            img_icon = MkPhosphorIcon.get_pixmap("image", fg.name(), 18)
            painter.drawPixmap((self.width() - 18) // 2, (self.height() - 18) // 2, img_icon)

        if self._is_hovered:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 110))
            eye_icon = MkPhosphorIcon.get_pixmap("eye", "#FFFFFF", 18)
            painter.drawPixmap((self.width() - 18) // 2, (self.height() - 18) // 2, eye_icon)

        painter.end()


class MkVideoCellWidget(MkQWidget):
    """现代化视频缩略图预览单元格容器，内置播放角标与弹窗播放器联动"""
    clicked = Signal(str)

    def __init__(self, video_path: str, thumbnail_path: Optional[str] = None, size: int = 36, radius: int = 6, parent=None):
        super().__init__(parent)
        self.video_path = video_path or ""
        self.box_size = size
        self.radius = radius
        self._is_hovered = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(size, size)
        self.pixmap = QPixmap(thumbnail_path) if (thumbnail_path and os.path.exists(thumbnail_path)) else QPixmap()

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        try:
            super().enterEvent(event)
        except Exception:
            pass

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        try:
            super().leaveEvent(event)
        except Exception:
            pass

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.video_path)
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        painter.setClipPath(path)

        if not self.pixmap.isNull():
            scaled = self.pixmap.scaled(
                self.rect().size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 80 if not self._is_hovered else 120))
        else:
            painter.fillRect(self.rect(), QColor("#0F172A" if not self._is_hovered else "#1E293B"))

        active_color = "#38BDF8" if self._is_hovered else "#FFFFFF"
        play_pix = MkPhosphorIcon.get_pixmap("play", active_color, 20)
        painter.drawPixmap((self.width() - 20) // 2, (self.height() - 20) // 2, play_pix)

        if self._is_hovered:
            painter.setPen(QPen(QColor("#38BDF8"), 1.2))
            painter.drawRoundedRect(rect.adjusted(0.6, 0.6, -0.6, -0.6), self.radius, self.radius)

        painter.end()


# ─────────────────────────────────────────────────────────────
# 主组件 MkProTable
# ─────────────────────────────────────────────────────────────

class MkProTable(MkQWidget):
    """
    MkProTable - 高级现代化仪表盘数据表格。
    基于 MkQWidget(role="card") 封装，开箱即用集成：
    - 多选复选框列 (selectable=True)：支持全选/反选与跨页持久化选择记忆；
    - 图片列 (type="image") 与 视频列 (type="video") 多媒体弹窗预览联动；
    - 自由调节外边框粗细 (border_width)、圆角 (border_radius) 与颜色 (border_color)；
    - 可配置标题/副标题、快速模糊搜索框；
    - 多列升降序循环表头指示器；
    - 每页条数下拉切换 (10/20/50/100 行/页) 与前后翻页导航；
    - 68 种主题风格自适应联动。
    """
    rowClicked = Signal(int, dict)
    actionTriggered = Signal(str, int, dict)
    selectionChanged = Signal(list)

    def __init__(
        self,
        columns: List[Dict[str, Any]] = None,
        data: List[Dict[str, Any]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        searchable: bool = True,
        search_placeholder: str = "搜索表格内容...",
        search_columns: Optional[List[str]] = None,
        selectable: bool = False,
        row_key: Optional[str] = None,
        page_size: int = 10,
        page_size_options: List[int] = None,
        row_height: int = 48,
        border_width: int = 1,
        border_radius: int = 12,
        border_color: Optional[str] = None,
        show_actions: bool = False,
        actions: Optional[List[Dict[str, Any]]] = None,
        role: str = "card",
        parent=None,
        **kwargs
    ):
        super().__init__(
            parent=parent,
            layout="v",
            margins=(18, 16, 18, 16),
            spacing=14,
            role=role,
            border_width=border_width,
            radius=border_radius,
            border_color=border_color,
            **kwargs
        )
        
        self.columns_config = columns or []
        self._raw_data: List[Dict[str, Any]] = data or []
        self._filtered_data: List[Dict[str, Any]] = list(self._raw_data)
        
        # 配置属性
        self.title_text = title
        self.description_text = description
        self.searchable = searchable
        self.search_placeholder = search_placeholder
        self.search_columns = search_columns
        self.selectable = bool(selectable)
        self.row_key = row_key
        self.row_height = int(row_height)
        self.show_actions = bool(show_actions)
        self.actions = actions
        
        # 边框与外形参数
        self.border_width = int(border_width)
        self.border_radius = int(border_radius)
        self.custom_border_color = border_color
        
        # 多选复选框记忆状态
        self._selected_row_keys = set()
        self._selected_rows_map = {}
        
        # 分页属性
        self.page_size = page_size
        self.page_size_options = page_size_options or [10, 20, 50, 100]
        if self.page_size not in self.page_size_options:
            self.page_size_options = sorted(list(set(self.page_size_options + [self.page_size])))
        self.current_page = 1
        
        # 排序状态
        self._sort_key: Optional[str] = None
        self._sort_order: Optional[Qt.SortOrder] = None
        
        # 搜索过滤文本
        self._search_query: str = ""

        self._setup_ui()
        self.refresh_table()

        # 监听主题切换
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    # ─────────────────────────────────────────────────────────
    # UI 构建
    # ─────────────────────────────────────────────────────────

    def _setup_ui(self):
        # 1. 顶部工具栏 (Header & Search)
        has_title = bool(self.title_text)
        has_desc = bool(self.description_text)

        if has_title or has_desc or self.searchable:
            self.top_toolbar = QWidget(self)
            self.top_toolbar.setObjectName("ProTableTopToolbar")
            self.top_toolbar.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.top_toolbar.setStyleSheet("background: transparent;")
            top_layout = QVBoxLayout(self.top_toolbar)
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.setSpacing(12)

            if has_title or has_desc:
                title_container = QWidget(self.top_toolbar)
                title_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
                title_container.setStyleSheet("background: transparent;")
                title_layout = QVBoxLayout(title_container)
                title_layout.setContentsMargins(0, 0, 0, 0)
                title_layout.setSpacing(3)

                if has_title:
                    self.title_label = QLabel(self.title_text, title_container)
                    self.title_label.setObjectName("ProTableTitle")
                    self.title_label.setFont(QFont('"Segoe UI", "Microsoft YaHei"', 12, QFont.Weight.Bold))
                    title_layout.addWidget(self.title_label)

                if has_desc:
                    self.desc_label = QLabel(self.description_text, title_container)
                    self.desc_label.setObjectName("ProTableDesc")
                    self.desc_label.setFont(QFont('"Segoe UI", "Microsoft YaHei"', 9))
                    title_layout.addWidget(self.desc_label)

                top_layout.addWidget(title_container)

            if self.searchable:
                search_container = QWidget(self.top_toolbar)
                search_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
                search_container.setStyleSheet("background: transparent;")
                s_layout = QHBoxLayout(search_container)
                s_layout.setContentsMargins(0, 2, 0, 4)

                self.search_input = MkInput(
                    placeholder=self.search_placeholder,
                    leading_icon="magnifying-glass",
                    parent=search_container
                )
                self.search_input.setFixedHeight(36)
                self.search_input.setMaximumWidth(320)
                self.search_input.textChanged.connect(self._on_search_text_changed)
                s_layout.addWidget(self.search_input)
                s_layout.addStretch()

                top_layout.addWidget(search_container)

            self.add_widget(self.top_toolbar)

        # 2. 数据表格视口容器 (Table Container)
        self.table_container = QFrame(self)
        self.table_container.setObjectName("ProTableInnerContainer")
        self.table_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.table_container.setStyleSheet("background: transparent; border: none;")
        tc_layout = QVBoxLayout(self.table_container)
        tc_layout.setContentsMargins(0, 0, 0, 0)
        tc_layout.setSpacing(0)

        # 核心 QTableWidget (采用支持整行悬停高亮与自适应分隔线的 MkProTableWidget)
        self.table_widget = MkProTableWidget(self.table_container)
        self.table_widget.setObjectName("MkProTableWidget")
        self.table_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.table_widget.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.table_widget.viewport().setStyleSheet("background: transparent;")
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table_widget.setShowGrid(False)
        self.table_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setAlternatingRowColors(False)
        self.table_widget.cellClicked.connect(self._on_cell_clicked)

        # 自定义抗锯齿可排列表头
        self.header_view = MkProTableHeaderView(
            orientation=Qt.Orientation.Horizontal,
            radius=self.border_radius,
            border_width=self.border_width,
            parent=self.table_widget
        )
        self.header_view.sortRequested.connect(self._on_header_sort_requested)
        self.header_view.headerCheckboxClicked.connect(self._on_header_checkbox_clicked)
        self.table_widget.setHorizontalHeader(self.header_view)

        tc_layout.addWidget(self.table_widget)
        self.add_widget(self.table_container, stretch=1)

        # 3. 底部控制与分页栏 (Footer Toolbar)
        self.footer_toolbar = QWidget(self)
        self.footer_toolbar.setObjectName("ProTableFooter")
        self.footer_toolbar.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.footer_toolbar.setStyleSheet("background: transparent;")
        footer_layout = QHBoxLayout(self.footer_toolbar)
        footer_layout.setContentsMargins(0, 8, 0, 8)
        footer_layout.setSpacing(10)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # 左侧条数统计 (垂直居中对齐，参考图4)
        self.total_label = QLabel(self.footer_toolbar)
        self.total_label.setObjectName("ProTableTotalCount")
        self.total_label.setFont(QFont('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif', 9))
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        footer_layout.addWidget(self.total_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        # 每页行数选择器 (垂直居中对齐，参考图4)
        self.page_size_label = QLabel("每页", self.footer_toolbar)
        self.page_size_label.setFont(QFont('-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif', 9))
        self.page_size_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        footer_layout.addWidget(self.page_size_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.page_size_combo = MkPageSizeComboBox(self.footer_toolbar)
        for opt in self.page_size_options:
            self.page_size_combo.addItem(f"{opt} 条", opt)
        curr_idx = self.page_size_options.index(self.page_size) if self.page_size in self.page_size_options else 0
        self.page_size_combo.setCurrentIndex(curr_idx)
        self.page_size_combo.currentIndexChanged.connect(self._on_page_size_changed)
        footer_layout.addWidget(self.page_size_combo, alignment=Qt.AlignmentFlag.AlignVCenter)

        footer_layout.addStretch()

        # 右侧翻页导航按钮组
        self.right_pager = QWidget(self.footer_toolbar)
        self.pager_layout = QHBoxLayout(self.right_pager)
        self.pager_layout.setContentsMargins(0, 4, 0, 4)
        self.pager_layout.setSpacing(4)
        footer_layout.addWidget(self.right_pager, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.add_widget(self.footer_toolbar)

    # ─────────────────────────────────────────────────────────
    # 参数与数据更新
    # ─────────────────────────────────────────────────────────

    @property
    def effective_columns(self) -> List[Dict[str, Any]]:
        """计算当前生效的列配置（受 selectable 与 show_actions 控制）"""
        cols = []

        # 1. 若开启了 selectable，首列自动追加复选框列
        if self.selectable:
            cols.append({
                "key": "__selection__",
                "label": "",
                "type": "selection",
                "width": 48,
                "sortable": False,
                "align": "center"
            })

        has_action_col = False
        for c in self.columns_config:
            if c.get("type") == "selection" or c.get("key") == "__selection__":
                continue
            if c.get("type") == "action" or c.get("key") == "action":
                has_action_col = True
                if self.show_actions:
                    cols.append(c)
            else:
                cols.append(c)

        # 若开启了 show_actions 但未传入 action 列，则自动追加标准操作列
        if self.show_actions and not has_action_col:
            cols.append({
                "key": "action",
                "label": "操作",
                "type": "action",
                "width": 90,
                "sortable": False,
                "actions": self.actions or [
                    {"name": "edit", "icon": "pencil", "tooltip": "编辑"},
                    {"name": "delete", "icon": "trash", "tooltip": "删除"}
                ]
            })
        return cols

    def set_selectable(self, selectable: bool):
        """动态开启或关闭复选框多选列"""
        self.selectable = bool(selectable)
        self.refresh_table()

    def set_show_actions(self, show: bool):
        """动态显示或隐藏操作列"""
        self.show_actions = bool(show)
        self.refresh_table()

    def set_data(self, data: List[Dict[str, Any]]):
        """设置新的数据源并重新渲染"""
        self._raw_data = data or []
        self.current_page = 1
        self._apply_filter_and_sort()

    def set_columns(self, columns: List[Dict[str, Any]]):
        """更新列配置"""
        self.columns_config = columns or []
        self.refresh_table()

    def set_border_props(self, width: Optional[int] = None, radius: Optional[int] = None, color: Optional[str] = None):
        """动态调节边框粗细、圆角及颜色"""
        if width is not None:
            self.border_width = int(width)
        if radius is not None:
            self.border_radius = int(radius)
        if color is not None:
            self.custom_border_color = color
        self.set_theme_style()

    # ─────────────────────────────────────────────────────────
    # 复选框多选控制体系
    # ─────────────────────────────────────────────────────────

    def _get_row_id(self, row_dict: dict, abs_idx: int) -> Any:
        if self.row_key and self.row_key in row_dict:
            return row_dict[self.row_key]
        if "id" in row_dict:
            return row_dict["id"]
        return abs_idx

    def _on_header_checkbox_clicked(self, checked: bool):
        """表头全选 / 反选联动"""
        if checked:
            for idx, r in enumerate(self._filtered_data):
                rid = self._get_row_id(r, idx)
                self._selected_row_keys.add(rid)
                self._selected_rows_map[rid] = r
        else:
            for idx, r in enumerate(self._filtered_data):
                rid = self._get_row_id(r, idx)
                self._selected_row_keys.discard(rid)
                self._selected_rows_map.pop(rid, None)

        self.refresh_table()
        self.selectionChanged.emit(self.get_selected_rows())

    def _on_row_checkbox_toggled(self, row_id: Any, row_dict: dict, checked: bool):
        """单行复选框状态改变"""
        if checked:
            self._selected_row_keys.add(row_id)
            self._selected_rows_map[row_id] = row_dict
        else:
            self._selected_row_keys.discard(row_id)
            self._selected_rows_map.pop(row_id, None)

        # 检查是否全部已选
        all_selected = len(self._filtered_data) > 0 and all(
            self._get_row_id(r, i) in self._selected_row_keys for i, r in enumerate(self._filtered_data)
        )
        self.header_view.set_header_checked(all_selected)
        self.selectionChanged.emit(self.get_selected_rows())

    def get_selected_rows(self) -> List[Dict[str, Any]]:
        """获取当前已选中的所有行原始数据字典列表"""
        return list(self._selected_rows_map.values())

    def get_selected_keys(self) -> List[Any]:
        """获取当前已选中的唯一标识键集合"""
        return list(self._selected_row_keys)

    def clear_selection(self):
        """清空所有选中行状态"""
        self._selected_row_keys.clear()
        self._selected_rows_map.clear()
        self.header_view.set_header_checked(False)
        self.refresh_table()
        self.selectionChanged.emit([])

    def select_all(self):
        """全选当前过滤结果集的所有行数据"""
        for idx, r in enumerate(self._filtered_data):
            rid = self._get_row_id(r, idx)
            self._selected_row_keys.add(rid)
            self._selected_rows_map[rid] = r
        self.header_view.set_header_checked(True)
        self.refresh_table()
        self.selectionChanged.emit(self.get_selected_rows())

    # ─────────────────────────────────────────────────────────
    # 搜索与排序内核 (Reactive Pipeline)
    # ─────────────────────────────────────────────────────────

    def _on_search_text_changed(self, text: str):
        self._search_query = text.strip().lower()
        self.current_page = 1
        self._apply_filter_and_sort()

    def _on_header_sort_requested(self, logical_index: int):
        cols = self.effective_columns
        if not (0 <= logical_index < len(cols)):
            return
        col = cols[logical_index]
        key = col.get("key")
        if not key or not col.get("sortable", True) or col.get("type") == "selection":
            return

        if self._sort_key != key:
            self._sort_key = key
            self._sort_order = Qt.SortOrder.AscendingOrder
        elif self._sort_order == Qt.SortOrder.AscendingOrder:
            self._sort_order = Qt.SortOrder.DescendingOrder
        elif self._sort_order == Qt.SortOrder.DescendingOrder:
            self._sort_key = None
            self._sort_order = None

        self._apply_filter_and_sort()

    def _apply_filter_and_sort(self):
        data = list(self._raw_data)

        if self._search_query:
            filtered = []
            cols_to_search = self.search_columns or [c.get("key") for c in self.columns_config if c.get("key")]
            for item in data:
                matched = False
                for col_key in cols_to_search:
                    val = item.get(col_key, "")
                    if val is not None and self._search_query in str(val).lower():
                        matched = True
                        break
                if matched:
                    filtered.append(item)
            data = filtered

        if self._sort_key and self._sort_order is not None:
            reverse = (self._sort_order == Qt.SortOrder.DescendingOrder)

            def sort_val(item):
                v = item.get(self._sort_key, "")
                if v is None:
                    return ""
                try:
                    return float(v)
                except (ValueError, TypeError):
                    return str(v).lower()

            try:
                data.sort(key=sort_val, reverse=reverse)
            except Exception:
                pass

        self._filtered_data = data

        cols = self.effective_columns
        active_col_idx = None
        if self._sort_key:
            for idx, c in enumerate(cols):
                if c.get("key") == self._sort_key:
                    active_col_idx = idx
                    break
        self.header_view.set_sort_state(active_col_idx, self._sort_order)
        self.refresh_table()

    # ─────────────────────────────────────────────────────────
    # 视口与数据渲染
    # ─────────────────────────────────────────────────────────

    def _on_page_size_changed(self, index: int):
        data = self.page_size_combo.currentData()
        if data is not None:
            self.page_size = int(data)
            self.current_page = 1
            self.refresh_table()

    def refresh_table(self):
        total_items = len(self._filtered_data)
        total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        self.current_page = min(max(1, self.current_page), total_pages)

        # 计算切片
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total_items)
        page_data = self._filtered_data[start_idx:end_idx]

        # 清理旧单元格控件
        for r in range(self.table_widget.rowCount()):
            for c in range(self.table_widget.columnCount()):
                w = self.table_widget.cellWidget(r, c)
                if w is not None:
                    self.table_widget.removeCellWidget(r, c)
                    w.setParent(None)
                    w.deleteLater()
        self.table_widget.clearContents()

        # 配置表格行列
        effective_cols = self.effective_columns
        col_count = len(effective_cols)
        self.table_widget.setColumnCount(col_count)
        self.table_widget.setRowCount(len(page_data))

        # 表头标签与排序列状态
        headers = [col.get("label", "") for col in effective_cols]
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.header_view.set_has_checkbox(self.selectable)

        # 检查当前页/总集全选状态
        all_selected = total_items > 0 and all(
            self._get_row_id(r, i) in self._selected_row_keys for i, r in enumerate(self._filtered_data)
        )
        self.header_view.set_header_checked(all_selected)

        for col_idx, col in enumerate(effective_cols):
            sortable = col.get("sortable", True)
            self.header_view.set_sortable(col_idx, sortable)

            align_str = col.get("align", "left").lower()
            if align_str == "center":
                align_flag = Qt.AlignmentFlag.AlignCenter
            elif align_str == "right":
                align_flag = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            else:
                align_flag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

            self.header_view.set_column_alignment(col_idx, align_flag)

            w = col.get("width")
            if w:
                self.header_view.setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Interactive)
                self.table_widget.setColumnWidth(col_idx, w)
            else:
                self.header_view.setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Stretch)

        # 填充单元格
        for row_idx, row_dict in enumerate(page_data):
            self.table_widget.setRowHeight(row_idx, self.row_height)
            abs_idx = start_idx + row_idx
            row_id = self._get_row_id(row_dict, abs_idx)

            for col_idx, col in enumerate(effective_cols):
                key = col.get("key")
                col_type = col.get("type", "text")
                raw_val = row_dict.get(key, "")

                align_str = col.get("align", "left").lower()
                if align_str == "center":
                    align_flag = Qt.AlignmentFlag.AlignCenter
                elif align_str == "right":
                    align_flag = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                else:
                    align_flag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

                if col_type == "selection":
                    # 复选框单元格
                    cell_chk = QWidget(self.table_widget)
                    chk_lay = QHBoxLayout(cell_chk)
                    chk_lay.setContentsMargins(0, 0, 0, 0)
                    chk_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    chk = MkCheckBox(parent=cell_chk)
                    chk.setFixedSize(18, 18)
                    chk.setChecked(row_id in self._selected_row_keys)
                    chk.toggled.connect(lambda checked, rid=row_id, rd=row_dict: self._on_row_checkbox_toggled(rid, rd, checked))
                    chk_lay.addWidget(chk)
                    self.table_widget.setCellWidget(row_idx, col_idx, cell_chk)
                    self.table_widget.bind_cell_widget(cell_chk, row_idx)

                elif col_type == "avatar_text":
                    avatar_val = row_dict.get(col.get("avatar_key", "avatar"), None)
                    color_val = row_dict.get(col.get("color_key", "color"), None)
                    cell_widget = MkAvatarTextCell(str(raw_val), avatar=avatar_val, color=color_val, align=align_flag, parent=self.table_widget)
                    cell_widget.clicked.connect(lambda t, a=abs_idx, r=row_dict: self.rowClicked.emit(a, r))
                    self.table_widget.setCellWidget(row_idx, col_idx, cell_widget)
                    self.table_widget.bind_cell_widget(cell_widget, row_idx)

                elif col_type == "image":
                    # 图片缩略图单元格
                    cell_widget = MkImageCellWidget(str(raw_val), parent=self.table_widget)
                    cell_widget.clicked.connect(lambda p: self._show_image_lightbox(p))
                    wrapper = QWidget(self.table_widget)
                    w_lay = QHBoxLayout(wrapper)
                    w_lay.setContentsMargins(14, 0, 14, 0)
                    w_lay.setAlignment(align_flag)
                    w_lay.addWidget(cell_widget)
                    self.table_widget.setCellWidget(row_idx, col_idx, wrapper)
                    self.table_widget.bind_cell_widget(wrapper, row_idx)

                elif col_type == "video":
                    # 视频缩略图单元格
                    thumb_val = row_dict.get(col.get("thumbnail_key", "thumbnail"), None)
                    cell_widget = MkVideoCellWidget(str(raw_val), thumbnail_path=thumb_val, parent=self.table_widget)
                    cell_widget.clicked.connect(lambda p: self._show_video_player(p))
                    wrapper = QWidget(self.table_widget)
                    w_lay = QHBoxLayout(wrapper)
                    w_lay.setContentsMargins(14, 0, 14, 0)
                    w_lay.setAlignment(align_flag)
                    w_lay.addWidget(cell_widget)
                    self.table_widget.setCellWidget(row_idx, col_idx, wrapper)
                    self.table_widget.bind_cell_widget(wrapper, row_idx)

                elif col_type == "badge":
                    icon_val = col.get("icon", None)
                    cell_widget = MkBadgeCell(str(raw_val), icon=icon_val, align=align_flag, parent=self.table_widget)
                    self.table_widget.setCellWidget(row_idx, col_idx, cell_widget)
                    self.table_widget.bind_cell_widget(cell_widget, row_idx)

                elif col_type == "status":
                    cell_widget = MkStatusCell(str(raw_val), align=align_flag, parent=self.table_widget)
                    self.table_widget.setCellWidget(row_idx, col_idx, cell_widget)
                    self.table_widget.bind_cell_widget(cell_widget, row_idx)

                elif col_type == "action":
                    action_widget = self._create_action_cell(abs_idx, row_dict, col.get("actions"), align=align_flag)
                    self.table_widget.setCellWidget(row_idx, col_idx, action_widget)
                    self.table_widget.bind_cell_widget(action_widget, row_idx)

                else:
                    # 纯文本单元格采用支持划词选择复制的 MkTextCell
                    cell_widget = MkTextCell(str(raw_val), align=align_flag, parent=self.table_widget)
                    self.table_widget.setCellWidget(row_idx, col_idx, cell_widget)
                    self.table_widget.bind_cell_widget(cell_widget, row_idx)

        # 更新底部信息
        sel_count = len(self._selected_row_keys)
        sel_suffix = f" (已选 {sel_count} 项)" if self.selectable and sel_count > 0 else ""
        self.total_label.setText(f"共 {total_items} 条{sel_suffix}")
        self._update_pagination_buttons(total_pages)

    def _create_action_cell(self, abs_row_idx: int, row_dict: dict, actions: Optional[List[dict]] = None, align: Qt.AlignmentFlag = None) -> QWidget:
        container = QWidget(self.table_widget)
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(14, 0, 14, 0)
        h_layout.setSpacing(6)
        h_layout.setAlignment(align or (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))

        act_list = actions or [
            {"name": "edit", "icon": "pencil", "tooltip": "编辑"},
            {"name": "delete", "icon": "trash", "tooltip": "删除"}
        ]

        t = ThemeEngine
        is_dark = t.is_dark()
        fg_color = "#94A3B8" if is_dark else "#64748B"
        hover_bg = "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(0, 0, 0, 0.06)"

        for act in act_list:
            act_name = act.get("name", "action")
            icon_name = act.get("icon", "dots-three")
            btn = QPushButton(container)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(28, 28)
            btn.setIcon(MkPhosphorIcon.get_icon(icon_name, fg_color, 16))
            btn.setIconSize(QSize(16, 16))
            btn.setToolTip(act.get("tooltip", act_name))

            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                }}
            """)

            btn.clicked.connect(lambda checked=False, a=act_name, idx=abs_row_idx, row=row_dict: self.actionTriggered.emit(a, idx, row))
            h_layout.addWidget(btn)

        return container

    def _show_image_lightbox(self, img_path: str):
        if not img_path:
            return
        from .preview_dialogs import MkLightboxDialog
        dialog = MkLightboxDialog(img_path, self.window())
        dialog.exec()

    def _show_video_player(self, video_path: str):
        if not video_path:
            return
        from .preview_dialogs import MkVideoPlayerDialog
        dialog = MkVideoPlayerDialog(video_path, self.window())
        dialog.exec()

    def _update_pagination_buttons(self, total_pages: int):
        while self.pager_layout.count():
            child = self.pager_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 上一页按钮
        prev_btn = QPushButton("‹ 上一页", self.right_pager)
        prev_btn.setEnabled(self.current_page > 1)
        prev_btn.setCursor(Qt.CursorShape.PointingHandCursor if self.current_page > 1 else Qt.CursorShape.ArrowCursor)
        prev_btn.clicked.connect(lambda: self._go_page(self.current_page - 1))
        self.pager_layout.addWidget(prev_btn)

        # 紧凑页码算法 (1 2 3 ... 10)
        pages_to_show = []
        if total_pages <= 5:
            pages_to_show = list(range(1, total_pages + 1))
        else:
            if self.current_page <= 3:
                pages_to_show = [1, 2, 3, 4, "...", total_pages]
            elif self.current_page >= total_pages - 2:
                pages_to_show = [1, "...", total_pages - 3, total_pages - 2, total_pages - 1, total_pages]
            else:
                pages_to_show = [1, "...", self.current_page - 1, self.current_page, self.current_page + 1, "...", total_pages]

        for p in pages_to_show:
            if p == "...":
                ellipsis_lbl = QLabel("...", self.right_pager)
                ellipsis_lbl.setFixedWidth(24)
                ellipsis_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.pager_layout.addWidget(ellipsis_lbl)
            else:
                btn = QPushButton(str(p), self.right_pager)
                btn.setFixedSize(30, 30)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                is_active = (p == self.current_page)
                if is_active:
                    btn.setObjectName("ActivePageBtn")
                else:
                    btn.clicked.connect(lambda checked=False, target=p: self._go_page(target))
                self.pager_layout.addWidget(btn)

        # 下一页按钮
        next_btn = QPushButton("下一页 ›", self.right_pager)
        next_btn.setEnabled(self.current_page < total_pages)
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor if self.current_page < total_pages else Qt.CursorShape.ArrowCursor)
        next_btn.clicked.connect(lambda: self._go_page(self.current_page + 1))
        self.pager_layout.addWidget(next_btn)

    def _go_page(self, page_num: int):
        self.current_page = page_num
        self.refresh_table()

    def _on_cell_clicked(self, row: int, column: int):
        self.table_widget.set_active_row(row)
        start_idx = (self.current_page - 1) * self.page_size
        abs_idx = start_idx + row
        if 0 <= abs_idx < len(self._filtered_data):
            self.rowClicked.emit(abs_idx, self._filtered_data[abs_idx])

    # ─────────────────────────────────────────────────────────
    # 68 种主题风格自适应 (Theme Engine Integration)
    # ─────────────────────────────────────────────────────────

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        primary = t.get("--primary", "#0284C7")
        fg = t.get("--glass-text", t.get("--fg", "#0F172A")) if t.is_glass() else t.get("--fg", "#0F172A")
        muted = t.get("--text-muted", "#64748B")
        border = self.custom_border_color or (t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0"))
        surface = t.get("--glass-surface", t.get("--surface", "#FFFFFF")) if t.is_glass() else t.get("--surface", "#FFFFFF")
        surface_muted = t.get("--surface-muted", "#F8FAFC")
        
        radius_val = 0 if t.is_brutal() or t.is_pixel() else self.border_radius
        b_width = self.border_width
        grid_rule = "#000000" if t.is_brutal() or t.is_pixel() else border
        active_fg = readable_text(primary)

        # 计算整行悬停背景与底部分隔线颜色 (全量适配 68 种主题风格，参考图2、3沉浸暗黑与图4/5标准)
        is_dark = t.is_dark()
        if t.is_glow():
            hover_color = QColor(255, 255, 255, 22)
            grid_rule = "#1F293D"
        elif t.is_glass():
            hover_color = QColor(255, 255, 255, 20 if not is_dark else 14)
            grid_rule = border
        elif t.is_brutal() or t.is_pixel():
            hover_color = QColor("#F1F5F9" if not is_dark else "#262626")
            grid_rule = "#000000"
        elif is_dark:
            # 暗黑/OLED 风格下采用纯粹中性微透白高亮，在深灰/深黑底色上呈现高雅纯净的深炭灰（完全无偏蓝，参考图2、图3）
            hover_color = QColor(255, 255, 255, 18)
            grid_rule = "rgba(255, 255, 255, 0.08)"
        else:
            hover_color = QColor(0, 0, 0, 10) if surface_muted == surface else QColor(surface_muted)
            grid_rule = border

        hover_hex = hover_color.name(QColor.NameFormat.HexArgb) if hover_color.alpha() < 255 else hover_color.name()

        self.table_widget.set_hover_color(hover_color)
        self.table_widget.set_divider_color(QColor(grid_rule))

        if hasattr(self, "page_size_combo") and self.page_size_combo is not None:
            self.page_size_combo.update_theme_style()

        # 1. 更新表头色值
        self.header_view.set_theme_props(
            radius=float(radius_val),
            border_width=b_width,
            bg_color="transparent",
            border_color=grid_rule,
            fg_color=muted
        )

        # 2. 更新表格与表头 QSS (仅整行由 paintEvent 统一悬停高亮，单个单元格不应用任何悬停或选中样式)
        self.table_widget.setStyleSheet(f"""
            QTableWidget#MkProTableWidget,
            QTableWidget {{
                background-color: transparent;
                border: none;
                gridline-color: transparent;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
                font-size: 13px;
                color: {fg};
                outline: none;
                selection-background-color: transparent;
                selection-color: {fg};
            }}
            QTableWidget#MkProTableWidget QLabel,
            QTableWidget QLabel {{
                color: {fg};
                background: transparent;
                border: none;
            }}
            QTableWidget#MkProTableWidget::item,
            QTableWidget::item {{
                border: none;
                border-bottom: none;
                padding: 6px 14px;
                background: transparent;
                background-color: transparent;
                outline: none;
            }}
            QTableWidget#MkProTableWidget::item:hover,
            QTableWidget::item:hover {{
                background: transparent;
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QTableWidget#MkProTableWidget::item:selected,
            QTableWidget::item:selected,
            QTableWidget#MkProTableWidget::item:selected:active,
            QTableWidget::item:selected:active,
            QTableWidget#MkProTableWidget::item:selected:!active,
            QTableWidget::item:selected:!active {{
                background: transparent;
                background-color: transparent;
                color: {fg};
                border: none;
                outline: none;
            }}
            QTableWidget#MkProTableWidget::item:focus,
            QTableWidget::item:focus {{
                outline: none;
                border: none;
                background: transparent;
                background-color: transparent;
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
                font-weight: 600;
                font-size: 13px;
                border: none;
                padding: 8px 14px;
                text-align: left;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {t.get("--scrollbar-thumb", "#CBD5E1")};
                min-height: 24px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t.get("--scrollbar-thumb-hover", "#94A3B8")};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        # 3. 更新标题栏与统计信息文字颜色
        if hasattr(self, "title_label"):
            self.title_label.setStyleSheet(f"color: {fg}; background: transparent; border: none;")
        if hasattr(self, "desc_label"):
            self.desc_label.setStyleSheet(f"color: {muted}; background: transparent; border: none;")
        self.total_label.setStyleSheet(f"color: {muted}; background: transparent; border: none;")
        self.page_size_label.setStyleSheet(f"color: {muted}; background: transparent; border: none;")

        # 4. 更新翻页按钮组 QSS (严格对齐现代设计规范，参考图2)
        btn_radius = 0 if t.is_brutal() or t.is_pixel() else 6
        if t.is_brutal():
            page_fg = "#000000" if not is_dark else "#FFFFFF"
            disabled_fg = "#9CA3AF" if not is_dark else "#52525B"
            hover_bg = "#E2E8F0" if not is_dark else "#262626"
            active_bg = "#FFDE59" if not is_dark else primary
            active_fg = "#000000" if not is_dark else readable_text(primary)
            active_bd = "2px solid #000000"
        elif t.is_glow():
            page_fg = fg
            disabled_fg = "#52525B" if is_dark else "#9CA3AF"
            hover_bg = "rgba(255, 255, 255, 0.10)"
            active_bg = primary
            active_fg = readable_text(primary)
            active_bd = f"1px solid {primary}"
        elif is_dark:
            # 暗黑 / OLED 模式：纯中性深灰，彻底消除蓝紫色偏，无生硬外边框（严格参考图2）
            page_fg = "#F4F4F5"
            disabled_fg = "#52525B"  # 纯正中性暗灰 (Zinc-600)，彻底消除偏蓝
            hover_bg = "rgba(255, 255, 255, 0.08)"
            active_bg = "#27272A"  # 悬浮深灰胶囊卡片（参考图2中的高质感选中状态）
            active_fg = "#FFFFFF"
            active_bd = "1px solid rgba(255, 255, 255, 0.12)"
        else:
            # 亮色模式
            page_fg = "#0F172A"
            disabled_fg = "#A1A1AA"  # 纯正中性浅灰 (Zinc-400)，彻底消除偏蓝
            hover_bg = "rgba(0, 0, 0, 0.05)"
            active_bg = "#0F172A"
            active_fg = "#FFFFFF"
            active_bd = "1px solid #0F172A"

        self.right_pager.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: {btn_radius}px;
                color: {page_fg};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
                font-size: 13px;
                font-weight: 500;
                padding: 4px 10px;
                min-height: 24px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                border: 1px solid transparent;
                color: {page_fg};
            }}
            QPushButton:disabled {{
                color: {disabled_fg};
                border: 1px solid transparent;
                background-color: transparent;
            }}
            QPushButton#ActivePageBtn {{
                background-color: {active_bg};
                color: {active_fg};
                border: {active_bd};
                font-weight: 600;
            }}
            QPushButton#ActivePageBtn:hover {{
                background-color: {active_bg};
                color: {active_fg};
            }}
            QLabel {{
                color: {disabled_fg};
                font-size: 13px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)

        if hasattr(self, "page_size_combo"):
            self.page_size_combo.update_theme_style()
