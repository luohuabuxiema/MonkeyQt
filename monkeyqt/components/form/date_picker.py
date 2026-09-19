import sys
from PySide6.QtCore import (Qt, QTime, QDate, QDateTime, QPropertyAnimation, 
                            QEasingCurve, QRectF, Signal, QPoint)
from PySide6.QtGui import (QColor, QPainter, QFont, QPalette, QBrush, QPen)
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QDialog, QFrame, 
                               QCalendarWidget, QSpinBox, QGraphicsDropShadowEffect, 
                               QAbstractSpinBox, QLineEdit, QStyledItemDelegate, 
                               QTableView, QStyle)


from monkeyqt.themes.engine import ThemeEngine

class ThemeMeta(type):
    @property
    def BG_COLOR(cls):
        return ThemeEngine.get("--surface", "#FFFFFF")
    @property
    def TEXT_PRIMARY(cls):
        return ThemeEngine.get("--fg", "#1E293B")
    @property
    def TEXT_SECONDARY(cls):
        return ThemeEngine.get("--text-muted", "#64748B")
    @property
    def ACCENT_COLOR(cls):
        t = ThemeEngine
        if t.is_glow() or t.is_brutal() or t.is_pixel():
            return t.get("--primary", "#409EFF")
        return "#FFFFFF" if t.is_dark() else "#0F172A"
    @property
    def ACCENT_HOVER(cls):
        return cls.ACCENT_COLOR
    @property
    def HOVER_BG(cls):
        return "rgba(255, 255, 255, 0.12)" if ThemeEngine.is_dark() else ThemeEngine.get("--surface-muted", "#F3F4F6")
    @property
    def BORDER_COLOR(cls):
        return ThemeEngine.get("--border", "#E5E7EB")

class Theme(metaclass=ThemeMeta):
    pass


class CalendarDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        rect = option.rect
        size = min(rect.width(), rect.height()) - 4
        center_rect = QRectF(
            rect.center().x() - size / 2,
            rect.center().y() - size / 2,
            size, size
        )

        is_selected = option.state & QStyle.State_Selected
        is_hovered = option.state & QStyle.State_MouseOver
        is_enabled = option.state & QStyle.State_Enabled

        hover_brush = QBrush(QColor(Theme.HOVER_BG))
        selected_brush = QBrush(QColor(Theme.ACCENT_COLOR))
        text_pen_normal = QPen(QColor(Theme.TEXT_PRIMARY))
        text_pen_selected = QPen(QColor("#0F172A" if ThemeEngine.is_dark() and Theme.ACCENT_COLOR == "#FFFFFF" else "#FFFFFF"))
        text_pen_sub = QPen(QColor(Theme.TEXT_SECONDARY))

        if is_selected:
            painter.setBrush(selected_brush)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center_rect)
        elif is_hovered and is_enabled:
            painter.setBrush(hover_brush)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center_rect)

        text = str(index.data(Qt.DisplayRole))
        if is_selected:
            painter.setPen(text_pen_selected)
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
        elif not is_enabled:
            painter.setPen(text_pen_sub)
        else:
            painter.setPen(text_pen_normal)

        painter.drawText(rect, Qt.AlignCenter, text)
        painter.restore()



class SmoothCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGridVisible(False)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setNavigationBarVisible(True)

        self.view = self.findChild(QTableView, "qt_calendar_calendarview")
        if self.view:
            self.view.setMouseTracking(True)
            self.view.setFrameShape(QFrame.NoFrame)
            self.view.setFocusPolicy(Qt.NoFocus)
            self.delegate = CalendarDelegate(self.view)
            self.view.setItemDelegate(self.delegate)
            self.view.viewport().setAttribute(Qt.WA_Hover)

        self.setup_styles()

    def setup_styles(self):
        self.setStyleSheet(f"""
            QCalendarWidget QWidget {{
                background-color: {Theme.BG_COLOR};
                alternate-background-color: {Theme.BG_COLOR};
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: transparent;
            }}

            /* 1. 月份按钮 */
            QToolButton#qt_calendar_monthbutton {{
                background-color: transparent;
                color: {Theme.TEXT_PRIMARY};
                font-size: 13px;
                font-weight: bold;
                min-width: 60px;
                margin-right: 5px;
                border: none;
            }}
            QToolButton#qt_calendar_monthbutton:hover {{
                background-color: {Theme.HOVER_BG};
                border-radius: 4px;
            }}

            /* 2. 年份按钮 */
            QToolButton#qt_calendar_yearbutton {{
                background-color: transparent;
                color: {Theme.TEXT_PRIMARY};
                font-size: 13px;
                font-weight: bold;
                min-width: 45px;
                border: none;
            }}
            QToolButton#qt_calendar_yearbutton:hover {{
                background-color: {Theme.HOVER_BG};
                border-radius: 4px;
            }}

            QSpinBox {{
                background-color: {Theme.BG_COLOR};
                color: {Theme.TEXT_PRIMARY};
                font-size: 13px;
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 4px;
            }}

            /* 左右箭头 */
            QToolButton#qt_calendar_prevmonth,
            QToolButton#qt_calendar_nextmonth {{
                color: {Theme.TEXT_PRIMARY};
                icon-size: 16px;
                width: 24px;
                height: 24px;
                margin: 2px 2px;
                border: none;
            }}
            QToolButton#qt_calendar_prevmonth:hover,
            QToolButton#qt_calendar_nextmonth:hover {{
                background-color: {Theme.HOVER_BG};
                border-radius: 12px;
            }}

            QCalendarWidget QMenu {{
                background-color: {Theme.BG_COLOR};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_COLOR};
                padding: 4px;
            }}
            QCalendarWidget QMenu::item:selected {{
                background-color: {Theme.HOVER_BG};
                color: {Theme.TEXT_PRIMARY};
                border-radius: 4px;
            }}

            QCalendarWidget QTableView {{
                selection-background-color: transparent;
                margin-top: 5px; /* 减小顶部间距 */
            }}
        """)


# --- SpinBox ---
class ModernSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setStyleSheet(f"""
            QSpinBox {{
                background-color: transparent;
                color: {Theme.TEXT_PRIMARY};
                border: none;
                font-size: 20px;
                font-weight: bold;
                selection-background-color: transparent;
                selection-color: {Theme.ACCENT_COLOR};
            }}
            QSpinBox:focus {{
                background-color: {Theme.HOVER_BG};
                border-radius: 8px;
            }}
        """)

    def wheelEvent(self, event):
        super().wheelEvent(event)
        event.accept()


