import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QStackedWidget, QFrame, QGridLayout
)
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtCore import Qt, QEvent
from monkeyqt import (
    MkButton, MkCheckBox, MkMenu, MkTopbar, MkBreadcrumb, MkTabs,
    MkSegmented, MkSegmentedTabs,
    MkAlert, MkProgressBar, MkProgressRing,
    MkTooltip, MkInfoIcon, create_field_header, create_input_field, create_switch_field,
    MkPagination, MkDropdown, MkSwitch, MkSlider, MkDatePicker, MkForm,
    MkInput, MkCaptchaWidget, MkAuthScreen, MkMessage,
    MkAvatar, MkProTable, MkImageCompare, MkImageSplit,
    MkTitleBar, MkWindow, MkUpload, MkComboBox, MkMultiComboBox,
    MkConsole, MkQWidget, MkWidget, MkScrollArea, MkStackedWidget,
    ThemeEngine, MkThemeSelector, apply_monkeyqt_theme, use_theme
)

class ButtonGallery(MkQWidget):
    """按钮组件的展示页"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        
        # 1. 基础用法
        label_basic = QLabel("基础用法 (Basic Types)")
        label_basic.setFont(title_font)
        layout.addWidget(label_basic)
        
        basic_layout = QHBoxLayout()
        basic_layout.addWidget(MkButton("Default"))
        basic_layout.addWidget(MkButton("Primary", type="primary"))
        basic_layout.addWidget(MkButton("Success", type="success"))
        basic_layout.addWidget(MkButton("Info", type="info"))
        basic_layout.addWidget(MkButton("Warning", type="warning"))
        basic_layout.addWidget(MkButton("Danger", type="danger"))
        basic_layout.addStretch()
        layout.addLayout(basic_layout)

        # 2. 禁用状态
        label_disabled = QLabel("禁用状态 (Disabled State)")
        label_disabled.setFont(title_font)
        layout.addWidget(label_disabled)
        
        disabled_layout = QHBoxLayout()
        for t, name in [("default", "Default"), ("primary", "Primary"), ("success", "Success"), 
                       ("info", "Info"), ("warning", "Warning"), ("danger", "Danger")]:
            btn = MkButton(name, type=t)
            btn.setEnabled(False)
            disabled_layout.addWidget(btn)
        disabled_layout.addStretch()
        layout.addLayout(disabled_layout)

        # 3. 尺寸
        label_sizes = QLabel("不同尺寸 (Sizes)")
        label_sizes.setFont(title_font)
        layout.addWidget(label_sizes)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(MkButton("Large", type="primary", size="large"))
        size_layout.addWidget(MkButton("Default", type="primary", size="default"))
        size_layout.addWidget(MkButton("Small", type="primary", size="small"))
        size_layout.addStretch()
        layout.addLayout(size_layout)

        layout.addStretch()

class CheckboxGallery(MkQWidget):
    """复选框组件的展示页"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        
        label_checkbox = QLabel("复选框 (CheckBox)")
        label_checkbox.setFont(title_font)
        layout.addWidget(label_checkbox)
        
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(MkCheckBox("Option 1"))
        
        chk2 = MkCheckBox("Option 2 (Checked)")
        chk2.setChecked(True)
        checkbox_layout.addWidget(chk2)
        
        chk3 = MkCheckBox("Disabled")
        chk3.setEnabled(False)
        checkbox_layout.addWidget(chk3)
        
        chk4 = MkCheckBox("Disabled & Checked")
        chk4.setChecked(True)
        chk4.setEnabled(False)
        checkbox_layout.addWidget(chk4)
        
        checkbox_layout.addStretch()
        layout.addLayout(checkbox_layout)

        layout.addStretch()

class TopbarGallery(MkQWidget):
    """顶部导航栏组件的展示页"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 为了演示顶部导航栏的完整效果，我们在这个页面模拟一个完整的窗口结构
        
        # 1. 顶部导航栏
        self.topbar = MkTopbar(logo_text="Monkey Qt")
        self.topbar.add_item("home", "处理中心")
        self.topbar.add_item("workspace", "我的工作台")
        self.topbar.add_item("orders", "订单管理")
        self.topbar.add_item("settings", "系统设置")
        
        # 默认选中处理中心
        self.topbar.set_active("home")
        
        layout.addWidget(self.topbar)
        
        # 2. 下方的模拟内容区域
        content_area = MkQWidget(role="transparent")
        content_layout = QVBoxLayout(content_area)
        
        self.status_label = QLabel("当前选中：处理中心 (home)")
        self.status_label.setFont(QFont("Microsoft YaHei", 12))
        content_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(content_area, stretch=1)
        
        # 连接信号
        self.topbar.itemClicked.connect(self._on_topbar_clicked)
        
    def _on_topbar_clicked(self, item_id):
        self.status_label.setText(f"当前选中：{item_id}")

class NavMiscGallery(MkQWidget):
    """面包屑与标签页展示"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        
        # 1. 面包屑
        label_breadcrumb = QLabel("面包屑导航 (Breadcrumb)")
        label_breadcrumb.setFont(title_font)
        layout.addWidget(label_breadcrumb)
        
        self.breadcrumb1 = MkBreadcrumb(separator="/")
        self.breadcrumb1.set_items([
            {"id": "home", "text": "首页"},
            {"id": "nav", "text": "导航组件"},
            {"id": "breadcrumb", "text": "面包屑"}
        ])
        layout.addWidget(self.breadcrumb1)
        
        self.breadcrumb2 = MkBreadcrumb(separator=">")
        self.breadcrumb2.set_items([
            {"id": "home", "text": "Home"},
            {"id": "user", "text": "User Management"},
            {"id": "detail", "text": "User Detail"}
        ])
        layout.addWidget(self.breadcrumb2)

        # 2. 标签页
        label_tabs = QLabel("标签页 (Tabs)")
        label_tabs.setFont(title_font)
        layout.addWidget(label_tabs)
        
        self.tabs = MkTabs()
        self.tabs.setFixedHeight(200) # 限定一下高度，方便展示
        
        # 标签1内容
        tab1_content = MkQWidget(role="transparent")
        t1_layout = QVBoxLayout(tab1_content)
        t1_layout.addWidget(QLabel("用户个人中心，支持放置任意自定义 QWidget"))

        
        # 标签2内容
        tab2_content = MkQWidget(role="transparent")
        t2_layout = QVBoxLayout(tab2_content)
        t2_layout.addWidget(QLabel("这是 配置管理 的内容面板"))
        
        self.tabs.add_tab("user", "用户管理", tab1_content)
        self.tabs.add_tab("config", "配置管理", tab2_content)
        
        layout.addWidget(self.tabs)
        
        # 3. 分段任务栏与胶囊导航 (MkSegmented & MkSegmentedTabs)
        label_seg = QLabel("分段任务栏与胶囊导航 (Segmented Tabs & Controls)")
        label_seg.setFont(title_font)
        layout.addWidget(label_seg)

        # 3.1 独立胶囊开关 (7天/30天与视图切换)
        seg_switches_layout = QHBoxLayout()
        self.seg_pill = MkSegmented(items=["7 天", "30 天"], size="default", pill=True)
        self.seg_pill.set_current_index(1)
        seg_switches_layout.addWidget(self.seg_pill)

        self.seg_radius = MkSegmented(items=["日视图", "周视图", "月视图", "季度"], radius=8, pill=False, size="default")
        seg_switches_layout.addWidget(self.seg_radius)

        self.seg_small = MkSegmented(items=["全部", "运行中", "已归档"], size="small", pill=True)
        seg_switches_layout.addWidget(self.seg_small)
        seg_switches_layout.addStretch()
        layout.addLayout(seg_switches_layout)

        # 3.2 一体化分段页面容器 (带徽标与内容自适应)
        self.seg_tabs = MkSegmentedTabs(size="large", radius=12, pill=False, tab_align="left")

        tab_p1 = MkQWidget(role="transparent")
        p1_l = QVBoxLayout(tab_p1)
        p1_l.setContentsMargins(12, 12, 12, 12)
        p1_l.addWidget(QLabel("概览页面：训练用时 26s，GPU RTX PRO 6000，计算成本 $0.02"))

        tab_p2 = MkQWidget(role="transparent")
        p2_l = QVBoxLayout(tab_p2)
        p2_l.setContentsMargins(12, 12, 12, 12)
        p2_l.addWidget(QLabel("训练指标页面：precision 0.762，recall 0.512，mAP50-95 0.472"))

        tab_p3 = MkQWidget(role="transparent")
        p3_l = QVBoxLayout(tab_p3)
        p3_l.setContentsMargins(12, 12, 12, 12)
        p3_l.addWidget(QLabel("模型导出页面：支持一键导出 ONNX, TensorRT, OpenVINO, CoreML"))

        self.seg_tabs.add_tab("overview", "概览", tab_p1)
        self.seg_tabs.add_tab("train", "训练指标", tab_p2)
        self.seg_tabs.add_tab("export", "模型导出", tab_p3, badge="1")
        self.seg_tabs.add_tab("deploy", "服务部署", QLabel("云端一键部署已就绪"))
        layout.addWidget(self.seg_tabs)
        
        # 4. 分页器
        label_pagination = QLabel("分页器 (Pagination)")
        label_pagination.setFont(title_font)
        layout.addWidget(label_pagination)
        
        self.pagination = MkPagination(total=200, page_size=10, current=1)
        layout.addWidget(self.pagination)

        # 5. 下拉菜单
        label_dropdown = QLabel("下拉菜单 (Dropdown)")
        label_dropdown.setFont(title_font)
        layout.addWidget(label_dropdown)
        
        dropdown_layout = QHBoxLayout()
        self.dropdown = MkDropdown("操作菜单")
        self.dropdown.add_item("新增", "add")
        self.dropdown.add_item("编辑", "edit")
        self.dropdown.add_separator()
        self.dropdown.add_item("删除", "delete")
        
        dropdown_layout.addWidget(self.dropdown)
        dropdown_layout.addStretch()
        layout.addLayout(dropdown_layout)

        layout.addStretch()

