# -*- coding: utf-8 -*-
"""
MkChartGroup & MkChartDashboard - 现代化卡片分组图表管理器与监控看板 (MonkeyQt Data)

核心特性:
  1. 【卡片分组管理 (Group Management)】:
     - 支持将大量监控指标/图表 (如 Metrics, Loss, Learning Rate 等) 分组收纳进独立折叠卡片；
     - 卡片头部展示折叠箭头 (Chevron)、分组标题 (Title) 与实时数量角标 (如 (6/8), (5/5))；
  2. 【对标 Ultralytics HUB 交互体验】:
     - 悬停特效 (Hover Capsule): 鼠标移入右上角更多按钮 [···] 时激活胶囊轮廓与高亮背景，移出恢复极简幽灵形态；
     - 菜单打开期间按钮持续保持激活状态；
     - 图表可见性下拉清单 (Chart Visibility Menu):
       * 每一项带有右侧对齐的高清矢量对勾 (Checkmark)，点击切换单图显隐；
       * 勾选操作菜单保持常驻 (Keep Open)，无需反复点开；
       * 底部快捷动作 [Show All] (显示全部) 与 [Hide All] (隐藏全部)；
       * 可选的 Series 全局系列切换 (如 Train solid / Val dashed)；
  3. 【自适应响应式网格 (Responsive Grid)】:
     - 默认 3 列排布 (可自定义 1~6 列)，显隐切换时无缝重排重聚；
     - 滚轮穿透保护: 智能转发鼠标滚轮事件到父级 QScrollArea，杜绝图表卡片滚动阻尼；
  4. 【双向兼容与极简数据注入】:
     - 独立兼容: 用户亦可完全脱离卡片直接使用 MkLineChart 单图；
     - 灵活装载: 支持 add_chart() 自动创建或 add_chart_widget() 接入任意外部组件；
     - 便捷数据驱动: 提供 set_series_data()、append_point() 及 update_metrics() 一键更新。
  5. 【68 种主题深度自适应】:
     - 继承 MkQWidget(role="card")，全自动响应深色、浅色、OLED、毛玻璃等所有 MonkeyQt 主题规范。
"""
from __future__ import annotations

from typing import Dict, List, Optional, Any, Sequence, Union

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QFrame, QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QRectF
from PySide6.QtGui import (
    QFont, QCursor, QColor, QPainter, QPixmap, QPen, QAction,
    QGuiApplication
)

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import parse_px, qcolor, readable_text
from monkeyqt_icons import (
    Ph, PhCaretDown, PhCaretRight, PhDotsThree, PhEye, PhEyeSlash
)
from monkeyqt.components.layout.widget import MkQWidget
from monkeyqt.components.navigation.dropdown import MkDropdown
from monkeyqt.components.feedback.skeleton import MkSkeleton, MkSkeletonBlock
from monkeyqt.components.data.line_chart import MkLineChart, MkSeries


class _GroupMoreButton(MkDropdown):
    """
    分组卡片右上角更多选项按钮 (···)
    对标 Ultralytics HUB 胶囊悬停交互 (Image 2 & Image 3):
    - 未悬浮时: 纯幽灵透明形态，仅展示灰度三点；
    - 悬浮或菜单打开时: 自动绘制 1px 边框与微光底色，圆角 6px；
    - 下拉菜单对齐右边缘 (bottom-end)。
    """
    def __init__(self, parent=None):
        super().__init__(
            text="",
            parent=parent,
            trigger="more",
            variant="ghost",
            placement="bottom-end",
            size="small",
            icon_size=18,
            radius=6,
            min_menu_width=180,
            show_arrow=False,
        )
        self.setFixedSize(32, 26)
        self.setToolTip("图表可见性与选项")

    def paintEvent(self, event):
        c = self._colors
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        force_hover = getattr(self, "_force_hover", False)
        hover = self.underMouse() or self.menu.isVisible() or force_hover

        if hover:
            painter.setBrush(c.get("surface", QColor(255, 255, 255)))
            painter.setPen(QPen(c.get("border", QColor(226, 232, 240)), 1))
            painter.drawRoundedRect(rect, self._radius, self._radius)
            icon_color = c.get("fg", QColor(15, 23, 42))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(Qt.PenStyle.NoPen)
            icon_color = c.get("muted", QColor(100, 116, 139))

        icon_size = 18
        ix = int((self.width() - icon_size) / 2)
        iy = int((self.height() - icon_size) / 2)
        pix = Ph.pixmap(
            name="dots-three",
            size=icon_size,
            weight="bold",
            color=icon_color.name(),
            dpr=self.devicePixelRatioF()
        )
        painter.drawPixmap(ix, iy, pix)


