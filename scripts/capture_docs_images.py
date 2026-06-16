import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QTableWidgetItem
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from monkeyqt import (
    MkButton, MkCheckBox, MkInput, MkSwitch, MkSlider, 
    MkAlert, MkProgressBar, MkProgressRing, MkAvatar,
    MkComboBox, MkMultiComboBox, MkDatePicker, MkUpload, MkTable, MkDataTable,
    MkMenu, MkTopbar, MkBreadcrumb, MkTabs, MkPagination, MkDropdown, MkWindow
)

def capture_widget(widget, filename, padding=20, bg_color="#ffffff"):
    """
    Wraps the widget in a stylized frame and captures a screenshot.
    """
    # Create wrapper frame
    frame = QFrame()
    frame.setObjectName("DocPreviewContainer")
    frame.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    
    # Simple styling: card layout with background and rounded corners
    frame.setStyleSheet(f"""
        QFrame#DocPreviewContainer {{
            background-color: {bg_color};
            border: 1px solid #e4e4e7;
            border-radius: 8px;
        }}
    """)
    
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(padding, padding, padding, padding)
    layout.addWidget(widget)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    # Realize widget
    frame.show()
    # Force layout and size recalculations by spinning the event loop multiple times
    for _ in range(10):
        QApplication.processEvents()
    frame.adjustSize()
    for _ in range(10):
        QApplication.processEvents()
    
    # Grab screenshot
    pixmap = frame.grab()
    
    # Ensure folder exists
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docs-site/docs/assets/images"))
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    pixmap.save(filepath, "PNG")
    print(f"Saved: {filepath}")
    frame.close()