class FeedbackGallery(MkQWidget):
    """反馈类组件展示页 (Tooltip Popover, Alert, Progress)"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)

        # 1. 气泡提示与信息图标 (Tooltip Popover & InfoIcon)
        label_tooltip = QLabel("气泡提示与信息图标 (Tooltip Popover & InfoIcon)")
        label_tooltip.setFont(title_font)
        layout.addWidget(label_tooltip)

        # 1.1 通用控件一键绑定气泡提示 (MkTooltip.attach)
        attach_box = QHBoxLayout()
        attach_box.setSpacing(12)
        btn_hover1 = MkButton("悬停查看气泡提示 (Hover Me)", type="primary")
        MkTooltip.attach(btn_hover1, "这是使用 MkTooltip.attach 绑定的气泡提示，具有平滑圆角与自适应指示箭头。")
        
        btn_hover2 = MkButton("短文本提示", type="default")
        MkTooltip.attach(btn_hover2, "简单快捷的操作提示")

        attach_box.addWidget(btn_hover1)
        attach_box.addWidget(btn_hover2)
        attach_box.addStretch()
        layout.addLayout(attach_box)

        layout.addSpacing(20)

        # 1.2 现代化 AI 训练参数卡片展示（参考 LabelPaw & Ultralytics HUB）
        card_train = MkQWidget(layout="v", role="card", radius=8, border=True, margins=16, spacing=14)
        card_lay = card_train.inner_layout

        card_title = QLabel("AI 训练超参数配置与字段提示 (对标 Ultralytics HUB / LabelPaw 规范)")
        card_title.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        card_lay.addWidget(card_title)
        card_lay.addSpacing(6)

        header_row = QHBoxLayout()
        header_row.addWidget(create_field_header(
            "基础模型选择 (Base Model)",
            hint="选择预训练模型架构，如 `yolov8n.pt` 或本地模型权重。在 Python 中对应 `model` 参数。Learn more ↗"
        ))
        header_row.addWidget(create_field_header(
            "训练数据集配置 (Dataset)",
            hint="配置用于模型训练的数据集 YAML。在 Python 中对应 `data` 参数。Learn more ↗"
        ))
        card_lay.addLayout(header_row)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(8)

        f_lr0, _ = create_input_field("初始学习率 (lr0)", "0.01", "初始学习率 (lr0)。SGD 推荐 0.01，Adam/AdamW 推荐 0.001")
        f_lrf, _ = create_input_field("最终学习率比例 (lrf)", "0.01", "最终学习率比率 (lrf)。最终学习率 = lr0 * lrf，默认 0.01")
        f_momentum, _ = create_input_field("动量系数 (momentum)", "0.937", "动量系数 (momentum)。控制梯度更新的惯性大小（对应 SGD 的动量系数，或 Adam/AdamW 算法中的 β1 衰减参数），默认 0.937")
        f_patience, _ = create_input_field("早停等待轮数 (patience)", "100", "早停机制等待轮数 (patience)。连续 N 轮验证集指标未提升则提前终止训练，默认 100")
        f_close_mosaic, _ = create_input_field("关闭 Mosaic 轮数 (close_mosaic)", "10", "最后 N 轮禁用 Mosaic 数据增强 (close_mosaic)。稳定收敛提升精度，0 为全程启用，默认 10")
        f_cos_lr, _ = create_switch_field("余弦退火调度 (cos_lr)", default_checked=True, hint="余弦退火学习率调度器 (cos_lr)。启用余弦退火动态平滑衰减学习率")

        grid.addWidget(f_lr0, 0, 0)
        grid.addWidget(f_lrf, 0, 1)
        grid.addWidget(f_momentum, 0, 2)
        grid.addWidget(f_patience, 1, 0)
        grid.addWidget(f_close_mosaic, 1, 1)
        grid.addWidget(f_cos_lr, 1, 2)

        card_lay.addLayout(grid)
        layout.addWidget(card_train)

        # 2. 警告提示 (Alert)
        label_alert = QLabel("警告提示 (Alert)")
        label_alert.setFont(title_font)
        layout.addWidget(label_alert)
        
        layout.addWidget(MkAlert(title="成功提示的文案", mk_type="success", show_icon=True))
        layout.addWidget(MkAlert(title="消息提示的文案", mk_type="info", show_icon=True, closable=True))
        layout.addWidget(MkAlert(
            title="错误提示的文案", 
            description="这是一句绕口令：黑化肥发灰，灰化肥发黑。黑化肥发灰会挥发；灰化肥挥发会发黑。",
            mk_type="error", 
            show_icon=True, 
            closable=True
        ))

        # 3. 进度条与进度环 (Progress Bar & Progress Ring)
        label_progress_bar = QLabel("进度展示 (Progress)")
        label_progress_bar.setFont(title_font)
        layout.addWidget(label_progress_bar)
        
        prog_row = QHBoxLayout()
        prog_row.addWidget(MkProgressBar(percentage=75, status="normal"))
        prog_row.addWidget(MkProgressBar(percentage=100, status="success"))
        layout.addLayout(prog_row)

        ring_layout = QHBoxLayout()
        ring_layout.addWidget(MkProgressRing(percentage=25, status="normal"))
        ring_layout.addWidget(MkProgressRing(percentage=100, status="success"))
        ring_layout.addWidget(MkProgressRing(percentage=75, status="warning"))
        ring_layout.addWidget(MkProgressRing(percentage=50, status="exception"))
        ring_layout.addStretch()
        layout.addLayout(ring_layout)

        layout.addStretch()

class DataGallery(MkQWidget):
    """数据展示组件展示页 (Avatar)"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        
        # 1. 头像 (Avatar)
        label_avatar = QLabel("头像组件 (MkAvatar)")
        label_avatar.setFont(title_font)
        layout.addWidget(label_avatar)
        
        desc = QLabel("支持多种形状（圆形 circle、圆角矩形 square）以及丰富尺寸与文本缩略。")
        desc.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(desc)
        
        avatar_layout = QHBoxLayout()
        avatar_layout.setSpacing(16)
        avatar_layout.addWidget(MkAvatar(text="U", size=32, shape="circle"))
        avatar_layout.addWidget(MkAvatar(text="User", size=40, shape="circle"))
        avatar_layout.addWidget(MkAvatar(text="Admin", size=50, shape="circle"))
        avatar_layout.addWidget(MkAvatar(text="Pro", size=60, shape="circle"))
        avatar_layout.addWidget(MkAvatar(text="Dev", size=50, shape="square"))
        avatar_layout.addWidget(MkAvatar(text="AI", size=40, shape="square"))
        avatar_layout.addStretch()
        layout.addLayout(avatar_layout)
        
        layout.addStretch()


