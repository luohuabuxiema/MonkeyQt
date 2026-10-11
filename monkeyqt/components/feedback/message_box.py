# -*- coding: utf-8 -*-
"""
MonkeyQt 现代化模态对话框与消息弹窗组件
包含:
  - MkModal / MkDialog: 现代化卡片式悬浮模态容器 (支持自适应 68 种主题、半透明遮罩、自定义内容控件)
  - MkMessageBox: 极简一行代码调用的消息弹窗外观门面 (confirm, info, success, warning, error, prompt)
"""

from typing import Optional, Union, Tuple, Sequence, Callable
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGraphicsDropShadowEffect,
    QApplication,
    QLineEdit,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QPoint, QRectF, QEvent, Signal, QTimer, QSize
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QBrush, QFont, QIcon, QKeyEvent

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import qcolor, readable_text, parse_px, lighten, darken

try:
    from monkeyqt_icons import Ph
    _HAS_PH_ICONS = True
except Exception:
    _HAS_PH_ICONS = False


class _ModalButton(QPushButton):
    """
    专为模态弹窗优化的胶囊/圆角微交互操作按钮
    完美支持取消态、危险软色调态 (对标现代前端设计)、主色态、成功/警告态
    """
    def __init__(self, text: str = "", variant: str = "cancel", parent=None):
        super().__init__(text, parent)
        self._variant = variant
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(34)
        self.setMinimumWidth(84)
        font = QFont("Segoe UI", 9, QFont.Weight.DemiBold)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        self.setFont(font)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self._apply_style()

    def set_variant(self, variant: str):
        self._variant = variant
        self._apply_style()

    def _apply_style(self):
        is_dark = ThemeEngine.is_dark()
        var = self._variant.lower()

        if var in ("cancel", "default", "neutral"):
            if is_dark:
                qss = """
                QPushButton {
                    background-color: #27272A;
                    border: 1px solid #3F3F46;
                    color: #F4F4F5;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #3F3F46;
                    border-color: #52525B;
                    color: #FFFFFF;
                }
                QPushButton:pressed {
                    background-color: #52525B;
                }
                """
            else:
                border_c = ThemeEngine.get("--border", "#E2E8F0")
                qss = f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    border: 1px solid {border_c};
                    color: #0F172A;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #F8FAFC;
                    border-color: #CBD5E1;
                    color: #0F172A;
                }}
                QPushButton:pressed {{
                    background-color: #F1F5F9;
                }}
                """
        elif var in ("danger", "destructive"):
            # 现代前端流行的高级软红底红字（参考截图规范）
            if is_dark:
                qss = """
                QPushButton {
                    background-color: #3C1B1B;
                    border: 1px solid #5A2323;
                    color: #F87171;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #4D2222;
                    border-color: #772C2C;
                    color: #FCA5A5;
                }
                QPushButton:pressed {
                    background-color: #5C2828;
                }
                """
            else:
                qss = """
                QPushButton {
                    background-color: #FEE2E2;
                    border: 1px solid #FECACA;
                    color: #DC2626;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #FECACA;
                    border-color: #FCA5A5;
                    color: #B91C1C;
                }
                QPushButton:pressed {
                    background-color: #FCA5A5;
                }
                """
        elif var in ("danger_solid", "destructive_solid"):
            # 实心红底白字
            qss = """
            QPushButton {
                background-color: #DC2626;
                border: none;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
            QPushButton:pressed {
                background-color: #991B1B;
            }
            """
        elif var == "success":
            if is_dark:
                qss = """
                QPushButton {
                    background-color: #143823;
                    border: 1px solid #1C5432;
                    color: #4ADE80;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #1A472D;
                    color: #86EFAC;
                }
                QPushButton:pressed {
                    background-color: #235A3A;
                }
                """
            else:
                qss = """
                QPushButton {
                    background-color: #DCFCE7;
                    border: 1px solid #BBF7D0;
                    color: #16A34A;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #BBF7D0;
                    color: #15803D;
                }
                QPushButton:pressed {
                    background-color: #86EFAC;
                }
                """
        elif var == "warning":
            if is_dark:
                qss = """
                QPushButton {
                    background-color: #3B280E;
                    border: 1px solid #573B13;
                    color: #FBBF24;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #4D3312;
                    color: #FCD34D;
                }
                QPushButton:pressed {
                    background-color: #614018;
                }
                """
            else:
                qss = """
                QPushButton {
                    background-color: #FEF3C7;
                    border: 1px solid #FDE68A;
                    color: #D97706;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #FDE68A;
                    color: #B45309;
                }
                QPushButton:pressed {
                    background-color: #FCD34D;
                }
                """
        else:
            # 默认 primary 模式，跟随主题色
            primary = ThemeEngine.get("--primary", "#0F172A")
            hover_primary = ThemeEngine.get("--hover-primary", lighten(primary, 0.15))
            text_color = readable_text(primary)
            qss = f"""
            QPushButton {{
                background-color: {primary};
                border: none;
                color: {text_color};
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {hover_primary};
            }}
            QPushButton:pressed {{
                background-color: {darken(primary, 0.10)};
            }}
            """

        self.setStyleSheet(qss)


class _ModalCardWidget(QFrame):
    """
    模态框居中核心卡片容器
    使用原生 QPainter + 抗锯齿绘制平滑大圆角与外微描边，杜绝边缘锯齿
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._radius = 16.0
        self._bg_color = QColor("#FFFFFF")
        self._border_color = QColor("#E2E8F0")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        # 悬浮立体柔和阴影
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(32)
        self._shadow.setOffset(0, 8)
        self._shadow.setColor(QColor(0, 0, 0, 45))
        self.setGraphicsEffect(self._shadow)

    def set_appearance(self, bg_color: QColor, border_color: QColor, is_dark: bool, radius: float = 16.0):
        self._bg_color = bg_color
        self._border_color = border_color
        self._radius = radius
        if is_dark:
            self._shadow.setColor(QColor(0, 0, 0, 160))
            self._shadow.setBlurRadius(36)
        else:
            self._shadow.setColor(QColor(0, 0, 0, 45))
            self._shadow.setBlurRadius(28)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, self._radius, self._radius)
        painter.fillPath(path, QBrush(self._bg_color))
        painter.setPen(QPen(self._border_color, 1))
        painter.drawPath(path)
        painter.end()


