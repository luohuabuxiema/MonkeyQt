# -*- coding: utf-8 -*-
"""
MonkeyQt Theme Gallery — 67 种 UI 风格可视化展示器

用法:
    python -m monkeyqt.themes.gallery
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLabel, QFrame, QScrollArea,
    QLineEdit, QSizePolicy, QSpacerItem, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

from .engine import ThemeEngine
from .components.button import ThemedButton
from .components.input import ThemedInput
from .components.switch import ThemedSwitch
from .components.card import ThemedCard
from .components.progress import ThemedProgressBar
from .components.alert import ThemedAlert
from .components.combobox import ThemedComboBox
from .components.slider import ThemedSlider
from .components.tabs import ThemedTabs
from .components.checkbox import ThemedCheckBox
from .components.progress_ring import ThemedProgressRing
from .components.avatar import ThemedAvatar
from .components.pagination import ThemedPagination
from .components.breadcrumb import ThemedBreadcrumb
from .components.dropdown import ThemedDropdown
from .components.table import ThemedTable
from .components.form import ThemedForm
from .components.date_picker import ThemedDatePicker
from .components.multicombobox import ThemedMultiComboBox
from .components.upload import ThemedUpload
from .components.topbar import ThemedTopbar
from .components.menu import ThemedMenu
from .components.message import ThemedMessage
from .components.captcha import ThemedCaptchaWidget
from .components.data_table import ThemedDataTable
from .components.image_compare import ThemedImageCompare
from .components.image_split import ThemedImageSplit
from .components.window import ThemedWindowShell


THEME_CN_NAMES = {
    'Minimalism & Swiss Style': '极简瑞士风格',
    'Neumorphism': '新拟物化 (Neumorphism)',
    'Glassmorphism': '玻璃拟态 (Glassmorphism)',
    'Brutalism': '粗野主义 (Brutalism)',
    '3D & Hyperrealism': '3D 与超现实',
    'Vibrant & Block-based': '活力板块风',
    'Dark Mode': '深色模式',
    'Accessible & Ethical': '无障碍与伦理设计',
    'Claymorphism': '黏土拟态 (Claymorphism)',
    'Aurora UI': '极光 UI (Aurora UI)',
    'Retro-Futurism': '复古未来主义',
    'Flat Design': '扁平化设计',
    'Skeuomorphism': '写实拟物化',
    'Liquid Glass': '流态玻璃',
    'Motion-Driven': '动效驱动',
    'Micro-interactions': '微交互风格',
    'Inclusive Design': '包容性设计',
    'Zero Interface': '无感零界面',
    'Soft UI Evolution': '柔和 UI 演进',
    'Neubrutalism': '新粗野主义 (Neubrutalism)',
    'Bento Box Grid': '便当盒网格 (Bento)',
    'Y2K Aesthetic': 'Y2K 千禧美学',
    'Cyberpunk UI': '赛博朋克 (Cyberpunk)',
    'Organic Biophilic': '有机双生设计',
    'AI-Native UI': 'AI 原生 UI',
    'Memphis Design': '孟菲斯设计 (Memphis)',
    'Vaporwave': '蒸汽波 (Vaporwave)',
    'Dimensional Layering': '多维分层',
    'Exaggerated Minimalism': '夸张极简主义',
    'Kinetic Typography': '动力字体设计',
    'Parallax Storytelling': '视差叙事',
    'Swiss Modernism 2.0': '瑞士现代主义 2.0',
    'HUD / Sci-Fi FUI': 'HUD 科幻界面',
    'Pixel Art': '像素艺术 (Pixel Art)',
    'Bento Grids': '便当网格',
    'Spatial UI (VisionOS)': '空间 UI (VisionOS)',
    'E-Ink / Paper': '电子墨水屏/纸质',
    'Gen Z Chaos / Maximalism': 'Z世代混乱/极繁',
    'Biomimetic / Organic 2.0': '仿生有机 2.0',
    'Anti-Polish / Raw Aesthetic': '反精致/粗砺美学',
    'Tactile Digital / Deformable UI': '触觉拟真/变形 UI',
    'Nature Distilled': '自然提炼色系',
    'Interactive Cursor Design': '交互式光标',
    'Voice-First Multimodal': '语音优先多模态',
    '3D Product Preview': '3D 产品预览',
    'Gradient Mesh / Aurora Evolved': '渐变网格/进化极光',
    'Editorial Grid / Magazine': '社论网格/杂志风',
    'Chromatic Aberration / RGB Split': '色差/RGB 分离',
    'Vintage Analog / Retro Film': '复古模拟胶片',
    'Hero-Centric Design': '大图主角设计',
    'Conversion-Optimized': '转化率优化设计',
    'Feature-Rich Showcase': '功能特性展示',
    'Minimal & Direct': '极简直达设计',
    'Social Proof-Focused': '社交信誉焦点',
    'Interactive Product Demo': '交互产品演示',
    'Trust & Authority': '信任与权威设计',
    'Storytelling-Driven': '故事叙事驱动',
    'Data-Dense Dashboard': '高密度数据看板',
    'Heat Map & Heatmap Style': '热力图分析风',
    'Executive Dashboard': '决策层仪表盘',
    'Real-Time Monitoring': '实时监控大屏',
    'Drill-Down Analytics': '下钻式深度分析',
    'Comparative Analysis Dashboard': '对比分析看板',
    'Predictive Analytics': '预测性分析风',
    'User Behavior Analytics': '用户行为分析',
    'Financial Dashboard': '财务指标看板',
    'Sales Intelligence Dashboard': '销售智能分析',
}


class ThemeGallery(QMainWindow):
    """67 种 UI 风格的可视化切换展示窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MonkeyQt 主题画廊 - 67 种风格")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ────── 左侧：风格列表面板 ──────
        left_panel = QWidget()
        left_panel.setFixedWidth(280)
        left_panel.setStyleSheet("""
            QWidget { background-color: #1E1E2E; }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 16, 12, 12)
        left_layout.setSpacing(10)

        # 标题
        title_lbl = QLabel("主题画廊")
        title_lbl.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #CDD6F4; background: transparent;")
        left_layout.addWidget(title_lbl)

        count_lbl = QLabel(f"提供 {len(ThemeEngine.list_themes())} 种视觉风格")
        count_lbl.setStyleSheet("color: #6C7086; font-size: 12px; background: transparent; font-family: 'Microsoft YaHei';")
        left_layout.addWidget(count_lbl)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索风格样式...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #313244;
                border: 1px solid #45475A;
                border-radius: 6px;
                color: #CDD6F4;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #89B4FA; }
        """)
        self.search_input.textChanged.connect(self._filter_themes)
        left_layout.addWidget(self.search_input)

        # 风格列表
        self.theme_list = QListWidget()
        self.theme_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                color: #BAC2DE;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px 10px;
                border-radius: 6px;
                margin-bottom: 2px;
            }
            QListWidget::item:hover {
                background-color: #313244;
            }
            QListWidget::item:selected {
                background-color: #45475A;
                color: #CDD6F4;
                font-weight: bold;
            }
        """)
        self._populate_theme_list()
        self.theme_list.currentItemChanged.connect(self._on_theme_selected)
        left_layout.addWidget(self.theme_list, 1)

        main_layout.addWidget(left_panel)

        # ────── 右侧：组件预览区 ──────
        right_panel = QWidget()
        right_panel.setObjectName("previewPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(24, 20, 24, 20)
        right_layout.setSpacing(16)

        # 顶部信息栏
        self.info_bar = QWidget()
        info_layout = QVBoxLayout(self.info_bar)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)

        self.lbl_theme_name = QLabel("极简瑞士风格")
        self.lbl_theme_name.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        info_layout.addWidget(self.lbl_theme_name)

        self.lbl_theme_meta = QLabel("通用视觉风格 (General) | Clean, simple, spacious...")
        self.lbl_theme_meta.setWordWrap(True)
        self.lbl_theme_meta.setFont(QFont("Microsoft YaHei", 10))
        info_layout.addWidget(self.lbl_theme_meta)

        # 色板展示
        self.color_bar = QWidget()
        self.color_bar.setFixedHeight(32)
        self.color_bar_layout = QHBoxLayout(self.color_bar)
        self.color_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.color_bar_layout.setSpacing(6)
        info_layout.addWidget(self.color_bar)

        right_layout.addWidget(self.info_bar)

        # 分割线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #E2E8F0; max-height: 1px;")
        right_layout.addWidget(sep)

        # 可滚动的组件预览区
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.preview_widget = QWidget()
        self.preview_widget.setStyleSheet("background: transparent;")
        self.preview_layout = QVBoxLayout(self.preview_widget)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(24)
        scroll.setWidget(self.preview_widget)
        right_layout.addWidget(scroll, 1)

        main_layout.addWidget(right_panel, 1)

        # 创建预览组件
        self._build_preview_components()

        # 默认选中第一个
        if self.theme_list.count() > 0:
            self.theme_list.setCurrentRow(0)

    def _populate_theme_list(self):
        """填充风格列表，按类型分组"""
        themes = ThemeEngine.list_themes()
        from .tokens import THEME_TOKENS

        type_map = {
            "General": "通用视觉风格 (General)",
            "Landing Page": "落地页风格 (Landing Page)",
            "BI/Analytics": "商业智能与大屏 (BI/Analytics)"
        }

        current_type = ""
        for name in themes:
            t = THEME_TOKENS[name]
            style_type = t.get("type", "General")

            # 类型分割头
            if style_type != current_type:
                current_type = style_type
                display_type = type_map.get(style_type, style_type)
                header_item = QListWidgetItem(f"── {display_type} ──")
                header_item.setFlags(Qt.ItemFlag.NoItemFlags)
                font = QFont("Microsoft YaHei", 9, QFont.Weight.Bold)
                header_item.setFont(font)
                header_item.setForeground(QColor("#6C7086"))
                self.theme_list.addItem(header_item)

            display_name = THEME_CN_NAMES.get(name, name)
            item = QListWidgetItem(f"  {display_name}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.theme_list.addItem(item)

    def _filter_themes(self, text: str):
        """过滤风格列表"""
        text = text.lower().strip()
        for i in range(self.theme_list.count()):
            item = self.theme_list.item(i)
            name = item.data(Qt.ItemDataRole.UserRole)
            if name is None:
                # 分组头 - 如果搜索时隐藏
                item.setHidden(bool(text))
            else:
                cn_name = THEME_CN_NAMES.get(name, "").lower()
                en_name = name.lower()
                item.setHidden(text not in en_name and text not in cn_name)

    def _build_preview_components(self):
        """构建右侧预览组件"""

        # ── Navigation Shell ──
        nav_section = self._make_section("导航容器 (Topbar / Menu)")
        self.topbar_demo = ThemedTopbar("MonkeyQt")
        self.topbar_demo.add_item("dashboard", "仪表盘")
        self.topbar_demo.add_item("components", "组件")
        self.topbar_demo.add_item("themes", "主题")
        self.topbar_demo.set_active("components")
        nav_section.addWidget(self.topbar_demo)

        self.menu_demo = ThemedMenu("侧边导航")
        self.menu_demo.add_item("home", "首页", "⌂")
        self.menu_demo.add_item("detect", "检测面板", "◎")
        self.menu_demo.add_item("settings", "系统设置", "⚙")
        self.menu_demo.set_active("detect")
        self.menu_demo.setFixedHeight(190)
        nav_section.addWidget(self.menu_demo)

        # ── Buttons ──
        btn_section = self._make_section("按钮 (Buttons)")
        btn_grid = QHBoxLayout()
        btn_grid.setSpacing(12)
        self.btn_primary = ThemedButton("主要按钮", btn_type="primary")
        self.btn_secondary = ThemedButton("次要按钮", btn_type="secondary")
        self.btn_default = ThemedButton("默认按钮", btn_type="default")
        self.btn_danger = ThemedButton("危险按钮", btn_type="danger")
        self.btn_success = ThemedButton("成功按钮", btn_type="success")
        self.btn_disabled = ThemedButton("禁用按钮", btn_type="primary")
        self.btn_disabled.setEnabled(False)
        for b in [self.btn_primary, self.btn_secondary, self.btn_default,
                   self.btn_danger, self.btn_success, self.btn_disabled]:
            btn_grid.addWidget(b)
        btn_grid.addStretch()
        btn_section.addLayout(btn_grid)

        # ── CheckBox ──
        check_section = self._make_section("复选框 (CheckBox)")
        check_row = QHBoxLayout()
        check_row.setSpacing(18)
        self.check_enabled = ThemedCheckBox("启用主题同步")
        self.check_enabled.setChecked(True)
        self.check_glass = ThemedCheckBox("玻璃材质")
        self.check_disabled = ThemedCheckBox("禁用项")
        self.check_disabled.setEnabled(False)
        for c in [self.check_enabled, self.check_glass, self.check_disabled]:
            check_row.addWidget(c)
        check_row.addStretch()
        check_section.addLayout(check_row)

        # ── Input ──
        input_section = self._make_section("输入框 (Input)")
        input_row = QHBoxLayout()
        input_row.setSpacing(12)
        self.input_normal = ThemedInput(placeholder="请输入内容...")
        self.input_focused = ThemedInput(placeholder="搜索...")
        input_row.addWidget(self.input_normal)
        input_row.addWidget(self.input_focused)
        input_section.addLayout(input_row)

        # ── ComboBox ──
        combo_section = self._make_section("下拉选择 (ComboBox)")
        combo_row = QHBoxLayout()
        combo_row.setSpacing(12)
        self.combo_style = ThemedComboBox()
        self.combo_style.addItems(["标准选项", "高级配置", "实时预览", "批量操作"])
        self.combo_status = ThemedComboBox()
        self.combo_status.addItems(["启用", "暂停", "草稿", "归档"])
        combo_row.addWidget(self.combo_style)
        combo_row.addWidget(self.combo_status)
        combo_row.addStretch()
        combo_section.addLayout(combo_row)

        # ── Date / Multi Select / Form ──
        form_section = self._make_section("表单组合 (Form / DatePicker / MultiComboBox)")
        self.form_demo = ThemedForm("检测参数", "组合式表单容器，用于承载多种 themed 输入控件。")
        self.date_picker_demo = ThemedDatePicker()
        self.multi_combo_demo = ThemedMultiComboBox("选择检测类别")
        self.multi_combo_demo.addItems(["person", "car", "bus", "dog", "cat"])
        self.multi_combo_demo.setCheckedData(["person", "car"])
        self.form_demo.add_row("日期", self.date_picker_demo)
        self.form_demo.add_row("类别", self.multi_combo_demo)
        self.captcha_demo = ThemedCaptchaWidget()
        self.form_demo.add_row("验证码", self.captcha_demo)
        form_section.addWidget(self.form_demo)

        # ── Dropdown ──
        dropdown_section = self._make_section("下拉菜单 (Dropdown)")
        dropdown_row = QHBoxLayout()
        dropdown_row.setSpacing(12)
        self.dropdown_action = ThemedDropdown("操作菜单")
        self.dropdown_action.add_item("编辑", "edit")
        self.dropdown_action.add_item("复制", "copy")
        self.dropdown_action.add_separator()
        self.dropdown_action.add_item("删除", "delete")
        self.dropdown_more = ThemedDropdown("更多")
        self.dropdown_more.add_item("导出 CSV", "export")
        self.dropdown_more.add_item("刷新数据", "refresh")
        dropdown_row.addWidget(self.dropdown_action)
        dropdown_row.addWidget(self.dropdown_more)
        dropdown_row.addStretch()
        dropdown_section.addLayout(dropdown_row)

        # ── Slider ──
        slider_section = self._make_section("滑块 (Slider)")
        self.slider_conf = ThemedSlider(Qt.Orientation.Horizontal)
        self.slider_conf.setRange(0, 100)
        self.slider_conf.setValue(72)
        self.slider_conf.set_formatter(lambda val: f"{val}%")
        self.slider_iou = ThemedSlider(Qt.Orientation.Horizontal)
        self.slider_iou.setRange(0, 100)
        self.slider_iou.setValue(45)
        self.slider_iou.set_formatter(lambda val: f"{val / 100:.2f}")
        slider_section.addWidget(self.slider_conf)
        slider_section.addWidget(self.slider_iou)

        # ── Switch ──
        switch_section = self._make_section("开关 (Switch)")
        switch_row = QHBoxLayout()
        switch_row.setSpacing(20)
        self.switch_on = ThemedSwitch(checked=True)
        self.switch_off = ThemedSwitch(checked=False)
        lbl_on = QLabel("开启")
        lbl_off = QLabel("关闭")
        for lbl in [lbl_on, lbl_off]:
            lbl.setStyleSheet("background: transparent; font-size: 12px; font-family: 'Microsoft YaHei';")
        switch_row.addWidget(lbl_on)
        switch_row.addWidget(self.switch_on)
        switch_row.addWidget(lbl_off)
        switch_row.addWidget(self.switch_off)
        switch_row.addStretch()
        switch_section.addLayout(switch_row)

        # ── Card ──
        card_section = self._make_section("卡片 (Card)")
        card_row = QHBoxLayout()
        card_row.setSpacing(16)
        self.card_1 = ThemedCard(title="系统设置")
        card_inner = QLabel("此处显示卡片内部内容。\n这是一个带主题样式的卡片容器。")
        card_inner.setWordWrap(True)
        card_inner.setStyleSheet("background: transparent; font-size: 12px; font-family: 'Microsoft YaHei';")
        self.card_1.content_layout.addWidget(card_inner)
        self.card_1.setFixedSize(300, 150)

        self.card_2 = ThemedCard(title="数据分析")
        card_inner2 = QLabel("仪表盘指标面板，\n采用对应风格的视觉样式。")
        card_inner2.setWordWrap(True)
        card_inner2.setStyleSheet("background: transparent; font-size: 12px; font-family: 'Microsoft YaHei';")
        self.card_2.content_layout.addWidget(card_inner2)
        self.card_2.setFixedSize(300, 150)

        card_row.addWidget(self.card_1)
        card_row.addWidget(self.card_2)
        card_row.addStretch()
        card_section.addLayout(card_row)

        # ── Avatar ──
        avatar_section = self._make_section("头像 (Avatar)")
        avatar_row = QHBoxLayout()
        avatar_row.setSpacing(12)
        self.avatar_a = ThemedAvatar("MQ", shape="circle", size=48)
        self.avatar_b = ThemedAvatar("AI", shape="square", size=48)
        self.avatar_c = ThemedAvatar("YO", shape="circle", size=56)
        avatar_row.addWidget(self.avatar_a)
        avatar_row.addWidget(self.avatar_b)
        avatar_row.addWidget(self.avatar_c)
        avatar_row.addStretch()
        avatar_section.addLayout(avatar_row)

        # ── Progress Bar ──
        prog_section = self._make_section("进度条 (Progress Bar)")
        self.prog_25 = ThemedProgressBar(percentage=25)
        self.prog_65 = ThemedProgressBar(percentage=65)
        self.prog_100 = ThemedProgressBar(percentage=100)
        prog_section.addWidget(self.prog_25)
        prog_section.addWidget(self.prog_65)
        prog_section.addWidget(self.prog_100)

        # ── Progress Ring ──
        ring_section = self._make_section("进度环 (Progress Ring)")
        ring_row = QHBoxLayout()
        ring_row.setSpacing(18)
        self.ring_normal = ThemedProgressRing(percentage=72, status="normal", width=96)
        self.ring_success = ThemedProgressRing(percentage=100, status="success", width=96)
        self.ring_warning = ThemedProgressRing(percentage=38, status="warning", width=96)
        for ring in [self.ring_normal, self.ring_success, self.ring_warning]:
            ring_row.addWidget(ring)
        ring_row.addStretch()
        ring_section.addLayout(ring_row)

        # ── Alert ──
        alert_section = self._make_section("提示框 (Alert)")
        self.alert_info = ThemedAlert("这是一条系统提示信息。", alert_type="info")
        self.alert_success = ThemedAlert("操作已成功完成！", alert_type="success")
        self.alert_warning = ThemedAlert("在继续操作前，请先仔细检查。", alert_type="warning")
        self.alert_error = ThemedAlert("处理过程中发生了一个错误。", alert_type="error")
        alert_section.addWidget(self.alert_info)
        alert_section.addWidget(self.alert_success)
        alert_section.addWidget(self.alert_warning)
        alert_section.addWidget(self.alert_error)

        # ── Message ──
        message_section = self._make_section("消息提示 (Message)")
        message_row = QHBoxLayout()
        message_row.setSpacing(10)
        self.message_success = ThemedMessage("保存成功，主题已同步。", "success")
        self.message_warning = ThemedMessage("部分风格需要自绘增强。", "warning")
        message_row.addWidget(self.message_success)
        message_row.addWidget(self.message_warning)
        message_section.addLayout(message_row)

        # ── Upload ──
        upload_section = self._make_section("上传 (Upload)")
        self.upload_demo = ThemedUpload(multiple=True, tip_text="支持拖拽或点击选择，适合图片/视频/模型文件。")
        upload_section.addWidget(self.upload_demo)

        # ── Breadcrumb ──
        breadcrumb_section = self._make_section("面包屑 (Breadcrumb)")
        self.breadcrumb_demo = ThemedBreadcrumb(separator="/")
        self.breadcrumb_demo.set_items([
            {"id": "home", "text": "首页"},
            {"id": "themes", "text": "主题系统"},
            {"id": "components", "text": "组件预览"},
        ])
        breadcrumb_section.addWidget(self.breadcrumb_demo)

        # ── Pagination ──
        page_section = self._make_section("分页器 (Pagination)")
        self.pagination_demo = ThemedPagination(total=186, page_size=10, current=8)
        page_section.addWidget(self.pagination_demo)

        # ── Table ──
        table_section = self._make_section("表格 (Table)")
        self.table_demo = ThemedTable(0, 3)
        self.table_demo.set_headers(["组件", "状态", "主题适配"])
        self.table_demo.set_data([
            ["Button", "完成", "交互态/复杂风格"],
            ["ComboBox", "完成", "弹出层/QSS"],
            ["ProgressRing", "完成", "语义色/发光"],
            ["Table", "新增", "数据展示"],
        ])
        table_section.addWidget(self.table_demo)

        # ── DataTable ──
        data_table_section = self._make_section("数据表组合 (DataTable)")
        self.data_table_demo = ThemedDataTable(
            columns=["模型", "尺寸", "状态"],
            data=[
                ["yolov8n.pt", "6.2MB", "Ready"],
                ["yolov8s.pt", "21.5MB", "Ready"],
                ["custom-best.pt", "42.1MB", "Training"],
                ["demo.onnx", "12.0MB", "Exported"],
            ],
            page_size=3,
        )
        data_table_section.addWidget(self.data_table_demo)

        # ── Image Widgets ──
        image_section = self._make_section("图像组件 (Image Compare / Split)")
        image_row = QHBoxLayout()
        image_row.setSpacing(14)
        self.image_compare_demo = ThemedImageCompare()
        self.image_compare_demo.setFixedHeight(150)
        self.image_split_demo = ThemedImageSplit()
        self.image_split_demo.setFixedHeight(150)
        image_row.addWidget(self.image_compare_demo)
        image_row.addWidget(self.image_split_demo)
        image_section.addLayout(image_row)

        # ── Window Shell ──
        window_section = self._make_section("窗口外壳 (Window / TitleBar)")
        self.window_shell_demo = ThemedWindowShell("MonkeyQt Theme Preview")
        self.window_shell_demo.setFixedHeight(130)
        shell_text = QLabel("可作为自定义标题栏、嵌入面板或窗口预览容器的主题化基础。")
        shell_text.setWordWrap(True)
        shell_text.setStyleSheet("background: transparent; font-size: 12px;")
        self.window_shell_demo.content_layout.addWidget(shell_text)
        window_section.addWidget(self.window_shell_demo)

        # ── Tabs ──
        tabs_section = self._make_section("标签页 (Tabs)")
        self.tabs_demo = ThemedTabs()
        for tab_id, title, body in [
            ("overview", "概览", "主题 token、组件状态和全局 QSS 的综合预览。"),
            ("metrics", "指标", "用于仪表盘、YOLO 检测面板、表单参数区等场景。"),
            ("logs", "日志", "承载较轻的信息流，验证标签切换和内容容器风格。"),
        ]:
            label = QLabel(body)
            label.setWordWrap(True)
            label.setMinimumHeight(70)
            label.setStyleSheet("background: transparent; padding: 12px; font-size: 12px;")
            self.tabs_demo.add_tab(tab_id, title, label)
        tabs_section.addWidget(self.tabs_demo)

        # 底部留白
        self.preview_layout.addStretch()

    def _make_section(self, title: str) -> QVBoxLayout:
        """创建一个带标题的预览区段"""
        container = QVBoxLayout()
        container.setSpacing(10)
        lbl = QLabel(title)
        lbl.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.DemiBold))
        lbl.setStyleSheet("background: transparent;")
        lbl.setObjectName("sectionTitle")
        container.addWidget(lbl)
        self.preview_layout.addLayout(container)
        return container

    def _on_theme_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        if not current:
            return
        name = current.data(Qt.ItemDataRole.UserRole)
        if not name:
            return

        # 切换全局主题
        ThemeEngine.set_theme(name)
        tokens = ThemeEngine.current_tokens()

        # 更新信息栏
        display_name = THEME_CN_NAMES.get(name, name)
        self.lbl_theme_name.setText(display_name)
        keywords = tokens.get("keywords", "")[:100]
        style_type = tokens.get("type", "General")

        type_map = {
            "General": "通用视觉风格 (General)",
            "Landing Page": "落地页风格 (Landing Page)",
            "BI/Analytics": "商业智能与大屏 (BI/Analytics)"
        }
        display_type = type_map.get(style_type, style_type)
        self.lbl_theme_meta.setText(f"{display_type}  |  {keywords}")

        # 更新色板
        self._update_color_bar(tokens)

        # 更新预览区背景
        bg = tokens.get("--bg", "#FFFFFF")
        fg = tokens.get("--fg", "#1E293B")
        panel = self.centralWidget().findChild(QWidget, "previewPanel")
        if panel is None:
            # fallback: right panel is second child
            panel = self.centralWidget().layout().itemAt(1).widget()
        panel.setStyleSheet(f"""
            QWidget#previewPanel {{ background-color: {bg}; }}
            QLabel {{ color: {fg}; }}
            QLabel#sectionTitle {{ color: {fg}; }}
        """)
        self.lbl_theme_name.setStyleSheet(f"background: transparent; color: {fg};")
        self.lbl_theme_meta.setStyleSheet(f"background: transparent; color: {fg}; opacity: 0.7;")

        # 刷新所有组件
        for w in [self.btn_primary, self.btn_secondary, self.btn_default,
                   self.btn_danger, self.btn_success, self.btn_disabled,
                   self.topbar_demo, self.menu_demo,
                   self.check_enabled, self.check_glass, self.check_disabled,
                   self.input_normal, self.input_focused,
                   self.combo_style, self.combo_status,
                   self.form_demo, self.date_picker_demo, self.multi_combo_demo, self.captcha_demo,
                   self.dropdown_action, self.dropdown_more,
                   self.slider_conf, self.slider_iou,
                   self.card_1, self.card_2,
                   self.avatar_a, self.avatar_b, self.avatar_c,
                   self.prog_25, self.prog_65, self.prog_100,
                   self.ring_normal, self.ring_success, self.ring_warning,
                   self.alert_info, self.alert_success, self.alert_warning, self.alert_error,
                   self.message_success, self.message_warning,
                   self.upload_demo,
                   self.breadcrumb_demo, self.pagination_demo, self.table_demo, self.data_table_demo,
                   self.image_compare_demo, self.image_split_demo, self.window_shell_demo, self.tabs_demo]:
            if hasattr(w, 'set_theme_style'):
                w.set_theme_style(name)
            elif hasattr(w, '_update_style'):
                w._update_style()
            self._safe_widget_update(w)

        # 开关也需刷新
        self._safe_widget_update(self.switch_on)
        self._safe_widget_update(self.switch_off)

    def _safe_widget_update(self, widget):
        """Refresh normal widgets and item-view widgets without tripping PySide overloads."""
        try:
            widget.update()
            return
        except TypeError:
            viewport = getattr(widget, "viewport", None)
            if callable(viewport):
                try:
                    viewport().update()
                    return
                except (TypeError, RuntimeError, AttributeError):
                    pass
        except RuntimeError:
            pass

    def _update_color_bar(self, tokens: dict):
        """更新色板展示条"""
        # 清除旧的
        while self.color_bar_layout.count():
            child = self.color_bar_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        color_keys = ["--bg", "--fg", "--primary", "--secondary", "--accent", "--border"]
        for key in color_keys:
            val = tokens.get(key, "")
            if not val or not val.startswith("#"):
                continue
            swatch = QLabel()
            swatch.setFixedSize(24, 24)
            swatch.setStyleSheet(f"""
                background-color: {val};
                border: 1px solid #CCC;
                border-radius: 4px;
            """)
            swatch.setToolTip(f"{key}: {val}")
            self.color_bar_layout.addWidget(swatch)

            label = QLabel(val)
            label.setFont(QFont("Consolas", 9))
            label.setStyleSheet("background: transparent; color: #888;")
            self.color_bar_layout.addWidget(label)

        self.color_bar_layout.addStretch()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    gallery = ThemeGallery()
    gallery.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