class ProTableGallery(MkQWidget):
    """高级响应式 ProTable 仪表盘数据表格展示页 (继承 MkQWidget，集聚前端现代化特性)"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        
        # 1. 标题与说明
        label_title = QLabel("现代化前端高级数据表格 (MkProTable)")
        label_title.setFont(title_font)
        layout.addWidget(label_title)
        
        desc = QLabel(
            "基于现代 Web 仪表盘美学封装的新一代数据表格，原生继承 MkQWidget(role='card')。\n"
            "特性包含：复选框全选/跨页记忆 (selectable=True)、图片缩略图+悬浮眼眸+高清灯箱大图 (type='image')、"
            "视频缩略图+播放角标+视频播放器弹窗 (type='video')、快速模糊过滤搜索、表头循环排序 (↑↓/↑/↓)、"
            "外边框与圆角实时调节、每页行数下拉切换、自适应 68 种主题风格。"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 13px; line-height: 20px;")
        layout.addWidget(desc)

        # 控制栏
        control_bar = QHBoxLayout()
        control_bar.setSpacing(8)
        
        self.btn_toggle_select = MkButton("关闭复选框", type="default", size="small")
        self.btn_toggle_select.clicked.connect(self._toggle_selectable)
        control_bar.addWidget(self.btn_toggle_select)

        btn_select_all = MkButton("全选当前页", type="default", size="small")
        btn_select_all.clicked.connect(lambda: self.pro_table.select_all())
        control_bar.addWidget(btn_select_all)

        btn_clear_sel = MkButton("清空已选", type="default", size="small")
        btn_clear_sel.clicked.connect(lambda: self.pro_table.clear_selection())
        control_bar.addWidget(btn_clear_sel)

        btn_border_1 = MkButton("默认边框 (1px, R12)", type="default", size="small")
        btn_border_1.clicked.connect(lambda: self.pro_table.set_border_props(width=1, radius=12))
        control_bar.addWidget(btn_border_1)

        btn_border_2 = MkButton("加粗边框 (2px, R14)", type="default", size="small")
        btn_border_2.clicked.connect(lambda: self.pro_table.set_border_props(width=2, radius=14))
        control_bar.addWidget(btn_border_2)

        btn_border_0 = MkButton("无外边框 (0px)", type="default", size="small")
        btn_border_0.clicked.connect(lambda: self.pro_table.set_border_props(width=0, radius=0))
        control_bar.addWidget(btn_border_0)

        btn_radius_round = MkButton("大圆角 (20px)", type="default", size="small")
        btn_radius_round.clicked.connect(lambda: self.pro_table.set_border_props(width=1, radius=20))
        control_bar.addWidget(btn_radius_round)

        self.btn_toggle_action = MkButton("显示操作列", type="default", size="small")
        self.btn_toggle_action.clicked.connect(self._toggle_action_column)
        control_bar.addWidget(self.btn_toggle_action)

        btn_expand_desc = MkButton("拓宽描述列 (340px)", type="default", size="small")
        btn_expand_desc.clicked.connect(lambda: self.pro_table.set_column_width("description", 340))
        control_bar.addWidget(btn_expand_desc)

        btn_reset_widths = MkButton("均匀分布列宽", type="default", size="small")
        btn_reset_widths.clicked.connect(lambda: self.pro_table.reset_column_widths())
        control_bar.addWidget(btn_reset_widths)

        control_bar.addStretch()
        layout.addLayout(control_bar)

        # 资源文件路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        before_path = os.path.join(base_dir, "assets", "before.png")
        after_path = os.path.join(base_dir, "assets", "after.png")
        video_path = os.path.join(base_dir, "assets", "demo_video.mp4")

        # 列配置：引入复选框 (selectable 参数控制)、图片 preview_img、视频 preview_vid、类型徽章、状态徽章等
        columns = [
            {"key": "name", "label": "项目 / 模型名称", "type": "avatar_text", "sortable": True},
            {"key": "preview_img", "label": "结果图片", "type": "image", "width": 88, "align": "center"},
            {"key": "preview_vid", "label": "演示视频", "type": "video", "width": 88, "align": "center"},
            {"key": "type", "label": "类型", "type": "badge", "sortable": True},
            {"key": "description", "label": "描述与备注", "type": "text", "sortable": True},
            {"key": "status", "label": "运行状态", "type": "status", "sortable": True},
            {"key": "updated", "label": "更新时间", "type": "text", "sortable": True},
        ]

        # 示例多媒体数据 (14 条，支持跨页多选与分页交互)
        mock_data = [
            {"name": "Alpha 核心项目", "type": "项目", "description": "核心模板项目工程 (对标 Ultralytics HUB 训练流水线，集成预训练模型校验与一键导出)", "status": "已完成", "updated": "2 天前", "color": "#ef4444", "preview_img": before_path, "preview_vid": video_path},
            {"name": "自动化训练流水线", "type": "项目", "description": "基于 YOLOv8 的工业安全帽与反光衣实时目标检测自动化训练管道", "status": "已完成", "updated": "5 天前", "color": "#ec4899", "preview_img": after_path, "preview_vid": video_path},
            {"name": "高精度图像数据集 2026", "type": "数据集", "description": "8 张高动态范围无人机航拍检测图像，已完成全景实例分割掩码切片", "status": "就绪", "updated": "2026年5月28日", "avatar": before_path, "preview_img": before_path, "preview_vid": video_path},
            {"name": "实用目标检测模型 v2", "type": "数据集", "description": "6 张多分类工业质检标注样本集，包含表面划痕与金属凹坑缺陷标记", "status": "就绪", "updated": "2026年5月28日", "avatar": after_path, "preview_img": after_path, "preview_vid": video_path},
            {"name": "YOLOv8 边缘推理模型", "type": "数据集", "description": "2 张边缘计算芯片实测基准图像，包含 FP16 与 INT8 量化延迟测试", "status": "就绪", "updated": "2026年5月27日", "avatar": before_path, "preview_img": before_path, "preview_vid": video_path},
            {"name": "精细化分类识别模型", "type": "数据集", "description": "2 张多视角图像", "status": "就绪", "updated": "2026年5月27日", "avatar": after_path, "preview_img": after_path, "preview_vid": video_path},
            {"name": "智能图像分割数据集", "type": "数据集", "description": "1 张超分辨率图像", "status": "就绪", "updated": "2026年5月21日", "avatar": before_path, "preview_img": before_path, "preview_vid": video_path},
            {"name": "优质样本检测库", "type": "数据集", "description": "11 张缺陷检测图像", "status": "就绪", "updated": "2026年5月21日", "avatar": after_path, "preview_img": after_path, "preview_vid": video_path},
            {"name": "高并发 OCR 文字识别", "type": "数据集", "description": "1 张票据图像", "status": "就绪", "updated": "2026年5月20日", "avatar": before_path, "preview_img": before_path, "preview_vid": video_path},
            {"name": "高速模型推理服务器", "type": "项目", "description": "高吞吐并发推理服务", "status": "进行中", "updated": "2026年5月18日", "color": "#3b82f6", "preview_img": after_path, "preview_vid": video_path},
            {"name": "待人工复核任务", "type": "项目", "description": "等待管理员手动复核", "status": "待处理", "updated": "2026年5月15日", "color": "#f59e0b", "preview_img": before_path, "preview_vid": video_path},
            {"name": "损坏缓存清理任务", "type": "数据集", "description": "0 张图像已清理", "status": "失败", "updated": "2026年5月10日", "color": "#ef4444", "preview_img": after_path, "preview_vid": video_path},
            {"name": "超分辨率画质放大模型", "type": "项目", "description": "4 倍画质超分放大模型", "status": "已完成", "updated": "2026年5月8日", "color": "#10b981", "preview_img": before_path, "preview_vid": video_path},
            {"name": "自动驾驶车道线数据集", "type": "数据集", "description": "2400 张标注图像", "status": "就绪", "updated": "2026年5月5日", "avatar": before_path, "preview_img": after_path, "preview_vid": video_path},
        ]

        self.pro_table = MkProTable(
            columns=columns,
            data=mock_data,
            title="近期动态与多媒体资产",
            description="展示最新的数据集、项目与图片/视频预览，支持跨页多选与高级交互",
            searchable=True,
            search_placeholder="搜索活动名称、类型或描述...",
            selectable=True,
            page_size=5,
            page_size_options=[5, 10, 20],
            border_width=1,
            border_radius=12,
            show_actions=False,
            parent=self
        )
        layout.addWidget(self.pro_table, stretch=1)

        # 实时交互状态卡
        self.status_card = QLabel("提示：点击图片缩略图可唤起大图灯箱；点击视频缩略图可唤起播放弹窗；点击行头复选框支持全选与跨页记忆。")
        self.status_card.setStyleSheet("color: #64748b; font-size: 12px; font-style: italic;")
        layout.addWidget(self.status_card)

        # 选中项统计条
        self.selection_label = QLabel("当前选中：0 项")
        self.selection_label.setStyleSheet("color: #0ea5e9; font-weight: 500; font-size: 13px;")
        layout.addWidget(self.selection_label)

        self.pro_table.rowClicked.connect(self._on_row_clicked)
        self.pro_table.actionTriggered.connect(self._on_action_triggered)
        self.pro_table.selectionChanged.connect(self._on_selection_changed)

    def _toggle_selectable(self):
        new_state = not self.pro_table.selectable
        self.pro_table.set_selectable(new_state)
        self.btn_toggle_select.setText("关闭复选框" if new_state else "开启复选框")

    def _toggle_action_column(self):
        new_state = not self.pro_table.show_actions
        self.pro_table.set_show_actions(new_state)
        self.btn_toggle_action.setText("隐藏操作列" if new_state else "显示操作列")

    def _on_selection_changed(self, selected_items: list):
        names = [item.get("name", "") for item in selected_items]
        preview_text = ", ".join(names[:3]) + ("..." if len(names) > 3 else "")
        self.selection_label.setText(f"当前选中：{len(selected_items)} 项 ({preview_text if names else '无'})")

    def _on_row_clicked(self, index: int, row_data: dict):
        self.status_card.setText(f"点击行事件：第 {index + 1} 项，名称: {row_data.get('name')}，状态: {row_data.get('status')}")

    def _on_action_triggered(self, action_name: str, index: int, row_data: dict):
        self.status_card.setText(f"操作按钮触发：[{action_name}] 针对数据项: {row_data.get('name')}")

class FormGallery(MkQWidget):
    """表单录入组件展示页 (Switch, Slider, DatePicker, ComboBox, MultiComboBox, Form)"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        
        # 1. 结构化表单
        label_form = QLabel("表单与输入组件 (Form, Switch, Slider, DatePicker, ComboBox, MultiComboBox)")
        label_form.setFont(title_font)
        layout.addWidget(label_form)
        
        self.form = MkForm(label_width=100, label_position="right")
        
        # Switch
        self.switch = MkSwitch(checked=True)
        self.form.add_item("即时配送", self.switch)
        
        # Slider
        self.slider = MkSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(40)
        self.form.add_item("优先级", self.slider)
        
        # DatePicker
        self.date_picker = MkDatePicker()
        self.form.add_item("活动时间", self.date_picker)
        
        # ComboBox (Single Select)
        self.combobox = MkComboBox()
        self.combobox.addItems(["选项一 (Option 1)", "选项二 (Option 2)", "选项三 (Option 3)"])
        self.form.add_item("单选下拉框", self.combobox)
        
        # MultiComboBox (Multi Select)
        self.multi_combobox = MkMultiComboBox()
        self.multi_combobox.addItems({
            0: "苹果 (Apple)",
            1: "香蕉 (Banana)",
            2: "橙子 (Orange)",
            3: "葡萄 (Grape)",
            4: "西瓜 (Watermelon)"
        })
        self.form.add_item("多选下拉框", self.multi_combobox)
        
        layout.addWidget(self.form)
        layout.addStretch()

