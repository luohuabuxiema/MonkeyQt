from PySide6.QtWidgets import QLineEdit, QLabel, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QAction, QFocusEvent
from monkeyqt.core.icons import MkPhosphorIcon
from monkeyqt.themes.engine import ThemeEngine

class MkInput(QLineEdit):
    """
    MkInput - Modern Web-style text input field.
    Supports Phosphor leading icons, custom focus rings, interactive password visibility toggle,
    and full automatic adaptation across all 68 MonkeyQt UI themes.
    """
    def __init__(self, placeholder: str = "", is_password: bool = False, leading_icon: str = None, parent=None):
        super().__init__(parent)
        self.is_password = is_password
        self.leading_icon_name = leading_icon
        
        self.setPlaceholderText(placeholder)
        
        self.leading_label = None
        self.password_btn = None
        self._password_visible = False
        
        self._setup_ui()
        self._apply_theme_style()
        ThemeEngine.instance().themeChanged.connect(self._apply_theme_style)

    def _setup_ui(self):
        # Configure input margins
        left_margin = 12
        right_margin = 12
        
        # 1. Setup leading icon
        if self.leading_icon_name:
            left_margin = 32
            self.leading_label = QLabel(self)
            self.leading_label.setFixedSize(16, 16)
            self.leading_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.leading_label.setStyleSheet("background: transparent;")
            
        # 2. Setup trailing password toggle eye button
        if self.is_password:
            right_margin = 32
            self.setEchoMode(QLineEdit.EchoMode.Password)
            
            self.password_btn = QPushButton(self)
            self.password_btn.setFixedSize(20, 20)
            self.password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.password_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.password_btn.setAutoDefault(False)
            self.password_btn.setDefault(False)
            self.password_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    outline: none;
                }
            """)
            self.password_btn.clicked.connect(self._toggle_password_visibility)
            
            # Initially hide the button if there is no text
            self.password_btn.hide()
            self.textChanged.connect(self._on_text_changed)
            
        # Apply padding margins so text doesn't overlap icons
        self.setTextMargins(left_margin, 0, right_margin, 0)

    def _apply_theme_style(self, theme_name: str = None):
        """Apply theme tokens dynamically across light, dark, and specialized styles."""
        t = ThemeEngine
        tokens = t.current_tokens()
        
        surface = tokens.get("--surface", "#ffffff")
        border = tokens.get("--border", "#e2e8f0")
        fg = tokens.get("--fg", "#0f172a")
        primary = tokens.get("--primary", "#3b82f6")
        muted = tokens.get("--text-muted", "#64748b")
        surface_muted = tokens.get("--surface-muted", "#f1f5f9")
        radius = "0px" if t.is_brutal() or t.is_pixel() else tokens.get("--radius", "6px")
        border_rule = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        focus_border = t.get("--input-focus-border", "#FFFFFF" if t.is_dark() else "#0F172A")
        hover_border = t.get("--input-hover-border", "rgba(255, 255, 255, 0.40)" if t.is_dark() else "#94A3B8")
        
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {surface};
                border: {border_rule};
                border-radius: {radius};
                color: {fg};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
                font-size: 13px;
                min-height: 28px;
                selection-background-color: {primary};
                selection-color: #ffffff;
            }}
            QLineEdit:hover {{
                border-color: {hover_border};
            }}
            QLineEdit:focus {{
                border-color: {focus_border};
                background-color: {surface};
            }}
            QLineEdit:disabled {{
                background-color: {surface_muted};
                color: {muted};
            }}
        """)
        
        if self.leading_label and self.leading_icon_name:
            current_color = focus_border if self.hasFocus() else muted
            self.leading_label.setPixmap(MkPhosphorIcon.get_pixmap(self.leading_icon_name, current_color, 16))
            
        if self.password_btn:
            eye_icon = "eye-slash" if self._password_visible else "eye"
            self.password_btn.setIcon(MkPhosphorIcon.get_icon(eye_icon, muted, primary, 16))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        h = self.height()
        w = self.width()
        
        # Dynamic positioning of overlays during resize
        if self.leading_label:
            # Centered vertically at x=10
            ly = (h - 16) // 2
            self.leading_label.move(10, ly)
            
        if self.password_btn:
            # Centered vertically at x = width - 26
            py = (h - 20) // 2
            self.password_btn.move(w - 26, py)

    def _toggle_password_visibility(self):
        self._password_visible = not self._password_visible
        t = ThemeEngine
        primary = t.get("--primary", "#3b82f6")
        muted = t.get("--text-muted", "#64748b")
        if self._password_visible:
            self.setEchoMode(QLineEdit.EchoMode.Normal)
            self.password_btn.setIcon(MkPhosphorIcon.get_icon("eye-slash", primary, muted, 16))
        else:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_btn.setIcon(MkPhosphorIcon.get_icon("eye", muted, primary, 16))

    def _on_text_changed(self, text):
        if self.password_btn:
            self.password_btn.setVisible(bool(text))
            
    def focusInEvent(self, event: QFocusEvent):
        super().focusInEvent(event)
        t = ThemeEngine
        focus_border = t.get("--input-focus-border", "#FFFFFF" if t.is_dark() else "#0F172A")
        if self.leading_label and self.leading_icon_name:
            self.leading_label.setPixmap(MkPhosphorIcon.get_pixmap(self.leading_icon_name, focus_border, 16))

    def focusOutEvent(self, event: QFocusEvent):
        super().focusOutEvent(event)
        t = ThemeEngine
        muted = t.get("--text-muted", "#64748b")
        if self.leading_label and self.leading_icon_name:
            self.leading_label.setPixmap(MkPhosphorIcon.get_pixmap(self.leading_icon_name, muted, 16))