class ModernDateTimePopup(QDialog):
    date_time_selected = Signal(QDateTime)
    def __init__(self, parent=None, target_widget=None, current_datetime=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 保存目标组件
        self.target_widget = target_widget
        self.current_dt = current_datetime or QDateTime.currentDateTime()

        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)  # 阴影预留区域

        self.container = QFrame(self)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_COLOR};
                border-radius: 12px;
                border: 1px solid {Theme.BORDER_COLOR};
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        content = QVBoxLayout(self.container)
        content.setSpacing(10)  # 布局间距
        content.setContentsMargins(15, 15, 15, 15)  # 内边距

        # 标题
        header = QHBoxLayout()
        title = QLabel("选择时间")
        # 字体
        title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {Theme.TEXT_PRIMARY}; border: none;")
        header.addWidget(title)
        content.addLayout(header)

        # 内容区
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(12)  # 左右模块间距

        self.calendar = SmoothCalendar()
        self.calendar.setSelectedDate(self.current_dt.date())
        # 尺寸大小
        self.calendar.setMinimumSize(260, 220)
        middle_layout.addWidget(self.calendar)

        # 分割线
        line = QFrame()
        line.setFixedWidth(1)
        line.setStyleSheet(f"background-color: {Theme.BORDER_COLOR}; border: none;")
        middle_layout.addWidget(line)

        # 时间滚轮
        time_layout = QVBoxLayout()
        time_layout.setAlignment(Qt.AlignCenter)

        # 滚轮尺寸
        spin_w, spin_h = 46, 36

        self.spin_hour = ModernSpinBox()
        self.spin_hour.setRange(0, 23)
        self.spin_hour.setFixedSize(spin_w, spin_h)
        self.spin_hour.setWrapping(True)

        self.spin_min = ModernSpinBox()
        self.spin_min.setRange(0, 59)
        self.spin_min.setFixedSize(spin_w, spin_h)
        self.spin_min.setWrapping(True)

        sep = QLabel(":")
        sep.setStyleSheet("font-size: 20px; font-weight: bold; color: #BBB; border: none; margin-bottom: 2px;")

        t_row = QHBoxLayout()
        t_row.setSpacing(2)
        t_row.addWidget(self.spin_hour)
        t_row.addWidget(sep)
        t_row.addWidget(self.spin_min)

        l_row = QHBoxLayout()
        l_row.setSpacing(2)
        for txt in ["时", "分"]:
            l = QLabel(txt)
            l.setAlignment(Qt.AlignCenter)
            l.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 11px; border: none;")
            l_row.addWidget(l)

        time_layout.addStretch()
        time_layout.addLayout(t_row)
        time_layout.addLayout(l_row)
        time_layout.addStretch()

        middle_layout.addLayout(time_layout)
        content.addLayout(middle_layout)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # 按钮字体和内边距
        btn_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid transparent;
                font-weight: 600;
                font-size: 13px;
                padding: 6px 12px;
                border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: {Theme.HOVER_BG}; }}
        """
        btn_primary_style = f"""
            QPushButton {{
                background-color: {Theme.ACCENT_COLOR};
                color: white;
                border: none;
                font-weight: 600;
                font-size: 13px;
                padding: 6px 16px;
                border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: {Theme.ACCENT_HOVER}; }}
        """

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet(btn_style)

        self.btn_ok = QPushButton("确认")
        self.btn_ok.setCursor(Qt.PointingHandCursor)
        self.btn_ok.setStyleSheet(btn_primary_style)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addSpacing(8)
        btn_layout.addWidget(self.btn_ok)
        content.addLayout(btn_layout)

        main_layout.addWidget(self.container)

        self.spin_hour.setValue(self.current_dt.time().hour())
        self.spin_min.setValue(self.current_dt.time().minute())

        self.btn_cancel.clicked.connect(self.reject_animated)
        self.btn_ok.clicked.connect(self.accept_data)

    def get_datetime(self):
        date = self.calendar.selectedDate()
        time = QTime(self.spin_hour.value(), self.spin_min.value())
        return QDateTime(date, time)

    def setup_animations(self):
        self.anim_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_opacity.setDuration(200)  # 动画
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)
        self.anim_opacity.setEasingCurve(QEasingCurve.OutCubic)

    def showEvent(self, event):
        if self.target_widget:
            global_pos = self.target_widget.mapToGlobal(QPoint(0, 0))
            target_height = self.target_widget.height()
            margin = 5
            x = global_pos.x() - margin
            y = global_pos.y() + target_height - margin + 5
            
            # fallback checking, we might not have valid screen in all contexts
            if self.screen():
                screen_geo = self.screen().availableGeometry()
                if y + self.height() > screen_geo.bottom():
                    y = global_pos.y() - self.height() + margin - 5
            
            self.move(x, y)

        elif self.parent():
            geo = self.parent().geometry()
            self.move(geo.center().x() - self.width() // 2,
                      geo.center().y() - self.height() // 2)

        self.anim_opacity.start()
        super().showEvent(event)

    def accept_data(self):
        self.date_time_selected.emit(self.get_datetime())
        self.accept()

    def reject_animated(self):
        self.anim_opacity.setDirection(QPropertyAnimation.Backward)
        self.anim_opacity.finished.connect(self.reject)
        self.anim_opacity.start()


class MkDatePicker(QLineEdit):
    """
    时间/日期选择器 (DatePicker)
    基于 QLineEdit 并集成 ModernDateTimePopup。
    """
    dateTimeChanged = Signal(QDateTime)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("选择时间")
        self.setCursor(Qt.PointingHandCursor)
        ThemeEngine.instance().themeChanged.connect(self.update_theme_style)
        self.update_theme_style()
        self.current_dt = QDateTime.currentDateTime()

    def update_theme_style(self, style_name: str = None):
        t = ThemeEngine
        is_dark = t.is_dark()
        focus_border = t.get("--input-focus-border", "#FFFFFF" if is_dark else "#0F172A")
        hover_border = t.get("--input-hover-border", "rgba(255, 255, 255, 0.40)" if is_dark else "#94A3B8")

        self.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {Theme.BORDER_COLOR};
                border-radius: 6px;
                padding: 5px 15px;
                background-color: {Theme.BG_COLOR};
                color: {Theme.TEXT_PRIMARY};
                min-width: 150px;
                min-height: 28px;
                font-size: 13px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            }}
            QLineEdit:hover {{
                border-color: {hover_border};
            }}
            QLineEdit:focus {{
                border-color: {focus_border};
            }}
        """)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.show_popup()

    def show_popup(self):
        popup = ModernDateTimePopup(parent=self.window(), target_widget=self, current_datetime=self.current_dt)
        popup.date_time_selected.connect(self.on_datetime_selected)
        popup.exec()

    def on_datetime_selected(self, dt):
        self.current_dt = dt
        self.setText(dt.toString("yyyy-MM-dd HH:mm"))
        self.dateTimeChanged.emit(dt)