class MkChartGroup(MkQWidget):
    """
    折叠式图表分组卡片组件 (Collapsible Chart Group Card)

    参数:
      title: 分组标题 (如 "Metrics", "Loss", "Learning Rate")
      parent: 父级窗口或容器
      columns: 网格列数 (默认 3 列)
      is_expanded: 初始是否展开 (默认 True)
      enable_series_toggle: 是否开启全局系列筛选 (如 Loss 的 Train/Val)
      series_options: 系列筛选名称列表 (默认 ["Train (solid)", "Val (dashed)"])
      chart_min_height: 单图表最小高度 (默认 240px)
    """
    visibilityChanged = Signal(str, bool)   # chart_id, is_visible
    seriesToggled = Signal(str, bool)       # series_name, is_visible
    expandedChanged = Signal(bool)          # is_expanded

    def __init__(
        self,
        title: str,
        parent: Optional[QWidget] = None,
        *,
        columns: int = 3,
        is_expanded: bool = True,
        enable_series_toggle: bool = False,
        series_options: Optional[List[str]] = None,
        chart_min_height: int = 240,
        loading: bool = False,
        skeleton_count: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            parent=parent,
            layout="v",
            role="card",
            radius=12,
            border=True,
            margins=(16, 12, 16, 14),
            spacing=10,
            **kwargs
        )
        self.title_text = str(title)
        self.columns = max(1, int(columns))
        self._is_expanded = bool(is_expanded)
        self._is_loading = bool(loading)
        self._skeleton_count = skeleton_count
        self.enable_series_toggle = bool(enable_series_toggle)
        self.series_options = list(series_options) if series_options is not None else (
            ["Train (solid)", "Val (dashed)"] if enable_series_toggle else []
        )
        self.chart_min_height = max(160, int(chart_min_height))

        # 内部数据结构
        self._charts_order: List[str] = []
        self._charts_widgets: Dict[str, QWidget] = {}
        self._charts_titles: Dict[str, str] = {}
        self._charts_visibility: Dict[str, bool] = {}
        self._series_visibility: Dict[str, bool] = {s: True for s in self.series_options}

        self._setup_group_ui()
        self._update_theme_style()
        ThemeEngine.instance().themeChanged.connect(self._update_theme_style)

    def wheelEvent(self, event):
        """滚轮事件直接由 Qt 冒泡至外层 QScrollArea，避免自定义 dispatch 产生卡顿"""
        event.ignore()

    def _setup_group_ui(self):
        # ── 1. Header 栏 ──
        self.header_frame = QFrame(self)
        self.header_frame.setObjectName("MkChartGroupHeader")

        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # 仅左侧标题与折叠箭头区域响应点击折叠 (对标图一红框，避免点击空白区域误折叠)
        self.toggle_container = QWidget(self.header_frame)
        self.toggle_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_container.mousePressEvent = lambda e: self.toggle_expanded()

        toggle_layout = QHBoxLayout(self.toggle_container)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(8)

        # 展开/折叠箭头指示图标
        self.lbl_chevron = QLabel(self.toggle_container)
        self.lbl_chevron.setFixedSize(16, 16)
        self.lbl_chevron.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toggle_layout.addWidget(self.lbl_chevron)

        # 分组标题
        self.lbl_title = QLabel(self.title_text, self.toggle_container)
        font = self.lbl_title.font()
        font.setPixelSize(14)
        font.setBold(True)
        self.lbl_title.setFont(font)
        toggle_layout.addWidget(self.lbl_title)

        # 数量角标 (visible/total)
        self.lbl_badge = QLabel("(0/0)", self.toggle_container)
        badge_font = self.lbl_badge.font()
        badge_font.setPixelSize(12)
        badge_font.setBold(True)
        self.lbl_badge.setFont(badge_font)
        toggle_layout.addWidget(self.lbl_badge)

        header_layout.addWidget(self.toggle_container)
        header_layout.addStretch()

        # 右侧操作更多按钮 (···)
        self.btn_more = _GroupMoreButton(self.header_frame)
        self.btn_more.aboutToShow.connect(self._rebuild_more_menu)
        header_layout.addWidget(self.btn_more)

        self.layout().addWidget(self.header_frame)

        # ── 2. Content 容器 ──
        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("MkChartGroupContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 4, 0, 0)
        self.content_layout.setSpacing(0)

        # 正常图表卡片网格容器
        self.cards_container = QWidget(self.content_widget)
        self.grid_layout = QGridLayout(self.cards_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(14)
        self.grid_layout.setVerticalSpacing(14)
        self.content_layout.addWidget(self.cards_container)

        # 骨架屏占位网格容器 (对标 Ultralytics 图三)
        self.skeleton_container = QWidget(self.content_widget)
        self.skeleton_grid_layout = QGridLayout(self.skeleton_container)
        self.skeleton_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.skeleton_grid_layout.setHorizontalSpacing(14)
        self.skeleton_grid_layout.setVerticalSpacing(14)
        self.skeleton_container.setVisible(False)
        self.content_layout.addWidget(self.skeleton_container)

        self.layout().addWidget(self.content_widget)

        self.set_expanded(self._is_expanded)
        self._update_chevron()
        self._rebuild_more_menu()
        if self._is_loading:
            self.set_loading(True)

    def set_loading(self, loading: bool, skeleton_count: Optional[int] = None):
        """设置分组卡片的骨架屏加载状态 (对标 Ultralytics 图三)"""
        self._is_loading = bool(loading)
        if skeleton_count is not None:
            self._skeleton_count = max(1, int(skeleton_count))
        if self._is_loading:
            self._render_skeleton()
            self.cards_container.setVisible(False)
            self.skeleton_container.setVisible(True)
        else:
            self.skeleton_container.setVisible(False)
            self.cards_container.setVisible(True)

    @property
    def is_loading(self) -> bool:
        return self._is_loading

    def _render_skeleton(self):
        while self.skeleton_grid_layout.count():
            item = self.skeleton_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        count = self._skeleton_count or (len(self._charts_order) if self._charts_order else self.columns)
        count = max(1, min(12, count))
        min_h = self.chart_min_height

        for i in range(count):
            row = i // self.columns
            col = i % self.columns
            card = MkQWidget(role="card", radius=12, border=True, parent=self.skeleton_container)
            card.setMinimumHeight(min_h)
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(16, 14, 16, 14)
            c_layout.setSpacing(12)

            blocks = [
                MkSkeletonBlock(x=0.32, y=6, width=0.36, height=16, radius=4),
                MkSkeletonBlock(x=0.04, y=36, width=0.92, height=max(60, min_h - 68), radius=8),
            ]
            skel = MkSkeleton(blocks=blocks, animated=True, parent=card)
            c_layout.addWidget(skel)
            self.skeleton_grid_layout.addWidget(card, row, col)

    def toggle_expanded(self):
        self.set_expanded(not self._is_expanded)

    def set_expanded(self, expanded: bool):
        was = self._is_expanded
        self._is_expanded = bool(expanded)
        self.content_widget.setVisible(self._is_expanded)
        self._update_chevron()
        if was != self._is_expanded:
            self.expandedChanged.emit(self._is_expanded)

    @property
    def is_expanded(self):
        class _CallableBool(int):
            def __bool__(self):
                return bool(int(self))
            def __call__(self):
                return bool(int(self))
        return _CallableBool(1 if self._is_expanded else 0)

    @is_expanded.setter
    def is_expanded(self, val: bool):
        self.set_expanded(val)

    def _update_chevron(self):
        is_dark = ThemeEngine.is_dark()
        icon_color = ThemeEngine.get("--text-muted", "#71717A" if is_dark else "#64748B")
        dpr = self.devicePixelRatioF()
        icon_name = "caret-down" if self._is_expanded else "caret-right"
        pix = Ph.pixmap(name=icon_name, size=14, weight="bold", color=icon_color, dpr=dpr)
        self.lbl_chevron.setPixmap(pix)

    def _update_badge(self):
        total = len(self._charts_order)
        visible = sum(1 for cid in self._charts_order if self._charts_visibility.get(cid, True))
        self.lbl_badge.setText(f"({visible}/{total})")

    def _update_theme_style(self):
        is_dark = ThemeEngine.is_dark()
        fg = ThemeEngine.get("--fg", "#F4F4F5" if is_dark else "#0F172A")
        text_muted = ThemeEngine.get("--text-muted", "#71717A" if is_dark else "#64748B")

        self.lbl_title.setStyleSheet(f"color: {fg}; background: transparent;")
        self.lbl_badge.setStyleSheet(f"color: {text_muted}; background: transparent;")
        self._update_chevron()
        if hasattr(self, "btn_more"):
            self.btn_more.update_theme_style()

    def set_theme(self, is_dark: bool = False):
        """向后兼容接口：刷新分组卡片主题样式"""
        self._update_theme_style()

    # ── 图表管理 API ──

    def add_chart(
        self,
        chart_id: str,
        title: Optional[str] = None,
        *,
        default_visible: bool = True,
        smooth: bool = True,
        area: bool = True,
        x_label: str = "",
        y_label: str = "",
        show_legend: bool = True,
        chart_min_height: Optional[int] = None,
        **chart_kwargs
    ) -> MkLineChart:
        """
        向分组卡片中添加一个全新的 MkLineChart 图表。
        返回创建的 MkLineChart 实例，方便链式配置。
        """
        cid = str(chart_id)
        display_title = str(title if title is not None else cid)

        chart = MkLineChart(
            title=display_title,
            smooth=smooth,
            area=area,
            x_label=x_label,
            y_label=y_label,
            show_legend=show_legend,
            parent=self.cards_container,
            **chart_kwargs
        )
        min_h = chart_min_height if chart_min_height is not None else self.chart_min_height
        chart.setMinimumHeight(min_h)
        self.add_chart_widget(cid, chart, title=display_title, default_visible=default_visible)
        return chart

    def add_chart_widget(
        self,
        chart_id: str,
        chart_widget: QWidget,
        title: Optional[str] = None,
        default_visible: bool = True,
    ):
        """
        向分组卡片中直接注入一个外部已创建的图表组件 (兼容自定义图表或已有 MkLineChart 实例)。
        """
        cid = str(chart_id)
        display_title = str(title if title is not None else cid)

        if cid in self._charts_widgets:
            old_w = self._charts_widgets[cid]
            old_w.setParent(None)

        if cid not in self._charts_order:
            self._charts_order.append(cid)

        self._charts_widgets[cid] = chart_widget
        self._charts_titles[cid] = display_title
        self._charts_visibility[cid] = bool(default_visible)
        chart_widget.setParent(self.cards_container)

        self._relayout_grid()
        self._update_badge()
        self._rebuild_more_menu()

    def remove_chart(self, chart_id: str):
        """从分组中移除指定图表"""
        cid = str(chart_id)
        if cid in self._charts_widgets:
            w = self._charts_widgets.pop(cid)
            w.setParent(None)
            self._charts_titles.pop(cid, None)
            self._charts_visibility.pop(cid, None)
            if cid in self._charts_order:
                self._charts_order.remove(cid)
            self._relayout_grid()
            self._update_badge()
            self._rebuild_more_menu()

    def get_chart(self, chart_id: str) -> Optional[QWidget]:
        """按 ID 获取子图表对象"""
        return self._charts_widgets.get(chart_id)

    def charts(self) -> Dict[str, QWidget]:
        """返回所有已注册的子图表字典 {chart_id: widget}"""
        return dict(self._charts_widgets)

    @property
    def chart_cards(self) -> Dict[str, QWidget]:
        """向后兼容属性，获取图表部件字典 {chart_id: widget}"""
        return self._charts_widgets

    @property
    def visible_charts(self) -> Dict[str, bool]:
        """向后兼容属性，获取各图表可见性字典"""
        return self._charts_visibility

    @property
    def show_train_series(self) -> bool:
        """检查 Train 系列是否处于显示状态"""
        for k, v in self._series_visibility.items():
            if "train" in k.lower():
                return v
        return True

    @property
    def show_val_series(self) -> bool:
        """检查 Val 系列是否处于显示状态"""
        for k, v in self._series_visibility.items():
            if "val" in k.lower():
                return v
        return True

    def set_chart_visible(self, chart_id: str, visible: bool):
        """按 ID 设置指定图表在网格中的显隐状态"""
        if chart_id in self._charts_visibility:
            self._charts_visibility[chart_id] = bool(visible)
            self._relayout_grid()
            self._update_badge()
            self.visibilityChanged.emit(chart_id, bool(visible))

    def is_chart_visible(self, chart_id: str) -> bool:
        """检查指定图表当前是否可见"""
        return self._charts_visibility.get(chart_id, True)

    def set_columns(self, columns: int):
        """动态修改网格列数"""
        self.columns = max(1, int(columns))
        self._relayout_grid()

    def show_all(self):
        """一键展示该分组下的所有图表"""
        for cid in self._charts_order:
            self._charts_visibility[cid] = True
        self._relayout_grid()
        self._update_badge()
        self._rebuild_more_menu()
        for cid in self._charts_order:
            self.visibilityChanged.emit(cid, True)

    def hide_all(self):
        """一键隐藏该分组下的所有图表"""
        for cid in self._charts_order:
            self._charts_visibility[cid] = False
        self._relayout_grid()
        self._update_badge()
        self._rebuild_more_menu()
        for cid in self._charts_order:
            self.visibilityChanged.emit(cid, False)

    def _relayout_grid(self):
        """响应式重排网格布局"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(self.cards_container)

        visible_count = 0
        for cid in self._charts_order:
            w = self._charts_widgets[cid]
            is_vis = self._charts_visibility.get(cid, True)
            if is_vis:
                row = visible_count // self.columns
                col = visible_count % self.columns
                self.grid_layout.addWidget(w, row, col)
                w.show()
                visible_count += 1
            else:
                w.hide()

    # ── 数据快速注入 API ──

    def set_series_data(
        self,
        chart_id: str,
        series_name: str,
        data: Sequence[Union[float, int, tuple]],
        **series_kwargs
    ):
        """快捷设置或更新指定图表的数据系列"""
        chart = self.get_chart(chart_id)
        if isinstance(chart, MkLineChart):
            found = False
            for s in chart.series_list:
                if s.name == series_name:
                    s.set_data(data)
                    found = True
                    break
            if not found:
                chart.add_series(series_name, data, **series_kwargs)
            else:
                chart.update()

    def append_point(self, chart_id: str, series_name: str, x: float, y: float):
        """流式向指定图表追加单点"""
        chart = self.get_chart(chart_id)
        if isinstance(chart, MkLineChart):
            for s in chart.series_list:
                if s.name == series_name:
                    s.points.append((float(x), float(y)))
                    s.points.sort(key=lambda p: p[0])
                    chart.canvas.update()
                    break

    def update_metrics(self, metrics: Dict[str, Any], step: Optional[float] = None):
        """
        批量更新训练指标 (用于 AI/模型训练监控或数据大屏流式刷新)
        metrics: 键值字典，如 {"precision(B)": 0.85, "train/box_loss": 0.42}
        """
        for key, val in metrics.items():
            if val is None:
                continue
            matched_id = None
            if key in self._charts_widgets:
                matched_id = key
            else:
                for cid, title in self._charts_titles.items():
                    if title == key:
                        matched_id = cid
                        break
            if matched_id:
                chart = self._charts_widgets[matched_id]
                if isinstance(chart, MkLineChart):
                    if not chart.series_list:
                        chart.add_series("metric", [(float(step or 0), float(val))])
                    else:
                        s = chart.series_list[0]
                        cur_x = float(step if step is not None else len(s.points))
                        s.points.append((cur_x, float(val)))
                        s.points.sort(key=lambda p: p[0])
                        chart.canvas.update()

    # ── 下拉菜单动态构建 (对标图一、图三) ──

    def _rebuild_more_menu(self):
        """构建图表可见性与序列选项下拉菜单"""
        self.btn_more.clear()

        # 1. 可选的 Series 区域 (如 Train / Val 虚实线全局切换)
        if self.enable_series_toggle and self.series_options:
            self.btn_more.add_label("Series")
            for s_name in self.series_options:
                checked = self._series_visibility.get(s_name, True)
                self.btn_more.add_check_item(
                    s_name,
                    item_id=f"series:{s_name}",
                    checked=checked,
                )
            self.btn_more.add_separator()

        # 2. 图表可见性清单 (Chart Visibility)
        self.btn_more.add_label("Chart Visibility")
        for cid in self._charts_order:
            title = self._charts_titles.get(cid, cid)
            checked = self._charts_visibility.get(cid, True)
            self.btn_more.add_check_item(
                title,
                item_id=f"chart:{cid}",
                checked=checked,
            )

        self.btn_more.add_separator()

        # 3. 底部快捷操作 (Show All / Hide All)
        self.btn_more.add_item(
            "Show All",
            item_id="show_all",
            icon="eye",
            callback=self.show_all
        )
        self.btn_more.add_item(
            "Hide All",
            item_id="hide_all",
            icon="eye-slash",
            callback=self.hide_all
        )

        try:
            self.btn_more.itemToggled.disconnect(self._on_menu_item_toggled)
        except Exception:
            pass
        self.btn_more.itemToggled.connect(self._on_menu_item_toggled)

    def _on_menu_item_toggled(self, item_id: str, checked: bool):
        if item_id.startswith("chart:"):
            cid = item_id[len("chart:"):]
            self.set_chart_visible(cid, checked)
        elif item_id.startswith("series:"):
            s_name = item_id[len("series:"):]
            self._series_visibility[s_name] = checked
            # 同步更新内部所有 MkLineChart 对应的同名 series
            for w in self._charts_widgets.values():
                if isinstance(w, MkLineChart):
                    for s in w.series_list:
                        if s.name.lower() in s_name.lower():
                            s.visible = checked
                    w.update()
            self.seriesToggled.emit(s_name, checked)


class MkChartDashboard(QWidget):
    """
    现代化多分组图表看板容器 (Chart Dashboard Container)
    
    统一管理多个 MkChartGroup (如 Metrics、Loss、Learning Rate 分组)，
    提供一键展开/收起全部、全局指标批量分发等高级看板功能。
    """
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        scrollable: bool = False,
        spacing: int = 14,
    ):
        super().__init__(parent)
        self.spacing = max(0, int(spacing))
        self.scrollable = bool(scrollable)
        self._groups: List[MkChartGroup] = []

        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        if self.scrollable:
            from monkeyqt.components.layout.scroll_area import MkScrollArea
            self.scroll_area = MkScrollArea(self)
            self.container = QWidget()
            self.container_layout = QVBoxLayout(self.container)
            self.container_layout.setContentsMargins(0, 0, 0, 0)
            self.container_layout.setSpacing(self.spacing)
            self.scroll_area.setWidget(self.container)
            root_layout.addWidget(self.scroll_area)
        else:
            self.container = self
            self.container_layout = root_layout
            self.container_layout.setSpacing(self.spacing)

    def add_group(
        self,
        title: str,
        group_id: Optional[str] = None,
        columns: int = 3,
        is_expanded: bool = True,
        **group_kwargs
    ) -> MkChartGroup:
        """快速添加并返回一个 MkChartGroup 分组卡片"""
        group = MkChartGroup(
            title=title,
            parent=self.container,
            columns=columns,
            is_expanded=is_expanded,
            **group_kwargs
        )
        if group_id:
            group.setObjectName(group_id)
        self.add_group_widget(group)
        return group

    def add_group_widget(self, group: MkChartGroup):
        """直接挂载外部创建的 MkChartGroup 分组卡片"""
        self._groups.append(group)
        self.container_layout.addWidget(group)

    def get_group(self, identifier: Union[str, int]) -> Optional[MkChartGroup]:
        """按索引或标题/对象名检索分组卡片"""
        if isinstance(identifier, int):
            if 0 <= identifier < len(self._groups):
                return self._groups[identifier]
            return None
        name = str(identifier)
        for g in self._groups:
            if g.objectName() == name or g.title_text == name:
                return g
        return None

    def groups(self) -> List[MkChartGroup]:
        """返回所有分组列表"""
        return list(self._groups)

    def expand_all(self):
        """展开全部图表分组"""
        for g in self._groups:
            g.set_expanded(True)

    def collapse_all(self):
        """折叠全部图表分组"""
        for g in self._groups:
            g.set_expanded(False)

    def update_metrics(self, metrics: Dict[str, Any], step: Optional[float] = None):
        """向看板中的所有图表分组广播指标更新"""
        for g in self._groups:
            g.update_metrics(metrics, step=step)

    def set_loading(self, loading: bool, skeleton_count: Optional[int] = None):
        """批量设置所有图表分组的骨架屏状态 (对标 Ultralytics 图三)"""
        for g in self._groups:
            g.set_loading(loading, skeleton_count=skeleton_count)