class AuthGallery(MkQWidget):
    """登录与注册组件展示页"""
    def __init__(self):
        super().__init__()
        # Horizontal layout: left control panel, right auth screen preview
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(30)
        
        # --- 1. Left Control Panel ---
        control_panel = QFrame(self)
        control_panel.setObjectName("AuthControlPanel")
        control_panel.setFixedWidth(260)
        control_panel.setProperty("mkPanel", "true")
        
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(12)
        
        panel_title = QLabel("Auth 自定义控制台")
        panel_title.setObjectName("AuthPanelTitle")
        panel_title.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        control_layout.addWidget(panel_title)
        
        # Background setting
        control_layout.addWidget(QLabel("背景主题配置"))
        self.bg_combo = MkComboBox()
        self.bg_combo.addItems([
            "极光深蓝渐变",
            "皇家魅紫渐变",
            "高级纯灰背景",
            "本地大图背景"
        ])
        control_layout.addWidget(self.bg_combo)
        
        # Avatar option
        control_layout.addWidget(QLabel("头像配置"))
        self.avatar_check = MkCheckBox("启用顶部头像")
        self.avatar_check.setChecked(True)
        control_layout.addWidget(self.avatar_check)
        
        self.avatar_shape_combo = MkComboBox()
        self.avatar_shape_combo.addItems(["圆形头像 (circle)", "方形头像 (square)"])
        control_layout.addWidget(self.avatar_shape_combo)
        
        # Captcha Type
        control_layout.addWidget(QLabel("安全验证码"))
        self.captcha_combo = MkComboBox()
        self.captcha_combo.addItems([
            "图形验证码 (graphic)",
            "短信验证码 (sms)",
            "无验证码 (none)"
        ])
        control_layout.addWidget(self.captcha_combo)
        
        # Register Custom Fields Config
        control_layout.addWidget(QLabel("注册页自定义字段"))
        self.custom_fields_combo = MkComboBox()
        self.custom_fields_combo.addItems([
            "默认字段 (用户名+邮箱+密码)",
            "性别 + 手机号",
            "地址 + 个人简介 + 年龄"
        ])
        control_layout.addWidget(self.custom_fields_combo)
        
        # Rebuild trigger button
        self.rebuild_btn = MkButton("一键生成登录界面", type="primary")
        self.rebuild_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rebuild_btn.setFixedHeight(36)
        self.rebuild_btn.clicked.connect(self.rebuild_auth_screen)
        control_layout.addWidget(self.rebuild_btn)
        
        # Dynamic Custom Fields Input & Button
        control_layout.addWidget(QLabel("动态添加单字段"))
        self.custom_field_input = MkInput("例如: 兴趣爱好 / 毕业院校")
        control_layout.addWidget(self.custom_field_input)
        
        self.add_field_btn = MkButton("一键添加此字段", type="success")
        self.add_field_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_field_btn.setFixedHeight(36)
        self.add_field_btn.clicked.connect(self.add_single_custom_field)
        control_layout.addWidget(self.add_field_btn)
        
        control_layout.addStretch()
        main_layout.addWidget(control_panel)
        
        # --- 2. Right Preview Panel ---
        self.preview_container = MkQWidget(self, role="transparent")
        self.preview_layout = QVBoxLayout(self.preview_container)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        
        main_layout.addWidget(self.preview_container, stretch=1)
        
        # Initial build
        self.auth_screen = None
        self.rebuild_auth_screen()

    def rebuild_auth_screen(self):
        # 1. Clear old screen
        if self.auth_screen:
            self.auth_screen.deleteLater()
            
        # 2. Resolve background config
        bg_opt = self.bg_combo.currentText()
        if bg_opt == "极光深蓝渐变":
            bg = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e293b, stop:1 #0f172a)"
        elif bg_opt == "皇家魅紫渐变":
            bg = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4f46e5, stop:1 #06b6d4)"
        elif bg_opt == "高级纯灰背景":
            bg = "#f1f5f9"
        else:
            # Use local gallery before.png
            base_dir = os.path.dirname(os.path.abspath(__file__))
            bg = os.path.join(base_dir, "assets", "before.png")
            
        # 3. Resolve avatar path & shape
        avatar_path = None
        if self.avatar_check.isChecked():
            # Use local after.png as user avatar
            base_dir = os.path.dirname(os.path.abspath(__file__))
            avatar_path = os.path.join(base_dir, "assets", "after.png")
            
        avatar_shape = "circle" if "circle" in self.avatar_shape_combo.currentText() else "square"
        
        # 4. Resolve captcha
        captcha_text = self.captcha_combo.currentText()
        if "graphic" in captcha_text:
            captcha_type = "graphic"
        elif "sms" in captcha_text:
            captcha_type = "sms"
        else:
            captcha_type = "none"
            
        # 4b. Resolve register custom fields
        custom_fields = None
        fields_opt = self.custom_fields_combo.currentText()
        if "性别" in fields_opt:
            custom_fields = [
                {"name": "gender", "placeholder": "请设置您的性别 (例如: 男/女)", "icon": "pencil"},
                {"name": "phone", "placeholder": "请输入您的密保手机号码", "icon": "pencil"}
            ]
        elif "地址" in fields_opt:
            custom_fields = [
                {"name": "address", "placeholder": "请输入您的常住居住地址", "icon": "pencil"},
                {"name": "bio", "placeholder": "请输入一句话个性签名", "icon": "pencil"},
                {"name": "age", "placeholder": "请输入您的真实年龄", "icon": "pencil"}
            ]
            
        # 5. Instantiate new MkAuthScreen
        self.auth_screen = MkAuthScreen(
            logo_text="Monkey Qt",
            description="风格极简授权中心",
            avatar=avatar_path,
            avatar_shape=avatar_shape,
            captcha_type=captcha_type,
            background=bg,
            register_custom_fields=custom_fields,
            parent=self.preview_container
        )
        
        # Connect callbacks
        self.auth_screen.loginSubmitted.connect(self._on_login_submitted)
        self.auth_screen.registerSubmitted.connect(self._on_register_submitted)
        self.auth_screen.smsRequested.connect(self._on_sms_requested)
        self.auth_screen.forgotPasswordClicked.connect(self._on_forgot_password_clicked)
        
        self.preview_layout.addWidget(self.auth_screen)
        if ThemeEngine.current_theme():
            apply_monkeyqt_theme(self.auth_screen)
 
    def _on_login_submitted(self, username, password, captcha_code, remember_me=False):
        remember_str = " (记住密码: 是)" if remember_me else " (记住密码: 否)"
        # Mock checks (database validation callback simulation)
        if username == "admin" and password == "admin123":
            MkMessage.success(self.window(), f"登录成功，欢迎尊贵的管理员回来！{remember_str}")
        else:
            # Failure popups
            MkMessage.error(self.window(), f"用户名或密码错误，请检查！(提示: admin / admin123){remember_str}")
 
    def _on_register_submitted(self, username, email, password, confirm_password, custom_fields=None):
        custom_str = ""
        if custom_fields:
            custom_str = " | 自定义: " + str(custom_fields)
        MkMessage.success(self.window(), f"注册成功！您的账号: {username}，我们已向 {email} 发送激活信！{custom_str}")
        # Toggle back to login mode
        self.auth_screen.switch_mode("login")
 
    def _on_sms_requested(self, email):
        MkMessage.info(self.window(), f"验证码已发送至：{email}，请查收短信/邮件！")

    def _on_forgot_password_clicked(self):
        MkMessage.warning(self.window(), "找回密码提示：系统已拦截点击事件，请接入您的找回密码业务逻辑！")

    def add_single_custom_field(self):
        field_name = self.custom_field_input.text().strip()
        if not field_name:
            MkMessage.error(self.window(), "请先在输入框中输入需要添加的字段名称！")
            return
        if self.auth_screen:
            self.auth_screen.add_register_field(field_name, f"请输入您的{field_name}", "pencil")
            MkMessage.success(self.window(), f"成功添加字段：{field_name}！切换至注册面板即可预览效果")
            self.custom_field_input.clear()

