# -*- coding: utf-8 -*- 
""" 
@Auth ：落花不写码 
@File ：mainui.py 
@Motto :学习新思想，争做新青年 
""" 
import sys 
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ["OPENCV_LOG_LEVEL"] = "OFF"
import cv2

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget,
    QFrame, QFileDialog, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QImage, QIcon, QFont
from monkeyqt import MkMenu, MkWindow, MkMessage, use_theme, MkSwitch, MkSlider, MkButton, MkAvatar, ThemeEngine
from monkeyqt.core.icons import MkPhosphorIcon
from core.yolo_predictor import YoloPredictor, YoloThread
from core.camera_scanner import CameraScanner
from ui.yolo_dashboard import YoloDashboardWidget
from ui.profile_page import ProfilePageWidget
from ui.settings_page import SettingsPageWidget


class QuickStartApp(MkWindow): 
    def __init__(self): 
        super().__init__(
            use_custom_title_bar=True,
            preset="default",
            sidebar_full_height=True,
        ) 
        
        # YOLO inference variables
        self.yolo_thread = None
        self.current_mode = "image"  # "image", "video", or "camera"
        self.model_path = ""
        self.input_source = None
        self.conf = 0.25
        self.iou = 0.45
        self.current_classes = None
        self.model_cache = {}
        
        # 自定义标题栏：高度加高，移除下边框线
        self.titlebar._height = 48
        self.titlebar._border_bottom = "none"
        self.titlebar.apply_theme_colors()
        self.titlebar.rebuild_layout()
        self.update_style()
        
        # self.setWindowTitle("基于MonkeyUI通用的YOLO目标检测系统")
        self.resize(1500, 1000)
        
        # --- 创建主布局（左右结构） ---
        # 使用 QHBoxLayout（水平布局）
        # 左侧放侧边栏(MkMenu)，右侧放内容区(QStackedWidget)
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 去掉窗口周围的空白边距
        self.main_layout.setSpacing(0)                  # 去掉组件之间的空隙

        # --- 创建并配置侧边栏 ---
        # 传入标题、图标和收缩模式
        self.sidebar = MkMenu(title="目标检测系统", collapse_mode="hamburger")
        self.sidebar.set_border_right("none")
        
        # 给侧边栏添加菜单项
        self.sidebar.add_item("home", "首页控制台", icon="house")
        self.sidebar.add_item("data", "推理检测", icon="chart-bar")
        self.sidebar.add_item("settings", "历史记录", icon="gear")
        
        # 将侧边栏加入到主布局的左侧
        self.main_layout.addWidget(self.sidebar)

        # --- 3. 创建右侧整体容器（上下结构） ---
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(20, 20, 20, 20) # 给右侧内容留出舒服的边距
        self.right_layout.setSpacing(20)

        # --- 3.1 底部放置主体内容区 (QStackedWidget) ---
        self.content_area = QStackedWidget()

        # 创建对应的测试页面
        self.page_home = self._create_placeholder_page("这里是首页控制台的内容", "#409eff")
        
        # 实例化封装后的 YOLO 仪表盘视图
        self.dashboard = YoloDashboardWidget(conf=self.conf, iou=self.iou)
        self.page_data = self.dashboard
        
        # Scan weights and populate model dropdown
        self._init_models_list()
        
        self.page_settings = self._create_placeholder_page("这里是系统设置的内容", "#e6a23c")
        
        # 个人主页 (来自 ui 文件夹下的封装)
        self.page_profile = ProfilePageWidget()
        self.page_profile.setObjectName("profile")
        
        # 设置页面 (来自 ui 文件夹下的封装)
        self.page_app_settings = SettingsPageWidget()
        self.page_app_settings.setObjectName("app_settings")
        
        # 绑定信号与槽
        self._setup_dashboard_connections()
        
        # Load initially selected model classes
        self._load_model_classes()

        # 将页面加入到堆叠内容区中
        # 给页面设置 objectName 以便 enable_titlebar_extras 自动映射
        self.page_home.setObjectName("home")
        self.page_data.setObjectName("data")
        self.page_settings.setObjectName("settings")
        
        self.content_area.addWidget(self.page_home)
        self.content_area.addWidget(self.page_data)
        self.content_area.addWidget(self.page_settings)
        self.content_area.addWidget(self.page_profile)
        self.content_area.addWidget(self.page_app_settings)

        # 将堆叠内容区加入到右侧垂直布局中
        self.right_layout.addWidget(self.content_area, stretch=1)

        # 最后，将整个右侧容器加入到主布局的右侧
        self.main_layout.addWidget(self.right_widget, stretch=1)

        # --- 4. 连接信号，实现点击侧边栏切换页面 ---
        self.sidebar.itemClicked.connect(self.on_menu_clicked)
        
        # 将整体页面组件注册为 MkWindow 的中央部件
        self.setCentralWidget(self.central_widget)
        
        # --- 5. 一行代码启用标题栏头像 + 前进后退 ---
        avatar_path = os.path.join(os.path.dirname(__file__), "user_avatar.png")
        self.enable_titlebar_extras(
            avatar=False,
            history_nav=True,
            user_name="落花不写码",
            subtitle="PySide6 组件开发者",
            avatar_image=avatar_path if os.path.exists(avatar_path) else "",
            avatar_size=32,
            nav_icon_only=True,
            avatar_actions=[
                {"id": "profile", "text": "个人主页", "icon": "user"},
                {"id": "settings", "text": "设置", "icon": "gear"},
                {"id": "logout", "text": "退出登录", "icon": "sign-out", "separator_before": True},
            ],
        )
        
        # 绑定头像菜单的动作信号
        if self.titlebar_avatar:
            self.titlebar_avatar.actionTriggered.connect(self._on_avatar_action)
        
        # 绑定历史导航变化信号，同步侧边栏选中状态
        if self.titlebar_history_nav:
            self.titlebar_history_nav.pageChanged.connect(self._on_page_changed)
        
        # 默认选中第一项
        self.sidebar.set_active("home")
        
    def on_menu_clicked(self, item_id):
        """当侧边栏菜单项被点击时触发的函数"""
        if self.titlebar_history_nav:
            # 通过 history_nav 导航以记录历史
            self.titlebar_history_nav.navigate(item_id)
        else:
            # Fallback: 直接切换页面
            if item_id == "home":
                self.content_area.setCurrentWidget(self.page_home)
            elif item_id == "data":
                self.content_area.setCurrentWidget(self.page_data)
            elif item_id == "settings":
                self.content_area.setCurrentWidget(self.page_settings)

    def _on_page_changed(self, page_id):
        """当历史页面（前进/后退）切换时，同步高亮侧边栏对应的菜单项"""
        found = False
        for item in self.sidebar._all_items:
            if item.item_id == page_id:
                item.setChecked(True)
                for other in self.sidebar._all_items:
                    if other != item:
                        other.setChecked(False)
                found = True
                break
        if not found:
            # 说明跳转到了非侧边栏页面（如个人主页、系统设置等），清除侧边栏所有的选中高亮
            for item in self.sidebar._all_items:
                item.setChecked(False)

    def _on_avatar_action(self, action_id):
        """头像菜单点击回调"""
        if action_id == "profile":
            if self.titlebar_history_nav:
                self.titlebar_history_nav.navigate("profile")
            else:
                self.content_area.setCurrentWidget(self.page_profile)
        elif action_id == "settings":
            if self.titlebar_history_nav:
                self.titlebar_history_nav.navigate("app_settings")
            else:
                self.content_area.setCurrentWidget(self.page_app_settings)
        elif action_id == "logout":
            MkMessage.success(self, "账号已安全登出！")

    def _setup_dashboard_connections(self):
        # 模式切换
        self.dashboard.btn_mode_img.clicked.connect(lambda: self._on_mode_changed("image"))
        self.dashboard.btn_mode_video.clicked.connect(lambda: self._on_mode_changed("video"))
        self.dashboard.btn_mode_cam.clicked.connect(lambda: self._on_mode_changed("camera"))
        
        # 模型选择与浏览
        self.dashboard.model_combo.currentIndexChanged.connect(self._on_model_changed)
        self.dashboard.btn_browse_model.clicked.connect(self._on_browse_model)
        
        # 类别过滤信号
        self.dashboard.classSelectionChanged.connect(self._on_class_selection_changed)
        
        # 阈值滑块
        self.dashboard.slider_conf.valueChanged.connect(self._on_conf_changed)
        self.dashboard.slider_iou.valueChanged.connect(self._on_iou_changed)
        
        # 媒体文件上传
        self.dashboard.upload_img.filesSelected.connect(self._on_image_selected)
        self.dashboard.upload_video.filesSelected.connect(self._on_video_selected)
        
        # 摄像头刷新与推理触发
        self.dashboard.btn_refresh_cam.clicked.connect(self._scan_cameras)
        self.dashboard.btn_detect_run.clicked.connect(self._on_start_detection)
        
        # 视频控制
        self.dashboard.btn_pause.clicked.connect(self._on_pause_detection)
        self.dashboard.btn_resume.clicked.connect(self._on_resume_detection)
        self.dashboard.btn_stop.clicked.connect(self._on_stop_detection)

    # --- Mode Switch & Settings Slots ---
    def _on_mode_changed(self, mode: str):
        self._on_stop_detection()
        self.current_mode = mode
        self.input_source = None
        self.dashboard.split_view.set_images(None, None)
        
        # Set button type property dynamically
        self.dashboard.btn_mode_img.mk_type = "primary" if mode == "image" else "default"
        self.dashboard.btn_mode_video.mk_type = "primary" if mode == "video" else "default"
        self.dashboard.btn_mode_cam.mk_type = "primary" if mode == "camera" else "default"
            
        if mode == "image":
            self.dashboard.input_stack.setCurrentIndex(0)
            self.dashboard.upload_img.clear()
            self.dashboard.lbl_status.setText("状态: 请上传一张图片进行检测")
        elif mode == "video":
            self.dashboard.input_stack.setCurrentIndex(1)
            self.dashboard.upload_video.clear()
            self.dashboard.lbl_status.setText("状态: 请上传一个视频进行检测")
        elif mode == "camera":
            self.dashboard.input_stack.setCurrentIndex(2)
            self._scan_cameras()
            self.dashboard.lbl_status.setText("状态: 请选择摄像头并点击开始检测")

    def _on_model_changed(self, index: int):
        if index < 0:
            return
        data = self.dashboard.model_combo.itemData(index)
        if data == "custom":
            self._on_browse_model()
        else:
            self.model_path = data
            self.dashboard.lbl_status.setText(f"状态: 选择模型 {os.path.basename(self.model_path)}")
            self._load_model_classes()

    def _on_browse_model(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 YOLOv8 模型", "", "PyTorch Models (*.pt)")
        if file_path:
            file_path = os.path.normpath(file_path)
            # Check if model already exists in combobox
            idx = -1
            for i in range(self.dashboard.model_combo.count()):
                if self.dashboard.model_combo.itemData(i) == file_path:
                    idx = i
                    break
            if idx == -1:
                # Add and select it
                filename = os.path.basename(file_path)
                self.dashboard.model_combo.insertItem(self.dashboard.model_combo.count() - 1, filename, file_path)
                idx = self.dashboard.model_combo.count() - 2
                
            self.dashboard.model_combo.setCurrentIndex(idx)
            self.model_path = file_path
            self.dashboard.lbl_status.setText(f"状态: 选择自定义模型 {os.path.basename(file_path)}")
            self._load_model_classes()
        else:
            # Reset back to default
            self.dashboard.model_combo.setCurrentIndex(0)

    def _on_conf_changed(self, val: int):
        self.conf = val / 100.0
        if self.yolo_thread:
            self.yolo_thread.conf = self.conf

    def _on_iou_changed(self, val: int):
        self.iou = val / 100.0
        if self.yolo_thread:
            self.yolo_thread.iou = self.iou

    def _scan_cameras(self):
        self.dashboard.lbl_status.setText("状态: 正在扫描系统可用摄像头...")
        self.dashboard.camera_combo.clear()
        cameras = CameraScanner.get_available_cameras()
        if cameras:
            for idx in cameras:
                self.dashboard.camera_combo.addItem(f"摄像头 #{idx}", idx)
            self.dashboard.btn_detect_run.setEnabled(True)
            self.dashboard.lbl_status.setText(f"状态: 扫描完成，发现 {len(cameras)} 个可用设备")
        else:
            self.dashboard.camera_combo.addItem("未检测到可用摄像头", -1)
            self.dashboard.btn_detect_run.setEnabled(False)
            self.dashboard.lbl_status.setText("警告: 未在您的系统上找到任何可用摄像头")

    # --- Media Selection Callbacks ---
    def _on_image_selected(self, files: list):
        if files:
            self.input_source = files[0]
            # Center the image inside the split view and hide handle
            self.dashboard.split_view.set_images(files[0], None)
            self.dashboard.lbl_status.setText(f"状态: 图片上传完成: {os.path.basename(files[0])}，等待检测")
        else:
            self.input_source = None
            self.dashboard.split_view.set_images(None, None)

    def _on_video_selected(self, files: list):
        if files:
            self.input_source = files[0]
            # Extract and display the first frame in split view
            cap = cv2.VideoCapture(files[0])
            ret, frame = cap.read()
            if ret:
                q_img = YoloThread.ndarray_to_qimage(frame)
                self.dashboard.split_view.set_images(q_img, None)
            cap.release()
            self.dashboard.lbl_status.setText(f"状态: 视频上传完成: {os.path.basename(files[0])}，已获取第一帧")
        else:
            self.input_source = None
            self.dashboard.split_view.set_images(None, None)

    # --- Detection Control Slots ---
    def _on_start_detection(self):
        if self.current_mode in ["image", "video"] and not self.input_source:
            MkMessage.error(self, "请先上传输入源文件！")
            return
            
        if self.current_mode == "image":
            self.dashboard.lbl_status.setText("状态: 正在加载模型并进行图像推理...")
            QApplication.processEvents()
            
            try:
                predictor = YoloPredictor(self.model_path)
                q_orig, q_annot = predictor.predict_image(
                    self.input_source, 
                    self.conf, 
                    self.iou, 
                    classes=self.current_classes
                )
                # Animate from single image (1.0 ratio) to 0.5 comparative split view
                self.dashboard.split_view.set_images(q_orig, q_annot)
                self.dashboard.lbl_status.setText("状态: 图像 YOLO 推理检测完成！")
            except Exception as e:
                self.dashboard.lbl_status.setText(f"错误: 推理失败: {str(e)}")
                
        elif self.current_mode in ["video", "camera"]:
            # Set up inputs
            source_val = self.input_source if self.current_mode == "video" else self.dashboard.camera_combo.currentData()
            if self.current_mode == "camera" and source_val == -1:
                return
                
            # Stop existing thread
            self._on_stop_detection()
            
            self.dashboard.lbl_status.setText("状态: 正在初始化 YOLO 推理线程...")
            self.yolo_thread = YoloThread(
                model_path=self.model_path,
                source=source_val,
                mode=self.current_mode,
                conf=self.conf,
                iou=self.iou,
                classes=self.current_classes
            )
            
            # Connect signals
            self.yolo_thread.frameProcessed.connect(self._on_frame_processed)
            self.yolo_thread.statusMessage.connect(self._on_status_message)
            self.yolo_thread.errorOccurred.connect(self._on_error_occurred)
            self.yolo_thread.finishedMessage.connect(self._on_video_finished)
            
            # Start
            self.yolo_thread.start()
            
            # Switch controls state
            self.dashboard.btn_detect_run.setVisible(False)
            self.dashboard.video_ctrl_widget.setVisible(True)
            self.dashboard.btn_pause.setVisible(True)
            self.dashboard.btn_resume.setVisible(False)

    def _on_pause_detection(self):
        if self.yolo_thread:
            self.yolo_thread.pause()
            self.dashboard.btn_pause.setVisible(False)
            self.dashboard.btn_resume.setVisible(True)

    def _on_resume_detection(self):
        if self.yolo_thread:
            self.yolo_thread.resume()
            self.dashboard.btn_resume.setVisible(False)
            self.dashboard.btn_pause.setVisible(True)

    def _on_stop_detection(self):
        if self.yolo_thread:
            # Tell thread to stop and clean up
            self.yolo_thread.stop()
            self.yolo_thread = None
            
        self.dashboard.btn_detect_run.setVisible(True)
        self.dashboard.video_ctrl_widget.setVisible(False)
        self.dashboard.lbl_status.setText("状态: 检测已停止")

    # --- Thread Signal Slots ---
    def _on_frame_processed(self, q_orig: QImage, q_annot: QImage):
        # Set frames to visualizer. If ratio is 1.0 (single view), it will animate to 0.5 compare view
        self.dashboard.split_view.set_images(q_orig, q_annot)

    def _on_status_message(self, msg: str):
        self.dashboard.lbl_status.setText(f"状态: {msg}")

    def _on_error_occurred(self, err: str):
        MkMessage.error(self, err)
        self._on_stop_detection()

    def _on_video_finished(self, msg: str):
        self._on_stop_detection()
        self.dashboard.lbl_status.setText("状态: 视频推理检测播放结束")

    def closeEvent(self, event):
        # Guarantee that threads are stopped and joined before window context vanishes
        if self.yolo_thread:
            self.yolo_thread.stop()
        super().closeEvent(event)

    def _create_placeholder_page(self, text, color):
        """辅助函数：用于创建一个简单的占位页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(text)
        label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page

    def _init_models_list(self):
        """Scan the weights/ folder and populate the model combobox."""
        self.dashboard.model_combo.clear()
        
        # Ensure weights folder exists
        weights_dir = "weights"
        if not os.path.exists(weights_dir):
            os.makedirs(weights_dir)
            
        pt_files = []
        try:
            for f in os.listdir(weights_dir):
                if f.endswith(".pt"):
                    pt_files.append(os.path.join(weights_dir, f))
        except Exception as e:
            print(f"Error scanning weights: {e}")
            
        if pt_files:
            for path in pt_files:
                filename = os.path.basename(path)
                self.dashboard.model_combo.addItem(filename, path)
        else:
            # Fallback defaults if no weights found
            self.dashboard.model_combo.addItem("yolov8n.pt", "yolov8n.pt")
            self.dashboard.model_combo.addItem("yolov8s.pt", "yolov8s.pt")
            self.dashboard.model_combo.addItem("yolov8m.pt", "yolov8m.pt")
            
        self.dashboard.model_combo.addItem("自定义模型...", "custom")
        
        # Initialize default selection
        self.model_path = self.dashboard.model_combo.itemData(0)

    def _load_model_classes(self):
        """Load YOLO model metadata to dynamically display category checklist."""
        if not self.model_path:
            self.dashboard.update_class_list({})
            return
            
        # Check cache
        if self.model_path in self.model_cache:
            self.dashboard.update_class_list(self.model_cache[self.model_path])
            return
            
        self.dashboard.lbl_status.setText("状态: 正在读取模型类别...")
        QApplication.processEvents()
        
        try:
            from ultralytics import YOLO
            # Temporarily load the model to inspect its names
            model = YOLO(self.model_path)
            class_dict = model.names
            
            # Cache it
            self.model_cache[self.model_path] = class_dict
            self.dashboard.update_class_list(class_dict)
            self.dashboard.lbl_status.setText(f"状态: 成功加载模型类别 (共 {len(class_dict)} 类)")
        except Exception as e:
            self.dashboard.update_class_list({})
            self.dashboard.lbl_status.setText(f"错误: 无法获取模型类别: {str(e)}")

    def _on_class_selection_changed(self, selected_classes):
        """Update current active filter classes and update running thread in real-time."""
        self.current_classes = selected_classes if selected_classes else None
        
        # If thread is active, dynamically update classes filter
        if self.yolo_thread:
            self.yolo_thread.classes = self.current_classes
            
        if self.current_classes:
            self.dashboard.lbl_status.setText(f"状态: 过滤类别已更新 ({len(self.current_classes)} 个类别被选中)")
        else:
            self.dashboard.lbl_status.setText("状态: 未选择任何过滤类别，检测所有类别")




if __name__ == "__main__": 
    app = QApplication(sys.argv) 
    use_theme("HUD 科幻界面")
    window = QuickStartApp() 
    window.show() 
    sys.exit(app.exec()) 
