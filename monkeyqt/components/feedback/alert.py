import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Property, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter

from ...core.theme import ThemeManager
from ..layout.widget import MkQWidget

class MkAlert(MkQWidget):
    """
    信息条 (Alert) 组件
    用于页面中展示重要的提示信息。
    支持类型: info, success, warning, error
    """
    closed = Signal()

    def __init__(self, title="", description="", mk_type="info", closable=False, show_icon=False, parent=None, message=None, alert_type=None):
        super().__init__(parent)
        
        # Resolve type and title to support alert_type and message arguments
        resolved_type = "info"
        if alert_type is not None:
            resolved_type = alert_type
        else:
            resolved_type = mk_type
            
        resolved_title = title
        if message is not None:
            resolved_title = message

        self._title = resolved_title
        self._description = description
        self._mk_type = resolved_type
        self._closable = closable
        self._show_icon = show_icon

        self._setup_ui()
        self._update_style()

    def on_theme_changed(self, theme_name: str = ""):
        self._update_style()

    def _setup_ui(self):
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Main layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(16, 8, 16, 8)
        self.main_layout.setSpacing(12)

        # Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(16, 16)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setVisible(self._show_icon)
        self.main_layout.addWidget(self.icon_label, 0, Qt.AlignTop | Qt.AlignLeft)

        # Content layout (Title + Description)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(4)
        
        self.title_label = QLabel(self._title)
        self.title_label.setWordWrap(True)
        self.title_label.setObjectName("alert-title")
        self.content_layout.addWidget(self.title_label)

        self.desc_label = QLabel(self._description)
        self.desc_label.setWordWrap(True)
        self.desc_label.setObjectName("alert-desc")
        self.desc_label.setVisible(bool(self._description))
        self.content_layout.addWidget(self.desc_label)

        self.main_layout.addLayout(self.content_layout, 1)

        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("alert-close-btn")
        self.close_btn.setFixedSize(16, 16)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close_alert)
        self.close_btn.setVisible(self._closable)
        self.main_layout.addWidget(self.close_btn, 0, Qt.AlignTop | Qt.AlignRight)

        self._update_icon()

    def _update_icon(self):
        if not self._show_icon:
            return
        
        # Simple text icon based on type (in a real project, use SVG icons)
        icons = {
            "info": "ℹ",
            "success": "✓",
            "warning": "!",
            "error": "✕"
        }
        self.icon_label.setText(icons.get(self._mk_type, "ℹ"))
        self.icon_label.setObjectName(f"alert-icon-{self._mk_type}")

    def _update_style(self, theme_name: str = None):
        try:
            from monkeyqt.themes.engine import ThemeEngine
            t = ThemeEngine
            is_dark = t.is_dark()
            fg = t.get("--fg", "#0F172A")
            muted = t.get("--text-muted", "#64748B")
            radius = t.get("--radius", "6px")
        except Exception:
            is_dark = False
            fg = "#0F172A"
            muted = "#64748B"
            radius = "6px"

        if is_dark:
            colors = {
                "info": {"bg": "rgba(148, 163, 184, 0.12)", "text": "#E2E8F0", "border": "rgba(148, 163, 184, 0.25)", "icon": "#94A3B8"},
                "success": {"bg": "rgba(16, 185, 129, 0.15)", "text": "#34D399", "border": "rgba(16, 185, 129, 0.30)", "icon": "#10B981"},
                "warning": {"bg": "rgba(245, 158, 11, 0.15)", "text": "#FBBF24", "border": "rgba(245, 158, 11, 0.30)", "icon": "#F59E0B"},
                "error": {"bg": "rgba(239, 68, 68, 0.15)", "text": "#F87171", "border": "rgba(239, 68, 68, 0.30)", "icon": "#EF4444"}
            }
            title_color = fg if self._description else None
            desc_color = muted
            close_color = muted
            close_hover = fg
        else:
            colors = {
                "info": {"bg": "#f4f4f5", "text": "#64748b", "border": "#e2e8f0", "icon": "#64748b"},
                "success": {"bg": "#ecfdf5", "text": "#059669", "border": "#a7f3d0", "icon": "#10b981"},
                "warning": {"bg": "#fffbeb", "text": "#d97706", "border": "#fde68a", "icon": "#f59e0b"},
                "error": {"bg": "#fef2f2", "text": "#dc2626", "border": "#fecaca", "icon": "#ef4444"}
            }
            title_color = "#0F172A" if self._description else None
            desc_color = "#475569"
            close_color = "#94A3B8"
            close_hover = "#0F172A"
        
        c = colors.get(self._mk_type, colors["info"])
        actual_title_color = title_color or c['text']
        
        qss = f"""
            MkAlert {{
                background-color: {c['bg']};
                border-radius: {radius};
                border: 1px solid {c['border']};
            }}
            QLabel {{
                background-color: transparent;
            }}
            #alert-title {{
                color: {actual_title_color};
                font-size: 13px;
                font-weight: {'bold' if self._description else 'normal'};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            }}
            #alert-desc {{
                color: {desc_color};
                font-size: 12px;
                margin-top: 4px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            }}
            #alert-close-btn {{
                background: transparent;
                border: none;
                color: {close_color};
                font-size: 12px;
            }}
            #alert-close-btn:hover {{
                color: {close_hover};
            }}
            QLabel[objectName^="alert-icon-"] {{
                color: {c['icon']};
                font-weight: bold;
                font-size: 14px;
            }}
        """
        self.setStyleSheet(qss)

    def close_alert(self):
        self.hide()
        self.closed.emit()

    # Properties
    @Property(str)
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_label.setText(value)

    @Property(str)
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self.desc_label.setText(value)
        self.desc_label.setVisible(bool(value))
        self._update_style()

    @Property(str)
    def mk_type(self):
        return self._mk_type

    @mk_type.setter
    def mk_type(self, value):
        if value not in ["info", "success", "warning", "error"]:
            value = "info"
        if self._mk_type != value:
            self._mk_type = value
            self._update_icon()
            self._update_style()

    @Property(bool)
    def closable(self):
        return self._closable

    @closable.setter
    def closable(self, value):
        self._closable = value
        self.close_btn.setVisible(value)

    @Property(bool)
    def show_icon(self):
        return self._show_icon

    @show_icon.setter
    def show_icon(self, value):
        self._show_icon = value
        self.icon_label.setVisible(value)
        self._update_icon()

    @Property(str)
    def message(self):
        return self.title

    @message.setter
    def message(self, value):
        self.title = value

    @Property(str)
    def alert_type(self):
        return self.mk_type

    @alert_type.setter
    def alert_type(self, value):
        self.mk_type = value