class ImageCompareGallery(MkQWidget):
    """图像对比组件展示页 (MkImageCompare)"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        
        label_title = QLabel("图像对比 (Image Compare)")
        label_title.setFont(title_font)
        layout.addWidget(label_title)
        
        desc = QLabel("交互式双图对比组件，常用于展示风格迁移、超分辨率、深度图像修复等模型的前后结果对比。")
        desc.setStyleSheet("color: #606266; font-size: 13px;")
        layout.addWidget(desc)
        
        # 获取图片的绝对路径，确保能在各种工作目录下正确加载
        base_dir = os.path.dirname(os.path.abspath(__file__))
        before_path = os.path.join(base_dir, "assets", "before.png")
        after_path = os.path.join(base_dir, "assets", "after.png")
        
        # 风格迁移对比实例 (带标签)
        compare_widget = MkImageCompare(before_path, after_path)
        layout.addWidget(compare_widget, stretch=1)
        
        tip_label = QLabel("提示：可以在上方图片中任意位置点击或拖动滑块，以交互式查看“迁移结果”与“原图”细节。")
        tip_label.setStyleSheet("color: #909399; font-size: 12px; font-style: italic;")
        layout.addWidget(tip_label)

class ImageSplitGallery(MkQWidget):
    """分屏对比组件展示页 (MkImageSplit)"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        
        label_title = QLabel("分屏对比 (Image Split)")
        label_title.setFont(title_font)
        layout.addWidget(label_title)
        
        desc = QLabel("左右分屏无损对比组件。双图完整并排渲染，拖拽中间的手柄可以改变分屏比例；点击手柄上的左右箭头，能优雅地平滑收缩折叠某一边，实现单图与双图对比的快速切换。")
        desc.setStyleSheet("color: #606266; font-size: 13px;")
        layout.addWidget(desc)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        before_path = os.path.join(base_dir, "assets", "before.png")
        after_path = os.path.join(base_dir, "assets", "after.png")
        
        # 实例化分屏对比组件
        split_widget = MkImageSplit(before_path, after_path)
        layout.addWidget(split_widget, stretch=1)
        
        tip_label = QLabel("提示：您可以拖拽中央的垂直胶囊手柄调节分屏比例，或者点击手柄上的箭头平滑收缩/还原左侧或右侧图片。")
        tip_label.setStyleSheet("color: #909399; font-size: 12px; font-style: italic;")
        layout.addWidget(tip_label)