class MkModal(QDialog):
    """
    MkModal (别名 MkDialog) - 现代化卡片式悬浮模态弹窗容器
    
    特性:
      1. 极致美感：纯净大圆角悬浮卡片、柔和阴影、可自定义半透明全屏遮罩；
      2. 68 种主题自适应：底色、描边、文字排版、按钮配色毫秒级动态切换；
      3. 对标现代前端规范：支持 Danger 危险弱底确认按钮（Delete model 场景）；
      4. 深度可扩展：支持在正文中自由嵌入任意 QWidget 自定义组件（输入框、表单等）；
      5. 贴心交互：Esc 键取消，Enter 键确认，点击背景遮罩自适应关闭（可配置）。
    """
    
    # 确定与取消信号
    confirmed = Signal()
    cancelled = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "确认操作",
        content: str = "",
        *,
        danger: bool = False,
        ok_text: str = "确定",
        cancel_text: Optional[str] = "取消",
        ok_type: str = "primary",
        icon: Optional[Union[str, QIcon]] = None,
        closable: bool = False,
        mask_closable: bool = False,
        overlay: bool = True,
        mask_opacity: Optional[float] = None,
        card_width: int = 420,
        custom_widget: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        self._title_text = title
        self._content_text = content
        self._danger = danger
        self._ok_text = ok_text
        self._cancel_text = cancel_text
        self._ok_type = "danger" if danger else ok_type
        self._icon_spec = icon
        self._closable = closable
        self._mask_closable = mask_closable
        self._overlay = overlay
        self._mask_opacity_custom = mask_opacity
        self._card_width = max(320, card_width)
        self._custom_widget = custom_widget

        self._target_parent: Optional[QWidget] = self._resolve_target_parent(parent)
        if self._target_parent:
            self._target_parent.installEventFilter(self)

        self._setup_ui()
        self._update_theme_style()

        # 监听主题引擎切换
        ThemeEngine.instance().themeChanged.connect(self._on_theme_changed)

    def _resolve_target_parent(self, parent: Optional[QWidget]) -> Optional[QWidget]:
        if parent and isinstance(parent, QWidget):
            return parent.window() if parent.window() else parent
        active = QApplication.activeWindow()
        if active and active is not self:
            return active
        return None

    def _setup_ui(self):
        # 整体对话框布局（用于将卡片居中定位）
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(24, 24, 24, 24)
        self._main_layout.setSpacing(0)

        # 核心卡片容器
        self._card = _ModalCardWidget(self)
        screen = QApplication.primaryScreen()
        if screen:
            max_allowed = max(280, int(screen.availableGeometry().width() * 0.90))
            if self._card_width > max_allowed:
                self._card_width = max_allowed
        self._card.setFixedWidth(self._card_width)
        self._card_layout = QVBoxLayout(self._card)
        self._card_layout.setContentsMargins(0, 0, 0, 0)
        self._card_layout.setSpacing(0)

        # ── 1. 顶部内容区 ──
        self._top_widget = QWidget(self._card)
        self._top_widget.setObjectName("MkModalTop")
        self._top_widget.setStyleSheet("background: transparent;")
        self._top_layout = QVBoxLayout(self._top_widget)
        self._top_layout.setContentsMargins(24, 22, 24, 18)
        self._top_layout.setSpacing(10)

        # 标题栏行
        self._header_layout = QHBoxLayout()
        self._header_layout.setContentsMargins(0, 0, 0, 0)
        self._header_layout.setSpacing(10)

        # 可选图标
        self._icon_label = QLabel(self._top_widget)
        self._icon_label.setFixedSize(22, 22)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._header_layout.addWidget(self._icon_label)
        self._setup_icon()

        # 标题文字
        self._title_label = QLabel(self._title_text, self._top_widget)
        title_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        title_font.setStyleHint(QFont.StyleHint.SansSerif)
        self._title_label.setFont(title_font)
        self._title_label.setWordWrap(True)
        self._header_layout.addWidget(self._title_label, 1)

        # 可选右上角关闭按钮
        if self._closable:
            self._close_btn = QPushButton("✕", self._top_widget)
            self._close_btn.setFixedSize(24, 24)
            self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._close_btn.clicked.connect(self.reject)
            self._header_layout.addWidget(self._close_btn, 0, Qt.AlignmentFlag.AlignTop)
        else:
            self._close_btn = None

        self._top_layout.addLayout(self._header_layout)

        # 正文描述文字
        self._content_label = QLabel(self._content_text, self._top_widget)
        content_font = QFont("Segoe UI", 10)
        content_font.setStyleHint(QFont.StyleHint.SansSerif)
        self._content_label.setFont(content_font)
        self._content_label.setWordWrap(True)
        self._content_label.setTextFormat(Qt.TextFormat.RichText)
        self._content_label.setOpenExternalLinks(True)
        self._top_layout.addWidget(self._content_label)
        self._content_label.setVisible(bool(self._content_text))

        # 用户自定义组件嵌入插槽
        self._custom_slot_layout = QVBoxLayout()
        self._custom_slot_layout.setContentsMargins(0, 4, 0, 0)
        self._custom_slot_layout.setSpacing(8)
        self._top_layout.addLayout(self._custom_slot_layout)
        if self._custom_widget:
            self._custom_slot_layout.addWidget(self._custom_widget)

        self._card_layout.addWidget(self._top_widget)

        # ── 2. 底部分割线 ──
        self._divider = QFrame(self._card)
        self._divider.setFixedHeight(1)
        self._divider.setFrameShape(QFrame.Shape.HLine)
        self._divider.setFrameShadow(QFrame.Shadow.Plain)
        self._card_layout.addWidget(self._divider)

        # ── 3. 底部操作区 ──
        self._footer_widget = QWidget(self._card)
        self._footer_widget.setObjectName("MkModalFooter")
        self._footer_widget.setStyleSheet("background: transparent;")
        self._footer_layout = QHBoxLayout(self._footer_widget)
        self._footer_layout.setContentsMargins(24, 14, 24, 16)
        self._footer_layout.setSpacing(10)

        self._footer_layout.addStretch(1)

        # 取消按钮
        if self._cancel_text:
            self._cancel_btn = _ModalButton(self._cancel_text, variant="cancel", parent=self._footer_widget)
            self._cancel_btn.clicked.connect(self.reject)
            self._footer_layout.addWidget(self._cancel_btn)
        else:
            self._cancel_btn = None

        # 确认按钮
        btn_variant = "danger" if self._danger else self._ok_type
        self._ok_btn = _ModalButton(self._ok_text, variant=btn_variant, parent=self._footer_widget)
        self._ok_btn.clicked.connect(self.accept)
        self._footer_layout.addWidget(self._ok_btn)

        self._card_layout.addWidget(self._footer_widget)

        # 将卡片放入主布局居中对齐
        self._main_layout.addWidget(self._card, 0, Qt.AlignmentFlag.AlignCenter)

    def _setup_icon(self):
        if not self._icon_spec:
            self._icon_label.setVisible(False)
            return

        self._icon_label.setVisible(True)
        if isinstance(self._icon_spec, QIcon):
            pix = self._icon_spec.pixmap(20, 20)
            self._icon_label.setPixmap(pix)
        elif isinstance(self._icon_spec, str):
            spec = self._icon_spec.lower()
            if _HAS_PH_ICONS:
                icon_map = {
                    "warning": "warning-circle",
                    "danger": "warning-octagon",
                    "error": "x-circle",
                    "success": "check-circle",
                    "info": "info",
                    "trash": "trash",
                    "question": "question",
                }
                icon_key = icon_map.get(spec, spec)
                try:
                    icon_obj = Ph.icon(icon_key)
                    if icon_obj and not icon_obj.isNull():
                        self._icon_label.setPixmap(icon_obj.pixmap(20, 20))
                        return
                except Exception:
                    pass

            # 纯文本字符回退
            unicode_map = {
                "warning": "⚠️",
                "danger": "⚠️",
                "error": "❌",
                "success": "✅",
                "info": "ℹ️",
                "question": "❓",
            }
            self._icon_label.setText(unicode_map.get(spec, "ℹ️"))

    def set_custom_widget(self, widget: QWidget):
        """设置/替换模态框内部的自定义控件（如输入框、选项卡片等）"""
        # 清除现有
        while self._custom_slot_layout.count():
            item = self._custom_slot_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._custom_widget = widget
        if widget:
            self._custom_slot_layout.addWidget(widget)
        self._card.adjustSize()
        self.adjustSize()

    def set_content(self, content: str):
        """动态更新正文内容"""
        self._content_text = content
        self._content_label.setText(content)
        self._content_label.setVisible(bool(content))
        self._card.adjustSize()

    def set_title(self, title: str):
        """动态更新标题内容"""
        self._title_text = title
        self._title_label.setText(title)

    def _on_theme_changed(self, theme_name: str = ""):
        self._update_theme_style()

    def _update_theme_style(self):
        is_dark = ThemeEngine.is_dark()

        # 读取主题 Token
        fg = ThemeEngine.get("--fg", "#F4F4F5" if is_dark else "#0F172A")
        text_muted = ThemeEngine.get("--text-muted", "#A1A1AA" if is_dark else "#64748B")
        border = ThemeEngine.get("--border", "#303030" if is_dark else "#E2E8F0")
        surface = ThemeEngine.get("--surface", "#18181B" if is_dark else "#FFFFFF")

        # 细微调理：如果 surface 刚好是亮色但处于暗色系，做高对比度补偿
        if is_dark and surface.upper() in ("#FFFFFF", "#F8FAFC", "#F5F5F5"):
            surface = "#18181B"
            border = "#2E2E32"

        radius = parse_px(ThemeEngine.get("--radius", "16px"), 16, 8, 24)

        # 更新卡片外观
        self._card.set_appearance(
            bg_color=qcolor(surface),
            border_color=qcolor(border),
            is_dark=is_dark,
            radius=float(radius),
        )

        # 标题与正文样式 (富文本中 <b> 标签自动高亮为标题前景色)
        self._title_label.setStyleSheet(f"color: {fg}; background: transparent;")
        self._content_label.setStyleSheet(
            f"QLabel {{ color: {text_muted}; background: transparent; line-height: 1.5; }} "
            f"b, strong {{ color: {fg}; font-weight: 600; }}"
        )

        # 分割线颜色
        self._divider.setStyleSheet(f"background-color: {border}; border: none;")

        # 关闭按钮样式
        if self._close_btn:
            close_hover_bg = "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(0, 0, 0, 0.06)"
            self._close_btn.setStyleSheet(f"""
                QPushButton {{
                    color: {text_muted};
                    background: transparent;
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    color: {fg};
                    background-color: {close_hover_bg};
                }}
            """)

        # 按钮样式刷新
        if self._cancel_btn:
            self._cancel_btn._apply_style()
        if self._ok_btn:
            self._ok_btn._apply_style()

        self.update()

    def _sync_parent_geometry(self):
        """自动吸附并覆盖父窗口区域，呈现沉浸式遮罩"""
        if not self._overlay or not self._target_parent:
            return
        if self._target_parent.isVisible():
            top_left = self._target_parent.mapToGlobal(QPoint(0, 0))
            self.setGeometry(top_left.x(), top_left.y(), self._target_parent.width(), self._target_parent.height())

    def eventFilter(self, obj, event):
        if obj is self._target_parent:
            if event.type() in (QEvent.Type.Resize, QEvent.Type.Move):
                self._sync_parent_geometry()
            elif event.type() == QEvent.Type.Close:
                self.reject()
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)
        if self._overlay and self._target_parent and self._target_parent.isVisible():
            self._sync_parent_geometry()
        else:
            # 没有父窗口或无需遮罩时，自动在屏幕居中
            screen = QApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                self.move(
                    geo.center().x() - self.width() // 2,
                    geo.center().y() - self.height() // 2,
                )

    def closeEvent(self, event):
        if self._target_parent:
            try:
                self._target_parent.removeEventFilter(self)
            except Exception:
                pass
        super().closeEvent(event)

    def done(self, r):
        if self._target_parent:
            try:
                self._target_parent.removeEventFilter(self)
            except Exception:
                pass
        if r == QDialog.DialogCode.Accepted:
            self.confirmed.emit()
        else:
            self.cancelled.emit()
        super().done(r)

    def paintEvent(self, event):
        """绘制背景遮罩层"""
        if not self._overlay or not self._target_parent:
            return

        painter = QPainter(self)
        is_dark = ThemeEngine.is_dark()
        if self._mask_opacity_custom is not None:
            opacity = max(0.0, min(1.0, self._mask_opacity_custom))
        else:
            opacity = 0.58 if is_dark else 0.40

        mask_alpha = int(255 * opacity)
        mask_color = QColor(0, 0, 0, mask_alpha)
        painter.fillRect(self.rect(), mask_color)
        painter.end()

    def mousePressEvent(self, event):
        """点击卡片外部遮罩区，支持配置自动关闭"""
        if event.button() == Qt.MouseButton.LeftButton:
            card_geo = self._card.geometry()
            if not card_geo.contains(event.pos()):
                if self._mask_closable:
                    self.reject()
                    return
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """快捷键支持：Esc 取消，Enter 确定"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # 若焦点在文本框且非多行文本，或者焦点不在输入框，直接触发确认
            focus_w = self.focusWidget()
            if focus_w and isinstance(focus_w, QLineEdit):
                self.accept()
                return
            elif not focus_w or isinstance(focus_w, QPushButton):
                self.accept()
                return
        super().keyPressEvent(event)


# 别名
MkDialog = MkModal


class MkMessageBox:
    """
    MkMessageBox - 极简一行代码调用的现代弹窗外观门面
    
    提供比原生 QMessageBox 更加美观、现代化且完全契合 68 种主题的静态方法。
    """

    @staticmethod
    def confirm(
        parent: Optional[QWidget] = None,
        title: str = "确认操作",
        content: str = "",
        *,
        danger: bool = False,
        ok_text: str = "确定",
        cancel_text: str = "取消",
        mask_closable: bool = False,
        icon: Optional[Union[str, QIcon]] = None,
        custom_widget: Optional[QWidget] = None,
        width: int = 420,
    ) -> bool:
        """
        弹出双按钮确认弹窗（支持软红底 Danger 危险按钮，对标 Delete model 场景）
        返回: True (用户点击确定) / False (用户点击取消或 Esc)
        """
        modal = MkModal(
            parent=parent,
            title=title,
            content=content,
            danger=danger,
            ok_text=ok_text,
            cancel_text=cancel_text,
            mask_closable=mask_closable,
            icon=icon,
            custom_widget=custom_widget,
            card_width=width,
        )
        result = modal.exec()
        return result == QDialog.DialogCode.Accepted

    @staticmethod
    def info(
        parent: Optional[QWidget] = None,
        title: str = "提示",
        content: str = "",
        *,
        ok_text: str = "我知道了",
        mask_closable: bool = True,
        icon: Optional[Union[str, QIcon]] = "info",
        width: int = 420,
    ) -> bool:
        """弹出信息提示弹窗（单按钮）"""
        modal = MkModal(
            parent=parent,
            title=title,
            content=content,
            ok_text=ok_text,
            cancel_text=None,
            ok_type="primary",
            mask_closable=mask_closable,
            icon=icon,
            card_width=width,
        )
        return modal.exec() == QDialog.DialogCode.Accepted

    @staticmethod
    def success(
        parent: Optional[QWidget] = None,
        title: str = "成功",
        content: str = "",
        *,
        ok_text: str = "确定",
        mask_closable: bool = True,
        icon: Optional[Union[str, QIcon]] = "success",
        width: int = 420,
    ) -> bool:
        """弹出操作成功弹窗"""
        modal = MkModal(
            parent=parent,
            title=title,
            content=content,
            ok_text=ok_text,
            cancel_text=None,
            ok_type="success",
            mask_closable=mask_closable,
            icon=icon,
            card_width=width,
        )
        return modal.exec() == QDialog.DialogCode.Accepted

    @staticmethod
    def warning(
        parent: Optional[QWidget] = None,
        title: str = "警告",
        content: str = "",
        *,
        ok_text: str = "确定",
        cancel_text: Optional[str] = "取消",
        mask_closable: bool = False,
        icon: Optional[Union[str, QIcon]] = "warning",
        width: int = 420,
    ) -> bool:
        """弹出操作警告弹窗"""
        modal = MkModal(
            parent=parent,
            title=title,
            content=content,
            ok_text=ok_text,
            cancel_text=cancel_text,
            ok_type="warning",
            mask_closable=mask_closable,
            icon=icon,
            card_width=width,
        )
        return modal.exec() == QDialog.DialogCode.Accepted

    @staticmethod
    def error(
        parent: Optional[QWidget] = None,
        title: str = "错误",
        content: str = "",
        *,
        ok_text: str = "关闭",
        cancel_text: Optional[str] = None,
        mask_closable: bool = False,
        icon: Optional[Union[str, QIcon]] = "error",
        width: int = 420,
    ) -> bool:
        """弹出操作异常/失败弹窗"""
        modal = MkModal(
            parent=parent,
            title=title,
            content=content,
            ok_text=ok_text,
            cancel_text=cancel_text,
            danger=True,
            mask_closable=mask_closable,
            icon=icon,
            card_width=width,
        )
        return modal.exec() == QDialog.DialogCode.Accepted

    @staticmethod
    def prompt(
        parent: Optional[QWidget] = None,
        title: str = "请输入",
        content: str = "",
        default_value: str = "",
        placeholder: str = "请输入内容...",
        *,
        ok_text: str = "确定",
        cancel_text: str = "取消",
        width: int = 440,
    ) -> Tuple[bool, str]:
        """
        弹出带文本输入的模态弹窗
        返回: (是否确认, 输入的字符串内容)
        """
        # 创建内嵌输入框
        input_widget = QLineEdit(default_value)
        input_widget.setPlaceholderText(placeholder)
        input_widget.setFixedHeight(36)
        
        # 适配当前主题的精致输入框 QSS
        is_dark = ThemeEngine.is_dark()
        bg_c = "#27272A" if is_dark else "#FFFFFF"
        fg_c = "#F4F4F5" if is_dark else "#0F172A"
        border_c = "#3F3F46" if is_dark else "#CBD5E1"
        focus_c = ThemeEngine.get("--primary", "#409EFF")

        input_widget.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg_c};
                color: {fg_c};
                border: 1px solid {border_c};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {focus_c};
            }}
        """)

        modal = MkModal(
            parent=parent,
            title=title,
            content=content,
            ok_text=ok_text,
            cancel_text=cancel_text,
            ok_type="primary",
            custom_widget=input_widget,
            card_width=width,
        )

        input_widget.selectAll()
        QTimer.singleShot(50, input_widget.setFocus)

        confirmed = (modal.exec() == QDialog.DialogCode.Accepted)
        return confirmed, (input_widget.text() if confirmed else "")

    @staticmethod
    def delete_confirm(
        parent: Optional[QWidget] = None,
        item_name: str = "yolo26n-seg",
        item_type: str = "model",
        retention_days: int = 30,
        *,
        ok_text: Optional[str] = None,
        cancel_text: str = "Cancel",
        lang: str = "zh",
    ) -> bool:
        """
        经典复刻参考图的场景专用快捷弹窗 (Delete Model)
        """
        if lang == "en":
            title = f"Delete {item_type}?"
            content = f"<b>{item_name}</b> will move to Trash. Items can be restored within {retention_days} days."
            ok_btn_text = ok_text or f"Delete {item_type}"
            cancel_btn_text = cancel_text
        else:
            title = f"确认删除该{item_type}？"
            content = f"<b>{item_name}</b> 将被移入回收站。项目可在 {retention_days} 天内进行恢复。"
            ok_btn_text = ok_text or f"删除{item_type}"
            cancel_btn_text = "取消"

        return MkMessageBox.confirm(
            parent=parent,
            title=title,
            content=content,
            danger=True,
            ok_text=ok_btn_text,
            cancel_text=cancel_btn_text,
        )