def main():
    app = QApplication(sys.argv)
    
    # 1. Button Group Preview
    btn_container = QWidget()
    btn_layout = QHBoxLayout(btn_container)
    btn_layout.setContentsMargins(0, 0, 0, 0)
    btn_layout.setSpacing(10)
    btn_layout.addWidget(MkButton("Default", type="default"))
    btn_layout.addWidget(MkButton("Primary", type="primary"))
    btn_layout.addWidget(MkButton("Success", type="success"))
    btn_layout.addWidget(MkButton("Danger", type="danger"))
    capture_widget(btn_container, "button_preview.png")
    
    # 2. CheckBox Preview
    cb = MkCheckBox("已勾选复选框")
    cb.setChecked(True)
    capture_widget(cb, "checkbox_preview.png")
    
    # 3. Input Preview
    inp = MkInput(placeholder="请输入密码...")
    inp.setEchoMode(MkInput.EchoMode.Password)
    inp.setFixedWidth(260)
    capture_widget(inp, "input_preview.png")
    
    # 4. Switch Preview
    sw = MkSwitch(checked=True)
    capture_widget(sw, "switch_preview.png")
    
    # 5. Alert Preview
    alert = MkAlert(title="温馨提示", description="这是由 QPainter 自绘的现代化警告框组件。", mk_type="success", show_icon=True)
    alert.setFixedWidth(400)
    capture_widget(alert, "alert_preview.png")
    
    # 6. Progress Bar Preview
    pb = MkProgressBar(percentage=70, status="success", stroke_width=8)
    pb.setFixedWidth(300)
    capture_widget(pb, "progress_bar_preview.png")
    
    # 7. Progress Ring Preview
    pr = MkProgressRing(percentage=75, status="warning", width=100)
    capture_widget(pr, "progress_ring_preview.png")
    
    # 8. Avatar Preview
    avatar_container = QWidget()
    avatar_layout = QHBoxLayout(avatar_container)
    avatar_layout.setContentsMargins(0, 0, 0, 0)
    avatar_layout.setSpacing(10)
    avatar_layout.addWidget(MkAvatar(text="UI"))
    avatar_layout.addWidget(MkAvatar(text="MK", shape="square"))
    capture_widget(avatar_container, "avatar_preview.png")

    # 9. Slider Preview
    slider = MkSlider(Qt.Horizontal)
    slider.setFixedWidth(260)
    slider.slider.setValue(45)
    capture_widget(slider, "slider_preview.png")

    # 10. ComboBox Preview
    combo = MkComboBox()
    combo.setFixedWidth(200)
    combo.addItems(["选项一", "选项二", "选项三"])
    capture_widget(combo, "combobox_preview.png")

    # 11. MultiComboBox Preview
    multi_container = QWidget()
    multi_layout = QVBoxLayout(multi_container)
    multi_layout.setContentsMargins(0, 0, 0, 0)
    multi_layout.setSpacing(10)

    multi = MkMultiComboBox()
    multi.setFixedWidth(280)
    multi.addItem("黄金会员", "gold")
    multi.addItem("白银会员", "silver")
    multi.addItem("青铜会员", "bronze")
    multi.popup.items[0][2].setChecked(True)
    multi._update_text()

    multi.popup.setParent(multi_container)
    multi.popup.setWindowFlags(Qt.Widget)
    multi.popup.setFixedHeight(120)
    multi.popup.show()

    multi_layout.addWidget(multi)
    multi_layout.addWidget(multi.popup)
    capture_widget(multi_container, "multicombobox_preview.png")

    # 12. DatePicker Preview
    picker_container = QWidget()
    picker_layout = QVBoxLayout(picker_container)
    picker_layout.setContentsMargins(0, 0, 0, 0)
    picker_layout.setSpacing(10)

    picker = MkDatePicker()
    picker.setFixedWidth(280)
    picker.setText("2026-06-04 12:00")

    from monkeyqt.components.form.date_picker import ModernDateTimePopup
    popup = ModernDateTimePopup(parent=picker_container, target_widget=None, current_datetime=picker.current_dt)
    popup.setWindowFlags(Qt.Widget)
    popup.container.setGraphicsEffect(None)
    popup.show()

    picker_layout.addWidget(picker)
    picker_layout.addWidget(popup)
    capture_widget(picker_container, "datepicker_preview.png")

    # 13. Upload Preview
    upload = MkUpload(tip_text="请拖拽文件到此处，或点击选择文件")
    upload.setFixedWidth(360)
    capture_widget(upload, "upload_preview.png")

    # 14. Table Preview
    table = MkTable(3, 3)
    table.set_headers(["姓名", "角色", "状态"])
    table.setItem(0, 0, QTableWidgetItem("张三"))
    table.setItem(0, 1, QTableWidgetItem("管理员"))
    table.setItem(0, 2, QTableWidgetItem("正常"))
    table.setItem(1, 0, QTableWidgetItem("李四"))
    table.setItem(1, 1, QTableWidgetItem("分析师"))
    table.setItem(1, 2, QTableWidgetItem("禁用"))
    table.setItem(2, 0, QTableWidgetItem("王五"))
    table.setItem(2, 1, QTableWidgetItem("运维"))
    table.setItem(2, 2, QTableWidgetItem("正常"))
    table.setFixedWidth(320)
    table.setFixedHeight(160)
    capture_widget(table, "table_preview.png")

    # 15. DataTable Preview
    gallery_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gallery"))
    before_path = os.path.join(gallery_dir, "assets", "before.png")
    after_path = os.path.join(gallery_dir, "assets", "after.png")
    video_path = os.path.join(gallery_dir, "assets", "demo_video.mp4")

    columns = [
        {"key": "date", "label": "录入日期", "width": 120},
        {"key": "name", "label": "操作人", "width": 80},
        {"key": "avatar", "label": "结果图片", "type": "image", "width": 80},
        {"key": "video", "label": "演示视频", "type": "video", "width": 80},
        {"key": "status", "label": "状态"},
        {"key": "action", "label": "操作", "type": "action", "width": 100}
    ]
    data = [
        {"id": "101", "date": "2026-06-01", "name": "王小虎", "avatar": before_path, "video": video_path, "status": "进行中"},
        {"id": "102", "date": "2026-06-02", "name": "李二狗", "avatar": after_path, "video": video_path, "status": "已完成"},
        {"id": "103", "date": "2026-06-03", "name": "张三疯", "avatar": before_path, "video": video_path, "status": "已完成"}
    ]
    data_table = MkDataTable(columns=columns, data=data, page_size=5, selection_enabled=True)
    data_table.setFixedWidth(680)
    data_table.setFixedHeight(320)
    data_table._selected_keys.add("101")
    data_table.refresh_table()
    capture_widget(data_table, "datatable_preview.png")

    # 16. Menu Preview
    menu = MkMenu(title="控制台", icon="house")
    menu.setFixedWidth(200)
    menu.setFixedHeight(280)
    menu.add_item("dashboard", "仪表盘", icon="chart-bar")
    sub = menu.add_submenu("用户管理", icon="user")
    menu.add_submenu_item(sub, "user-list", "用户列表", icon="file")
    menu.set_active("dashboard")
    capture_widget(menu, "menu_preview.png", padding=10)

    # 17. Topbar Preview
    topbar = MkTopbar(logo_text="MonkeyQt")
    topbar.add_item("home", "首页")
    topbar.add_item("workspace", "工作台")
    topbar.add_item("settings", "设置")
    topbar.set_active("home")
    topbar.setFixedWidth(450)
    capture_widget(topbar, "topbar_preview.png", padding=10)

    # 18. Breadcrumb Preview
    breadcrumb = MkBreadcrumb(separator=">")
    breadcrumb.set_items([
        {"id": "home", "text": "首页"},
        {"id": "components", "text": "导航"},
        {"id": "breadcrumb", "text": "面包屑"}
    ])
    breadcrumb.setFixedWidth(260)
    capture_widget(breadcrumb, "breadcrumb_preview.png")

    # 19. Tabs Preview
    tabs = MkTabs()
    tabs.setFixedWidth(320)
    tabs.setFixedHeight(120)
    tabs.add_tab("tab1", "用户管理", QFrame())
    tabs.add_tab("tab2", "配置管理", QFrame())
    capture_widget(tabs, "tabs_preview.png")

    # 20. Pagination Preview
    pagination = MkPagination(total=100, page_size=10, current=3)
    pagination.setFixedWidth(380)
    capture_widget(pagination, "pagination_preview.png")

    # 21. Dropdown Preview
    dropdown = MkDropdown("操作菜单")
    dropdown.add_item("新增", "add")
    dropdown.add_item("编辑", "edit")
    dropdown.add_separator()
    dropdown.add_item("删除", "delete")
    dropdown.setFixedWidth(120)
    capture_widget(dropdown, "dropdown_preview.png")

    # 22. Window Preview
    win = MkWindow(use_custom_title_bar=True, preset="default")
    win.setWindowTitle("自定义窗口")
    win.setCentralWidget(QFrame())
    win.setFixedSize(400, 250)
    win.show()
    for _ in range(10):
        QApplication.processEvents()
    pixmap = win.grab()
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docs-site/docs/assets/images"))
    filepath = os.path.join(output_dir, "window_preview.png")
    pixmap.save(filepath, "PNG")
    print(f"Saved: {filepath}")
    win.close()

    # 23. Titlebar Extras & Profile Page Previews
    from test_titlebar_extras import TestApp
    win_extras = TestApp()
    win_extras.setFixedSize(1100, 750)
    win_extras.show()
    for _ in range(30):
        QApplication.processEvents()
        
    # Capture Titlebar Extras (Home Page Active)
    filepath_extras = os.path.join(output_dir, "titlebar_extras_preview.png")
    win_extras.grab().save(filepath_extras, "PNG")
    print(f"Saved: {filepath_extras}")
    
    # Navigate to profile page
    if win_extras.titlebar_history_nav:
        win_extras.titlebar_history_nav.navigate("profile")
    else:
        win_extras.content_area.setCurrentWidget(win_extras.page_profile)
        
    for _ in range(30):
        QApplication.processEvents()
        
    # Capture Profile Page Preview
    filepath_profile = os.path.join(output_dir, "profile_page_preview.png")
    win_extras.grab().save(filepath_profile, "PNG")
    print(f"Saved: {filepath_profile}")
    
    win_extras.close()

if __name__ == "__main__":
    main()