class ConsoleGallery(MkQWidget):
    """控制台日志组件展示页 (MkConsole / ThemedConsole)"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        
        # 1. 标题与说明
        label_title = QLabel("控制台日志 (Console)")
        label_title.setFont(title_font)
        layout.addWidget(label_title)
        
        desc = QLabel(
            "一个美观且功能丰富的控制台日志输出组件。支持 68 种主题自适应、自动滚动、"
            "一键清除、带计数指示面板、支持水平与垂直滚动，具有方便的各级别日志打印 API。"
        )
        desc.setStyleSheet("color: #64748b; font-size: 13px; line-height: 18px;")
        layout.addWidget(desc)
        
        # 2. 实例化 MkConsole
        self.console = MkConsole("输出控制台")
        layout.addWidget(self.console, stretch=1)
        
        # 3. 交互控制按钮
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        btn_info = MkButton("打印 Info", type="default")
        btn_info.clicked.connect(lambda: self.console.info("这是一条普通系统信息。"))
        control_layout.addWidget(btn_info)
        
        btn_success = MkButton("打印 Success", type="success")
        btn_success.clicked.connect(lambda: self.console.success("恭喜，任务处理圆满成功！"))
        control_layout.addWidget(btn_success)
        
        btn_warn = MkButton("打印 Warning", type="warning")
        btn_warn.clicked.connect(lambda: self.console.warn("警告：检测到显存使用率超过 90%！"))
        control_layout.addWidget(btn_warn)
        
        btn_error = MkButton("打印 Error", type="danger")
        btn_error.clicked.connect(lambda: self.console.error("错误：模型文件加载失败，IO 读取异常。"))
        control_layout.addWidget(btn_error)
        
        btn_debug = MkButton("打印 Debug", type="info")
        btn_debug.clicked.connect(lambda: self.console.debug("调试信息: layer_index=12, tensor_shape=[1, 3, 640, 640]"))
        control_layout.addWidget(btn_debug)
        
        layout.addLayout(control_layout)
        
        # Seed with initial logs
        self.console.info("欢迎使用 MonkeyQt 控制台组件。")
        self.console.success("系统所有核心组件加载完毕。")

class WindowGallery(MkQWidget):
    """自定义窗口与标题栏展示页"""
    def __init__(self):
        super().__init__()
        # Use a horizontal layout for the split page: controls on the left, preview on the right
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(30)
        
        # Left Panel (Controls)
        control_panel = QFrame(self)
        control_panel.setFixedWidth(280)
        control_panel.setProperty("mkPanel", "true")
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(10)
        
        title_label = QLabel("自定义窗口控制台")
        title_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        control_layout.addWidget(title_label)
        
        # 1. Preset Selector
        control_layout.addWidget(QLabel("选择主题预设风格 (Presets)"))
        self.preset_combo = MkComboBox()
        self.preset_combo.addItem("默认风格 (default)", "default")
        self.preset_combo.addItem("Shadcn UI风格 (shadcn)", "shadcn")
        self.preset_combo.addItem("IDA Pro风格 (ida)", "ida")
        self.preset_combo.addItem("向日葵风格 (sunlogin)", "sunlogin")
        self.preset_combo.addItem("汽水音乐风格 (soda)", "soda")
        self.preset_combo.addItem("IDE风格 (ide)", "ide")
        control_layout.addWidget(self.preset_combo)
        
        # 2. Custom Background Color override
        control_layout.addWidget(QLabel("自定义背景色 (Hex/RGBA)"))
        self.bg_color_input = MkInput(placeholder="留空则使用预设默认色")
        control_layout.addWidget(self.bg_color_input)
        
        # 3. Custom Text Color override
        control_layout.addWidget(QLabel("自定义文字色 (Hex)"))
        self.text_color_input = MkInput(placeholder="留空则使用预设默认色")
        control_layout.addWidget(self.text_color_input)
        
        # 4. Height override
        control_layout.addWidget(QLabel("标题栏高度 (30 - 70 px)"))
        self.height_slider = MkSlider(Qt.Horizontal)
        self.height_slider.show_value = False
        self.height_slider.setRange(30, 70)
        self.height_slider.setValue(40)
        control_layout.addWidget(self.height_slider)
        
        # 5. Radius override
        control_layout.addWidget(QLabel("窗口圆角半径 (0 - 20 px)"))
        self.radius_slider = MkSlider(Qt.Horizontal)
        self.radius_slider.show_value = False
        self.radius_slider.setRange(0, 20)
        self.radius_slider.setValue(8)
        control_layout.addWidget(self.radius_slider)
        
        # 6. Close button behavior
        control_layout.addWidget(QLabel("关闭按钮行为"))
        self.close_combo = MkComboBox()
        self.close_combo.addItem("销毁窗口并退出 (close)", "close")
        self.close_combo.addItem("隐藏到后台/托盘 (hide)", "hide")
        control_layout.addWidget(self.close_combo)
        
        # 7. Action Button
        self.btn_launch = MkButton("启动独立无边框窗口", type="primary")
        self.btn_launch.clicked.connect(self.launch_demo_window)
        control_layout.addWidget(self.btn_launch)
        
        control_layout.addStretch()
        
        main_layout.addWidget(control_panel)
        
        # Right Panel (Live Mini Preview)
        preview_panel = QFrame(self)
        preview_panel.setProperty("mkPanel", "true")
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        preview_layout.setSpacing(15)
        
        preview_header = QLabel("标题栏实时外观预览 (Local Mini Mock)")
        preview_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #334155; border: none; background: transparent;")
        preview_layout.addWidget(preview_header)
        
        # Container to hold the mock window preview
        self.mock_win_frame = QFrame()
        self.mock_win_frame.setObjectName("MockWindowFrame")
        self.mock_win_frame.setFrameShape(QFrame.Shape.NoFrame)
        mock_win_layout = QVBoxLayout(self.mock_win_frame)
        mock_win_layout.setContentsMargins(0, 0, 0, 0)
        mock_win_layout.setSpacing(0)
        
        # Add the MkTitleBar inside the mock frame
        self.mock_titlebar = MkTitleBar(preset="default")
        self.mock_titlebar.set_title("MonkeyQt - YOLO Target Detection Console")
        # Set a dummy icon
        base_dir = os.path.dirname(os.path.abspath(__file__))
        after_path = os.path.join(base_dir, "assets", "after.png")
        if os.path.exists(after_path):
            self.mock_titlebar.set_icon(QPixmap(after_path))
            
        mock_win_layout.addWidget(self.mock_titlebar)
        
        # Fake client area in mock
        self.mock_client = MkQWidget(role="surface", radius=8)
        self.mock_client.setObjectName("MockClient")
        self.mock_client_layout = QVBoxLayout(self.mock_client)
        self.mock_client_layout.setContentsMargins(20, 40, 20, 40)
        
        self.mock_desc = QLabel("这里是子页面的模拟客户端区域。\n选择左侧的预设风格或滑动高度/圆角，以直接观察此处的实时变化。")
        self.mock_desc.setAlignment(Qt.AlignCenter)
        self.mock_client_layout.addWidget(self.mock_desc)
        
        mock_win_layout.addWidget(self.mock_client, stretch=1)
        
        preview_layout.addWidget(self.mock_win_frame, stretch=1)
        
        main_layout.addWidget(preview_panel, stretch=1)
        
        # Connect settings signals
        self.preset_combo.currentIndexChanged.connect(self.update_mini_preview)
        self.bg_color_input.textChanged.connect(self.update_mini_preview)
        self.text_color_input.textChanged.connect(self.update_mini_preview)
        self.height_slider.valueChanged.connect(self.update_mini_preview)
        self.radius_slider.valueChanged.connect(self.update_mini_preview)
        
        # Initial trigger
        self.update_mini_preview()
        
    def update_mini_preview(self):
        preset = self.preset_combo.currentData()
        bg_color = self.bg_color_input.text().strip()
        text_color = self.text_color_input.text().strip()
        height = self.height_slider.value()
        radius = self.radius_slider.value()
        
        # Apply configurations to mock titlebar
        self.mock_titlebar.apply_preset(preset)
        
        # Override values
        if bg_color:
            self.mock_titlebar._bg_color = bg_color
        if text_color:
            self.mock_titlebar._text_color = text_color
            
        self.mock_titlebar._height = height
        
        # Refresh drawing
        self.mock_titlebar.apply_theme_colors()
        self.mock_titlebar.rebuild_layout()
        
        # Refresh Mock window container styling (border, radius)
        border_color = "#e4e4e7" if preset == "shadcn" else "#3f3f3f" if preset == "ida" else "#313244" if preset == "ide" else "#e2e8f0"
        
        window_bg = "#ffffff"
        client_text = "#94a3b8"
        if preset in ["ida", "sunlogin", "soda", "ide"]:
            window_bg = "#1e1e2e" if preset == "ide" else "#1e1f22" if preset == "sunlogin" else "#121212" if preset == "soda" else "#1a1a1a"
            client_text = "#64748b"
            
        self.mock_win_frame.setStyleSheet(f"""
            QFrame#MockWindowFrame {{
                background-color: {window_bg};
                border: 1px solid {border_color};
                border-radius: {radius}px;
            }}
        """)
        self.mock_desc.setStyleSheet(f"color: {client_text}; font-size: 12px; line-height: 18px;")
        
    def launch_demo_window(self):
        preset = self.preset_combo.currentData()
        bg_color = self.bg_color_input.text().strip()
        text_color = self.text_color_input.text().strip()
        height = self.height_slider.value()
        radius = self.radius_slider.value()
        close_behavior = self.close_combo.currentData()
        
        # Spawn MkWindow
        self.demo_win = MkWindow(use_custom_title_bar=True, preset=preset)
        self.demo_win.setWindowTitle("MonkeyQt - YOLO Target Detection System")
        
        # Set Window icon
        base_dir = os.path.dirname(os.path.abspath(__file__))
        after_path = os.path.join(base_dir, "assets", "after.png")
        if os.path.exists(after_path):
            self.demo_win.setWindowIcon(QIcon(after_path))
            
        self.demo_win.set_border_radius(radius)
        self.demo_win.set_close_behavior(close_behavior)
        
        # Apply overrides if specified
        if bg_color:
            self.demo_win.titlebar._bg_color = bg_color
        if text_color:
            self.demo_win.titlebar._text_color = text_color
        self.demo_win.titlebar._height = height
        self.demo_win.titlebar.apply_theme_colors()
        self.demo_win.titlebar.rebuild_layout()
        self.demo_win.update_style()
        
        # Central contents dashboard for YOLO Detection mock
        content = MkQWidget(role="transparent", layout="v", margins=(30, 25, 30, 25), spacing=15)
        content_layout = content.inner_layout
        
        title_font = QFont("Microsoft YaHei", 14, QFont.Bold)
        info_label = QLabel("独立自定义无边框窗口示例")
        info_label.setFont(title_font)
        
        # Select title color based on preset theme
        title_color = "#ffffff" if preset in ["ida", "sunlogin", "soda", "ide"] else "#0f172a"
        info_label.setStyleSheet(f"color: {title_color};")
        
        desc_label = QLabel(
            f"<b>当前标题预设:</b> {preset}<br>"
            f"<b>窗体圆角半径:</b> {radius}px<br>"
            f"<b>高度大小:</b> {height}px<br>"
            f"<b>关闭处理行为:</b> {close_behavior}<br><br>"
            "<b>核心交互提示:</b><br>"
            "• 拖拽顶部的自定义标题栏可以<b>移动</b>该无边框窗口。<br>"
            "• 双击顶部标题栏可以<b>最大化 / 还原</b>窗口大小。<br>"
            "• 将鼠标指针悬停在<b>窗口外沿四周及四角</b>，会显现大小缩放箭头，拖拽即可直接<b>调整窗口大小</b>。<br>"
            "• 窗体周围在无边框下自带高档<b>卡片式投影效果</b>，视觉十分丝滑！"
        )
        desc_color = "#94a3b8" if preset in ["ida", "sunlogin", "soda", "ide"] else "#475569"
        desc_label.setStyleSheet(f"font-size: 12px; line-height: 20px; color: {desc_color};")
        
        close_btn = MkButton("关闭该独立窗口", type="danger")
        close_btn.clicked.connect(self.demo_win.close)
        
        content_layout.addWidget(info_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(desc_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.demo_win.setCentralWidget(content)
        self.demo_win.resize(640, 420)
        self.demo_win.show()

class UploadGallery(MkQWidget):
    """文件上传组件展示页 (MkUpload)"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        
        # Title & Desc
        label_title = QLabel("文件上传 (Upload)")
        label_title.setFont(title_font)
        layout.addWidget(label_title)
        
        desc = QLabel("支持拖拽文件和点击选择上传，内置文件类型限制、体积上限过滤以及美观的已选择文件列表。")
        desc.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(desc)
        
        # 1. Single File Upload
        label_single = QLabel("单文件上传 (Single File)")
        label_single.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(label_single)
        
        self.upload_single = MkUpload(multiple=False, max_size_mb=10, tip_text="支持任意单文件，文件体积不超过 10MB")
        layout.addWidget(self.upload_single)
        
        # 2. Image-only Multi-file Upload
        label_multi_img = QLabel("图片多选上传 (Image Files Only)")
        label_multi_img.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(label_multi_img)
        
        self.upload_images = MkUpload(
            multiple=True, 
            accept_filters=["*.png", "*.jpg", "*.jpeg", "*.gif"], 
            max_size_mb=5, 
            tip_text="仅支持图片格式 (png, jpg, jpeg, gif)，单个不超过 5MB"
        )
        layout.addWidget(self.upload_images)
        
        # Log Box to display drop/upload logs
        label_logs = QLabel("上传操作日志 (Interaction Logs)")
        label_logs.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(label_logs)
        
        self.log_area = QLabel("等待上传交互...")
        self.log_area.setObjectName("UploadLogArea")
        self.log_area.setProperty("mkPanel", "true")
        self.log_area.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log_area)
        
        # Connect signals to update log box
        self.upload_single.filesSelected.connect(self._on_single_selected)
        self.upload_images.filesSelected.connect(self._on_images_selected)
        self.upload_single.fileRemoved.connect(lambda f: self._on_file_removed("单文件", f))
        self.upload_images.fileRemoved.connect(lambda f: self._on_file_removed("图片列表", f))
        
        layout.addStretch()

    def _on_single_selected(self, files):
        if files:
            self.log_area.setText(f"[单文件已选择]: {files[0]}")
        else:
            self.log_area.setText("[单文件已选择]: 无")
            
    def _on_images_selected(self, files):
        files_str = "\n  - ".join(files)
        self.log_area.setText(f"[多图已选择 ({len(files)}个)]:\n  - {files_str}" if files else "[多图已选择]: 无")
        
    def _on_file_removed(self, category, file_path):
        self.log_area.setText(f"[{category} 移除了文件]: {os.path.basename(file_path)}")

