from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QFrame
from PySide6.QtCore import Qt, Signal
from monkeyqt import MkButton, MkUpload, MkSlider, MkImageSplit, MkComboBox, MkCheckBox, MkMultiComboBox
from monkeyqt.core.icons import MkPhosphorIcon

class YoloDashboardWidget(QWidget):
    classSelectionChanged = Signal(list)
    
    def __init__(self, conf=0.25, iou=0.45, parent=None):
        super().__init__(parent)
        self.conf = conf
        self.iou = iou
        self._setup_ui()

    def _setup_ui(self):
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(15)
        
        # 1. 顶部标题 & 描述
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)
        
        title_label = QLabel("YOLO26/11/v8 目标检测系统")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e293b;")
        header_layout.addWidget(title_label)
        
        desc_label = QLabel("支持图片、视频文件和本地摄像头实时推理。")
        desc_label.setStyleSheet("font-size: 13px; color: #64748b;")
        header_layout.addWidget(desc_label)
        page_layout.addWidget(header_widget)
        
        # 2. 主页面内容区域（水平分割：左控制面板，右显示区域）
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)
        
        # --- 左侧卡片式控制面板 (Width: 320px) ---
        self.ctrl_panel = QFrame()
        self.ctrl_panel.setObjectName("ctrl_panel")
        self.ctrl_panel.setFixedWidth(320)
        self.ctrl_panel.setStyleSheet("""
            QFrame#ctrl_panel {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QLabel {
                border: none;
                background: transparent;
                font-family: "Microsoft YaHei", sans-serif;
            }
        """)
        ctrl_layout = QVBoxLayout(self.ctrl_panel)
        ctrl_layout.setContentsMargins(15, 20, 15, 20)
        ctrl_layout.setSpacing(15)
        
        # A. 检测模式按钮切换组
        mode_title = QLabel("检测输入源模式")
        mode_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #334155; margin-top: 5px;")
        ctrl_layout.addWidget(mode_title)
        
        mode_btn_layout = QHBoxLayout()
        mode_btn_layout.setSpacing(6)
        
        self.btn_mode_img = MkButton("图片检测", type="primary")
        self.btn_mode_video = MkButton("视频检测", type="default")
        self.btn_mode_cam = MkButton("摄像头", type="default")
        
        for btn in [self.btn_mode_img, self.btn_mode_video, self.btn_mode_cam]:
            mode_btn_layout.addWidget(btn, stretch=1)
        
        ctrl_layout.addLayout(mode_btn_layout)
        
        # B. 模型与参数微调
        param_title = QLabel("模型与参数配置")
        param_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #334155;")
        ctrl_layout.addWidget(param_title)
        
        # Model Selection dropdown
        model_layout = QHBoxLayout()
        model_layout.setSpacing(6)
        
        self.model_combo = MkComboBox()
        self.model_combo.addItems(["yolov8n.pt", "yolov8s.pt", "yolov8m.pt"])
        model_layout.addWidget(self.model_combo, stretch=1)
        
        self.btn_browse_model = MkButton("浏览", type="default", size="small")
        model_layout.addWidget(self.btn_browse_model)
        
        ctrl_layout.addLayout(model_layout)
        
        # Confidence Threshold Slider
        self.lbl_conf = QLabel("置信度阈值 (Conf)")
        self.lbl_conf.setStyleSheet("color: #475569; font-size: 12px; font-weight: bold;")
        ctrl_layout.addWidget(self.lbl_conf)
        
        self.slider_conf = MkSlider(Qt.Horizontal)
        self.slider_conf.setRange(5, 100)
        self.slider_conf.setValue(int(self.conf * 100))
        self.slider_conf.set_formatter(lambda val: f"{val / 100:.2f}")
        ctrl_layout.addWidget(self.slider_conf)
        
        # IoU Threshold Slider
        self.lbl_iou = QLabel("非极大值抑制 (IoU)")
        self.lbl_iou.setStyleSheet("color: #475569; font-size: 12px; font-weight: bold;")
        ctrl_layout.addWidget(self.lbl_iou)
        
        self.slider_iou = MkSlider(Qt.Horizontal)
        self.slider_iou.setRange(5, 100)
        self.slider_iou.setValue(int(self.iou * 100))
        self.slider_iou.set_formatter(lambda val: f"{val / 100:.2f}")
        ctrl_layout.addWidget(self.slider_iou)
        
        # C. 类别过滤
        class_title_layout = QHBoxLayout()
        class_title_layout.setContentsMargins(0, 0, 0, 0)
        class_title_layout.setSpacing(6)
        
        class_title = QLabel("类别过滤")
        class_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #334155;")
        class_title_layout.addWidget(class_title)
        
        class_title_layout.addStretch()
        
        self.btn_clear_classes = MkButton("重置", type="text", size="small")
        self.btn_clear_classes.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_classes.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #3b82f6;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 12px;
                font-weight: 500;
                padding: 0px;
            }
            QPushButton:hover {
                color: #1d4ed8;
                text-decoration: underline;
            }
            QPushButton:pressed {
                color: #1e3a8a;
            }
        """)
        self.btn_clear_classes.clicked.connect(self.clear_selected_classes)
        class_title_layout.addWidget(self.btn_clear_classes)
        ctrl_layout.addLayout(class_title_layout)
        
        # Multi-select dropdown
        self.class_combo = MkMultiComboBox()
        self.class_combo.selectionChanged.connect(self._on_class_checkbox_changed)
        ctrl_layout.addWidget(self.class_combo)
        
        class_tip = QLabel("选择需要预测的类别，留空就是预测所有类别。")
        class_tip.setStyleSheet("font-size: 11px; color: #64748b; margin-top: 2px;")
        ctrl_layout.addWidget(class_tip)
        
        # D. 媒体输入容器 (QStackedWidget)
        input_title = QLabel("媒体源配置")
        input_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #334155;")
        ctrl_layout.addWidget(input_title)
        
        self.input_stack = QStackedWidget()
        self.input_stack.setStyleSheet("QStackedWidget { border: none; background: transparent; }")
        
        # Page 0: Image Upload
        self.upload_img = MkUpload(
            multiple=False, 
            accept_filters=["*.png", "*.jpg", "*.jpeg", "*.bmp"], 
            max_size_mb=20, 
            tip_text="拖入或点击上传原图，不超过 20MB"
        )
        self.input_stack.addWidget(self.upload_img)
        
        # Page 1: Video Upload
        self.upload_video = MkUpload(
            multiple=False, 
            accept_filters=["*.mp4", "*.avi", "*.mkv", "*.mov"], 
            max_size_mb=100, 
            tip_text="拖入或点击上传视频，不超过 100MB"
        )
        self.input_stack.addWidget(self.upload_video)
        
        # Page 2: Camera Selector
        self.cam_panel = QWidget()
        self.cam_panel.setObjectName("cam_panel")
        self.cam_panel.setStyleSheet("""
            QWidget#cam_panel {
                background-color: #f8fafc;
                border: 1px dashed #cbd5e1;
                border-radius: 8px;
            }
        """)
        
        cam_layout = QVBoxLayout(self.cam_panel)
        cam_layout.setContentsMargins(15, 15, 15, 15)
        cam_layout.setSpacing(12)
        
        # 1. Header Row
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        
        self.cam_icon = QLabel()
        self.cam_icon.setObjectName("dashboard_cam_icon")
        self.cam_icon.setPixmap(MkPhosphorIcon.get_pixmap("video-camera", "#3b82f6", 18))
        header_row.addWidget(self.cam_icon)
        
        cam_title = QLabel("本地摄像头检测")
        cam_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b; border: none; background: transparent;")
        header_row.addWidget(cam_title)
        
        header_row.addStretch()
        
        # Online status badge
        self.status_dot = QLabel()
        self.status_dot.setObjectName("dashboard_status_dot")
        self.status_dot.setFixedSize(6, 6)
        self.status_dot.setStyleSheet("background-color: #22c55e; border-radius: 3px;")
        header_row.addWidget(self.status_dot)
        
        status_text = QLabel("Online")
        status_text.setStyleSheet("color: #22c55e; font-size: 11px; font-weight: bold; border: none; background: transparent;")
        header_row.addWidget(status_text)
        
        cam_layout.addLayout(header_row)
        
        # 2. Subtitle / Tip
        cam_tip = QLabel("检测并读取您本地连接的 USB 摄像头设备进行实时目标识别。")
        cam_tip.setWordWrap(True)
        cam_tip.setStyleSheet("color: #64748b; font-size: 11px; line-height: 14px; border: none; background: transparent;")
        cam_layout.addWidget(cam_tip)
        
        # 3. ComboBox Selection Group
        select_group = QWidget()
        select_group.setStyleSheet("border: none; background: transparent;")
        select_group_layout = QVBoxLayout(select_group)
        select_group_layout.setContentsMargins(0, 0, 0, 0)
        select_group_layout.setSpacing(4)
        
        select_lbl = QLabel("可用的视频输入源:")
        select_lbl.setStyleSheet("color: #475569; font-size: 11px; font-weight: 500; border: none; background: transparent;")
        select_group_layout.addWidget(select_lbl)
        
        cam_row = QHBoxLayout()
        cam_row.setSpacing(6)
        self.camera_combo = MkComboBox()
        cam_row.addWidget(self.camera_combo, stretch=1)
        self.btn_refresh_cam = MkButton("刷新", type="default", size="small")
        cam_row.addWidget(self.btn_refresh_cam)
        select_group_layout.addLayout(cam_row)
        cam_layout.addWidget(select_group)
        
        # 4. Device Specs Card
        self.specs_card = QFrame()
        self.specs_card.setObjectName("specs_card")
        self.specs_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        specs_layout = QVBoxLayout(self.specs_card)
        specs_layout.setContentsMargins(10, 10, 10, 10)
        specs_layout.setSpacing(6)
        
        spec1 = QLabel("📡 状态: 设备已就绪")
        spec1.setStyleSheet("color: #334155; font-size: 11px;")
        spec2 = QLabel("⚙️ 格式: OpenCV DirectShow")
        spec2.setStyleSheet("color: #334155; font-size: 11px;")
        spec3 = QLabel("⏱️ 帧率: 约 30 帧/秒")
        spec3.setStyleSheet("color: #334155; font-size: 11px;")
        
        specs_layout.addWidget(spec1)
        specs_layout.addWidget(spec2)
        specs_layout.addWidget(spec3)
        cam_layout.addWidget(self.specs_card)
        
        self.input_stack.addWidget(self.cam_panel)
        ctrl_layout.addWidget(self.input_stack)
        
        # E. 开始检测与视频播放控制按钮
        ctrl_layout.addSpacing(10)
        self.btn_detect_run = MkButton("开始 YOLO 推理 ", type="primary")
        self.btn_detect_run.setFixedHeight(38)
        ctrl_layout.addWidget(self.btn_detect_run)
        
        # Video controls (Pause, Resume, Stop)
        self.video_ctrl_widget = QWidget()
        self.video_ctrl_widget.setStyleSheet("border: none; background: transparent;")
        video_ctrl_layout = QHBoxLayout(self.video_ctrl_widget)
        video_ctrl_layout.setContentsMargins(0, 0, 0, 0)
        video_ctrl_layout.setSpacing(8)
        
        self.btn_pause = MkButton("暂停检测", type="warning")
        self.btn_resume = MkButton("继续检测", type="success")
        self.btn_stop = MkButton("结束检测", type="danger")
        
        video_ctrl_layout.addWidget(self.btn_pause)
        video_ctrl_layout.addWidget(self.btn_resume)
        video_ctrl_layout.addWidget(self.btn_stop)
        self.video_ctrl_widget.setVisible(False)
        ctrl_layout.addWidget(self.video_ctrl_widget)
        
        # F. 推理状态和日志监控区
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(QLabel("状态日志"))
        self.lbl_status = QLabel("状态: 准备就绪")
        self.lbl_status.setObjectName("dashboard_status")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet("""
            QLabel {
                font-family: Consolas;
                font-size: 11px;
                color: #64748b;
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        ctrl_layout.addWidget(self.lbl_status)
        
        # --- 左侧图像对比分屏展示区 (Width: Stretch) ---
        self.split_view = MkImageSplit()
        self.split_view.set_labels("输入源画面", "检测结果")
        self.split_view.setMinimumSize(400, 300)
        
        # Display area container for better styling
        self.display_frame = QFrame()
        self.display_frame.setObjectName("display_frame")
        self.display_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        display_layout = QVBoxLayout(self.display_frame)
        display_layout.setContentsMargins(10, 10, 10, 10)
        display_layout.addWidget(self.split_view)
        
        split_layout.addWidget(self.display_frame, stretch=1)
        
        # --- 右侧卡片式控制面板 (Width: 320px) ---
        split_layout.addWidget(self.ctrl_panel)
        
        page_layout.addLayout(split_layout)

    def update_class_list(self, class_dict):
        """Dynamically update the checkboxes inside multicombobox based on loaded model classes."""
        self.class_combo.clear()
        if class_dict:
            self.class_combo.addItems(class_dict)

    def _on_class_checkbox_changed(self):
        """Emit custom signal with selected class IDs when state changes."""
        selected = self.get_selected_classes()
        self.classSelectionChanged.emit(selected)

    def get_selected_classes(self):
        """Return list of selected class integer IDs."""
        return self.class_combo.get_checked_data()

    def clear_selected_classes(self):
        """Uncheck all classes."""
        self.class_combo.clear_checked()