class MainGallery(MkWindow):
    def __init__(self):
        super().__init__(
            use_custom_title_bar=True,
            preset="default",
            sidebar_full_height=True,
        )
        self.setWindowTitle("MonkeyQt - Enterprise Gallery")
        self.resize(1500, 1000)
        
        # 自定义标题栏：高度加高，移除下边框线 (参考 mainui.py)
        self.titlebar._height = 48
        self.titlebar._border_bottom = "none"
        self.titlebar.apply_theme_colors()
        self.titlebar.rebuild_layout()
        self.update_style()
        self._setup_theme_selector()
        
        # --- 创建主布局（左右结构，参考 mainui.py） ---
        self.central_widget = MkQWidget(role="bg", layout="h", margins=0, spacing=0)
        self.central_widget.setObjectName("MainCentralWidget")
        self.main_layout = self.central_widget.inner_layout
        
        # --- 1. 创建并配置侧边栏 (参考 mainui.py) ---
        self.sidebar = MkMenu(title="MonkeyQt", collapse_mode="hamburger")
        self.sidebar.set_border_right("none")
        
        sub_basic = self.sidebar.add_submenu("基础组件", icon="squares-four")
        self.sidebar.add_submenu_item(sub_basic, "btn", "Button 按钮", icon="cursor-click")
        self.sidebar.add_submenu_item(sub_basic, "chk", "CheckBox 复选框", icon="check-square")
        
        sub_nav = self.sidebar.add_submenu("导航", icon="compass")
        self.sidebar.add_submenu_item(sub_nav, "sidebar", "侧边导航", icon="sidebar")
        self.sidebar.add_submenu_item(sub_nav, "topbar", "顶部导航栏", icon="layout")
        self.sidebar.add_submenu_item(sub_nav, "navmisc", "面包屑与标签页等", icon="tabs")
        
        sub_form = self.sidebar.add_submenu("表单组件", icon="textbox")
        self.sidebar.add_submenu_item(sub_form, "form", "开关、滑块与日期", icon="sliders")
        self.sidebar.add_submenu_item(sub_form, "authscreen", "Auth 登录与注册", icon="user")
        self.sidebar.add_submenu_item(sub_form, "upload", "Upload 上传组件", icon="upload-simple")
        
        sub_data = self.sidebar.add_submenu("数据展示", icon="table")
        self.sidebar.add_submenu_item(sub_data, "data", "头像展示 (Avatar)", icon="user-circle")
        self.sidebar.add_submenu_item(sub_data, "pro_table", "ProTable 数据表格", icon="table")
        self.sidebar.add_submenu_item(sub_data, "image_compare", "图像对比 Slider", icon="images")
        self.sidebar.add_submenu_item(sub_data, "image_split", "图像分屏 Split", icon="columns")
        self.sidebar.add_submenu_item(sub_data, "console", "控制台日志 Console", icon="terminal-window")
        
        sub_feedback = self.sidebar.add_submenu("反馈组件", icon="bell")
        self.sidebar.add_submenu_item(sub_feedback, "feedback", "信息提示与进度", icon="chat-circle-dots")
        
        sub_layout = self.sidebar.add_submenu("窗口与布局", icon="browsers")
        self.sidebar.add_submenu_item(sub_layout, "window", "Window 自定义窗口", icon="app-window")
        
        self.main_layout.addWidget(self.sidebar)
        
        # --- 2. 创建右侧整体容器 (参考 mainui.py) ---
        self.right_widget = MkQWidget(role="transparent", layout="v", margins=20, spacing=0)
        self.right_widget.setObjectName("MainRightWidget")
        self.right_layout = self.right_widget.inner_layout
        
        # 主体内容区 (MkStackedWidget)
        self.content_area = MkStackedWidget()
        self.content_area.setObjectName("MainContentArea")
        
        # 页面按需惰性工厂
        self._page_factories = {
            "btn": ("page_button", ButtonGallery),
            "chk": ("page_checkbox", CheckboxGallery),
            "topbar": ("page_topbar", TopbarGallery),
            "navmisc": ("page_navmisc", NavMiscGallery),
            "feedback": ("page_feedback", FeedbackGallery),
            "form": ("page_form", FormGallery),
            "authscreen": ("page_auth", AuthGallery),
            "data": ("page_data", DataGallery),
            "pro_table": ("page_pro_table", ProTableGallery),
            "image_compare": ("page_image_compare", ImageCompareGallery),
            "image_split": ("page_image_split", ImageSplitGallery),
            "console": ("page_console", ConsoleGallery),
            "window": ("page_window", WindowGallery),
            "upload": ("page_upload", UploadGallery),
        }
        self._pages = {}
        for attribute, _factory in self._page_factories.values():
            setattr(self, attribute, None)
        self.page_empty = MkQWidget(role="transparent")
        self.content_area.addWidget(self.page_empty)
        
        self.right_layout.addWidget(self.content_area, stretch=1)
        self.main_layout.addWidget(self.right_widget, stretch=1)
        
        # --- 3. 连接信号，实现点击侧边栏切换页面 ---
        self.sidebar.itemClicked.connect(self.switch_page)
        
        # 默认选中第一项
        self.sidebar.set_active("btn")
        self.switch_page("btn")
        
        # 注册中央部件
        self.setCentralWidget(self.central_widget)

    def _setup_theme_selector(self):
        """在标题栏加入 MonkeyQt 默认样式 + 68 种 UI 风格切换"""
        self.theme_selector = MkThemeSelector()
        self.titlebar.center_layout.addStretch()
        self.titlebar.center_layout.addWidget(self.theme_selector)
        self.titlebar.center_layout.addStretch()

    def switch_page(self, item_id):
        """页面切换，无需任何手工样式覆盖，完全由 MonkeyQt 原生驱动"""
        if item_id == "collapse":
            self.sidebar.toggle_collapse()
            return
            
        page_spec = self._page_factories.get(item_id)
        if page_spec is None:
            self.content_area.setCurrentWidget(self.page_empty)
            return

        page = self._pages.get(item_id)
        if page is None:
            attribute, factory = page_spec
            page = factory()
            self._pages[item_id] = page
            setattr(self, attribute, page)
            self.content_area.addWidget(page)
            if ThemeEngine.current_theme():
                apply_monkeyqt_theme(page)

        self.content_area.setCurrentWidget(page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    use_theme("雅致亮色")
    window = MainGallery()
    window.show()
    sys.exit(app.exec())
