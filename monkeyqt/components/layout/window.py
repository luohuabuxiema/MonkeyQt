# -*- coding: utf-8 -*-
"""
@File ：window.py
@Desc ：Custom title bar and frameless window components for MonkeyQt.
"""
import sys
from typing import Optional, List, Dict, Any, Union


from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QGraphicsDropShadowEffect, QFrame,
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QPoint, Signal, QEvent, QRect, QRectF, QSize, QTimer
from PySide6.QtGui import QFont, QCursor, QColor, QMouseEvent, QIcon, QGuiApplication, QPainter, QPainterPath

from monkeyqt.components.navigation import MkAnimatedStackedWidget, MkHistoryNavigation, MkAvatarMenu
from monkeyqt.core.icons import MkPhosphorIcon
from .widget import MkQWidget

class MkTitleBarCloseButton(QPushButton):
    """
    Dedicated close button for MkTitleBar.
    Features:
    1. Automatic corner radius adaptation matching the host window/system.
       - Windowed mode: Smooth rounded top-right corner matching window border-radius (default 8px).
       - Maximized mode: Straight 90-degree right angle (0px) honoring Fitts's Law.
    2. Pixel-perfect seamless fitting:
       - Uses QPainter.CompositionMode_Source to eliminate any underlying titlebar/container
         background fringe or color leak.
       - High-DPI anti-aliased geometry drawing.
    """
    def __init__(self, titlebar, parent=None):
        super().__init__(parent or titlebar)
        self._titlebar = titlebar
        self.setObjectName("TitleBarCloseButton")
        self._is_hovered = False
        self._is_pressed = False
        self._icon_normal = QIcon()
        self._icon_hover = QIcon()
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            "QPushButton#TitleBarCloseButton { background: transparent; border: none; margin: 0px; padding: 0px; }"
        )

    def set_icons(self, normal_icon: QIcon, hover_icon: QIcon = None):
        self._icon_normal = normal_icon
        self._icon_hover = hover_icon if hover_icon is not None else normal_icon
        self.update()

    def _is_macos(self) -> bool:
        if hasattr(self, "_titlebar") and getattr(self._titlebar, "_button_style", "") == "macos":
            return True
        return False

    def get_effective_radius(self) -> float:
        if self._is_macos():
            return 6.0
        # Check window maximization state first
        win = self.window()
        if win and hasattr(win, "isMaximized") and win.isMaximized():
            return 0.0
        p_win = getattr(self._titlebar, "parent_window", None)
        if p_win:
            if hasattr(p_win, "isMaximized") and p_win.isMaximized():
                return 0.0
            if getattr(p_win, "_current_is_max_state", False):
                return 0.0
            if hasattr(p_win, "_border_radius"):
                return float(p_win._border_radius)

        # Fallback to ThemeEngine token if present
        try:
            from monkeyqt.themes.engine import ThemeEngine
            r_val = ThemeEngine.get("--radius", "8px")
            if isinstance(r_val, str) and r_val.endswith("px"):
                return float(r_val[:-2])
            return float(r_val)
        except Exception:
            pass
        return 8.0

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        if self.parentWidget():
            self.parentWidget().update()
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        if self._is_macos():
            super().paintEvent(event)
            return

        painter = QPainter(self)
        w = float(self.width())
        h = float(self.height())
        r = self.get_effective_radius()

        if self._is_hovered or self._is_pressed:
            bg_color = QColor("#c42b1c" if self._is_pressed else "#e81123")
            # 1. Clear any parent titlebar background using Source mode to prevent edge leak
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            if r <= 0.0:
                painter.fillRect(self.rect(), bg_color)
            else:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                path = QPainterPath()
                path.moveTo(0, 0)
                path.lineTo(w - r, 0)
                path.arcTo(QRectF(w - 2 * r, 0, 2 * r, 2 * r), 90, -90)
                path.lineTo(w, h)
                path.lineTo(0, h)
                path.closeSubpath()
                painter.fillPath(path, bg_color)

            # Draw "X" icon in pure white
            target_icon = self._icon_hover if not self._icon_hover.isNull() else self._icon_normal
            if not target_icon.isNull():
                icon_s = 12
                ix = int((w - icon_s) / 2)
                iy = int((h - icon_s) / 2)
                target_icon.paint(painter, QRect(ix, iy, icon_s, icon_s))
        else:
            # Normal: transparent background, draw normal icon
            if not self._icon_normal.isNull():
                icon_s = 12
                ix = int((w - icon_s) / 2)
                iy = int((h - icon_s) / 2)
                self._icon_normal.paint(painter, QRect(ix, iy, icon_s, icon_s))

        painter.end()


class MkTitleBar(MkQWidget):
    """
    Customizable title bar component mimicking modern UI designs.
    Supports presets: 'default', 'shadcn', 'ida', 'sunlogin', 'soda', 'ide'
    """
    
    closeClicked = Signal()
    minimizeClicked = Signal()
    maximizeClicked = Signal()
    
    def __init__(self, parent=None, preset="default"):
        super().__init__(parent)
        self.parent_window = parent
        self._preset = preset
        
        # Custom properties that can override presets
        self._bg_color = None
        self._text_color = None
        self._hover_color = None
        self._height = 40
        self._button_style = "windows"  # "windows" (right controls) or "macos" (left traffic lights)
        self._title_visible = True
        self._icon_visible = True
        self._border_bottom = ""
        
        # Dragging state
        self._drag_pos = None
        
        # Layouts
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 0, 0, 0)
        self.main_layout.setSpacing(10)
        
        # UI Elements
        self.icon_label = QLabel()
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Medium))
        
        # Container for center custom widgets
        self.center_container = QWidget()
        self.center_layout = QHBoxLayout(self.center_container)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(6)
        
        # Window control buttons
        self.btn_min = QPushButton()
        self.btn_min.setObjectName("TitleBarMinButton")
        self.btn_max = QPushButton()
        self.btn_max.setObjectName("TitleBarMaxButton")
        self.btn_close = MkTitleBarCloseButton(self)
        self.btn_close.setObjectName("TitleBarCloseButton")
        
        self.btn_min.setFixedSize(28, 28)
        self.btn_max.setFixedSize(28, 28)
        self.btn_close.setFixedSize(28, 28)
        
        # Connect signals
        self.btn_min.clicked.connect(self._on_minimize)
        self.btn_max.clicked.connect(self._on_maximize)
        self.btn_close.clicked.connect(self._on_close)
        
        # Set cursor
        self.btn_min.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.apply_preset(preset)
        self.rebuild_layout()
        
        # Connect to ThemeEngine for dynamic style reactivity
        try:
            from monkeyqt.themes.engine import ThemeEngine
            ThemeEngine.instance().themeChanged.connect(self._on_theme_changed)
        except Exception:
            pass

    def _on_theme_changed(self, theme_name: str = ""):
        self.apply_theme_colors()
        self.update()

    def set_title(self, title: str):
        self.title_label.setText(title)

    def set_icon(self, pixmap):
        if pixmap:
            self.icon_label.setPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.icon_label.setVisible(self._icon_visible)
        else:
            self.icon_label.setVisible(False)

    def apply_preset(self, preset: str):
        self._preset = preset
        
        # Clear any dynamic widgets in the center
        while self.center_layout.count():
            item = self.center_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if preset == "shadcn":
            self._bg_color = "#ffffff" if not self._is_dark_theme() else "#09090b"
            self._text_color = "#09090b" if not self._is_dark_theme() else "#fafafa"
            self._hover_color = "#f4f4f5" if not self._is_dark_theme() else "#27272a"
            self._height = 40
            self._button_style = "windows"
            self.title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
            self._border_bottom = f"1px solid {'#e4e4e7' if not self._is_dark_theme() else '#27272a'}"
            
        elif preset == "ida":
            self._bg_color = "#2d2d2d"
            self._text_color = "#d3d3d3"
            self._hover_color = "#3f3f3f"
            self._height = 36
            self._button_style = "windows"
            self.title_label.setFont(QFont("Consolas", 9))
            self._border_bottom = "1px solid #3f3f3f"
            
            # Decorative: Show a green ready status indicator and a code-style path
            status_dot = QFrame()
            status_dot.setFixedSize(8, 8)
            status_dot.setStyleSheet("background-color: #2ec872; border-radius: 4px;")
            self.center_layout.addWidget(status_dot)
            
            env_label = QLabel("[IDA Pro - Active Session]")
            env_label.setStyleSheet("color: #858585; font-family: Consolas; font-size: 11px;")
            self.center_layout.addWidget(env_label)
            self.center_layout.addStretch()
            
        elif preset == "sunlogin":
            self._bg_color = "#1e1f22"  # Dark Theme
            self._text_color = "#ffffff"
            self._hover_color = "#2d3035"
            self._height = 48
            self._button_style = "windows"
            self.title_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
            
            # Sunlogin Search Input decoration
            search_input = QLineEdit()
            search_input.setPlaceholderText("输入设备识别码以远程控制...")
            search_input.setFixedWidth(220)
            search_input.setStyleSheet("""
                QLineEdit {
                    background-color: #2b2d30;
                    border: 1px solid #3f4247;
                    border-radius: 4px;
                    padding: 2px 8px;
                    color: #cfd3dc;
                    font-size: 11px;
                }
                QLineEdit:focus {
                    border-color: #ff6b1a;
                }
            """)
            self.center_layout.addStretch()
            self.center_layout.addWidget(search_input)
            self.center_layout.addStretch()
            
        elif preset == "soda":
            # Soda Music style: Translucent acrylic look with macOS buttons on the left
            self._bg_color = "rgba(18, 18, 18, 0.85)"
            self._text_color = "#ffffff"
            self._hover_color = "rgba(255, 255, 255, 0.15)"
            self._height = 56
            self._button_style = "macos"
            self.title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.DemiBold))
            
            # Central search bar mimicking music app
            search_input = QLineEdit()
            search_input.setPlaceholderText("🔍 搜索音乐、歌手、歌单...")
            search_input.setFixedWidth(260)
            search_input.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: none;
                    border-radius: 14px;
                    padding: 4px 12px;
                    color: #eaeaea;
                    font-size: 12px;
                }
            """)
            self.center_layout.addStretch()
            self.center_layout.addWidget(search_input)
            self.center_layout.addStretch()
            
        elif preset == "ide":
            self._bg_color = "#1e1e2e"  # Deep Catppuccin / IDE Mocha style
            self._text_color = "#cdd6f4"
            self._hover_color = "#313244"
            self._height = 42
            self._button_style = "windows"
            self.title_label.setFont(QFont("Outfit", 9, QFont.Weight.Medium))
            self._border_bottom = "1px solid #313244"
            
        else:  # "default"
            self._bg_color = None
            self._text_color = None
            self._hover_color = None
            self._height = 40
            self._button_style = "windows"
            self.title_label.setFont(QFont("Microsoft YaHei", 9))
            self._border_bottom = ""
            
        self.apply_theme_colors()

    def _is_dark_theme(self):
        try:
            from monkeyqt.themes.engine import ThemeEngine
            if ThemeEngine.current_theme():
                return ThemeEngine.is_dark()
        except Exception:
            pass
        if self._bg_color:
            try:
                from monkeyqt.themes.style_utils import luminance
                return luminance(self._bg_color) < 0.5
            except Exception:
                pass
        return False

    def _get_effective_colors(self):
        """Dynamically resolve background, text, and hover colors based on preset and ThemeEngine."""
        theme_active = False
        tokens = {}
        is_dark = False
        try:
            from monkeyqt.themes.engine import ThemeEngine
            if ThemeEngine.current_theme():
                theme_active = True
                tokens = ThemeEngine.current_tokens()
                is_dark = ThemeEngine.is_dark()
        except Exception:
            pass

        # 1. Background color
        if self._bg_color is not None:
            bg = self._bg_color
        elif theme_active:
            follows_content = bool(self.property("mkContentAlignedTitleBar"))
            if not follows_content and self.parent_window:
                follows_content = bool(getattr(self.parent_window, "_sidebar_full_height", False))
            
            if follows_content and not ThemeEngine.has_override("--titlebar-bg"):
                bg = tokens.get("--bg", "#ffffff")
            else:
                bg = tokens.get("--chrome-surface", tokens.get("--surface", "#ffffff"))
        else:
            bg = "#ffffff"

        # 2. Text color
        if self._text_color is not None:
            text = self._text_color
        elif theme_active:
            text = tokens.get("--fg", "#F8FAFC" if is_dark else "#0F172A")
        else:
            text = "#0f172a"

        # 3. Hover color for min/max buttons
        if self._hover_color is not None:
            hover = self._hover_color
        elif theme_active:
            hover = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.06)"
        else:
            hover = "#f1f5f9"

        return bg, text, hover

    def apply_theme_colors(self, is_max: bool | None = None):
        bg, text, hover = self._get_effective_colors()
        border_css = f"border-bottom: {self._border_bottom};" if hasattr(self, '_border_bottom') and self._border_bottom else ""
        
        # Calculate parent window's top-left and top-right corner radius to prevent visual overflow
        if is_max is None:
            is_max = False
            if self.parent_window and hasattr(self.parent_window, "window"):
                win = self.parent_window.window()
                if win and hasattr(win, "isMaximized"):
                    is_max = win.isMaximized()
            elif self.parent_window and hasattr(self.parent_window, "isMaximized"):
                is_max = self.parent_window.isMaximized()

        window_radius = 0 if is_max else getattr(self.parent_window, "_border_radius", 8)

        is_sidebar_full = False
        if self.parent_window and getattr(self.parent_window, "_sidebar_full_height", False):
            is_sidebar_full = True
        tl_radius = 0 if is_sidebar_full else window_radius
        tr_radius = window_radius

        self.setObjectName("MkTitleBar")
        self.setStyleSheet(f"""
            QWidget#MkTitleBar {{
                background-color: {bg};
                color: {text};
                {border_css}
                border-top-left-radius: {tl_radius}px;
                border-top-right-radius: {tr_radius}px;
            }}
            QLabel {{
                color: {text};
                background: transparent;
            }}
        """)
        
        # Style buttons based on style choice
        self.update_buttons(is_max=is_max)

    def _get_close_btn_stylesheet(self, window_radius: int) -> str:
        return f"""
            QPushButton {{ 
                background-color: transparent; 
                border: none; 
                border-top-right-radius: {window_radius}px;
                border-top-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                margin: 0px;
                padding: 0px;
            }}
            QPushButton:hover {{ 
                background-color: #e81123; 
                color: #ffffff; 
                border-top-right-radius: {window_radius}px;
                border-top-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                margin: 0px;
                padding: 0px;
            }}
            QPushButton:pressed {{ 
                background-color: #c42b1c; 
                color: #ffffff; 
                border-top-right-radius: {window_radius}px;
                border-top-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                margin: 0px;
                padding: 0px;
            }}
        """

    def set_maximized_state(self, is_max: bool):
        """Instantaneous, synchronous update of maximize button icon, titlebar radius, and close button radius."""
        if not hasattr(self, "_icon_max_restore") or not hasattr(self, "_icon_max_square"):
            self.update_buttons(is_max=is_max)
            return

        self.btn_max.setIcon(self._icon_max_restore if is_max else self._icon_max_square)
        self.btn_max.setToolTip("还原" if is_max else "最大化")

        window_radius = 0 if is_max else (getattr(self.parent_window, "_border_radius", 8) if self.parent_window else 8)
        if self._button_style != "macos":
            self.btn_close.update()

        bg, text, _ = self._get_effective_colors()
        border_css = f"border-bottom: {self._border_bottom};" if hasattr(self, '_border_bottom') and self._border_bottom else ""
        is_sidebar_full = False
        if self.parent_window and getattr(self.parent_window, "_sidebar_full_height", False):
            is_sidebar_full = True
        tl_radius = 0 if is_sidebar_full else window_radius
        tr_radius = window_radius
        self.setStyleSheet(f"""
            QWidget#MkTitleBar {{
                background-color: {bg};
                color: {text};
                {border_css}
                border-top-left-radius: {tl_radius}px;
                border-top-right-radius: {tr_radius}px;
            }}
            QLabel {{
                color: {text};
                background: transparent;
            }}
        """)

    def update_buttons(self, is_max: bool | None = None):
        bg, text_color, hover_color = self._get_effective_colors()
        
        # High contrast icons with pre-cached references for zero-delay switching
        self._icon_min = MkPhosphorIcon.get_icon("minus", text_color, text_color, 12)
        self._icon_close = MkPhosphorIcon.get_icon("x", text_color, "#ffffff" if self._preset != "soda" else text_color, 12)
        self._icon_close_hover = MkPhosphorIcon.get_icon("x", "#ffffff", "#ffffff", 12)
        self._icon_max_square = MkPhosphorIcon.get_icon("square", text_color, text_color, 12)
        self._icon_max_restore = MkPhosphorIcon.get_icon("restore", text_color, text_color, 12)
        
        if is_max is None:
            is_max = False
            if self.parent_window:
                win = self.parent_window.window() if hasattr(self.parent_window, "window") else self.parent_window
                is_max = win.isMaximized() if (win and hasattr(win, "isMaximized")) else False
        
        self.btn_min.setIcon(self._icon_min)
        self.btn_max.setIcon(self._icon_max_restore if is_max else self._icon_max_square)
        self.btn_close.setIcon(self._icon_close)
        self.btn_max.setToolTip("还原" if is_max else "最大化")
        
        if self._button_style == "macos":
            # Traffic Light style for macOS
            self.btn_close.setIcon(QIcon())
            self.btn_min.setIcon(QIcon())
            self.btn_max.setIcon(QIcon())
            
            self.btn_close.setStyleSheet(f"""
                QPushButton {{ background-color: #ff5f56; border: none; border-radius: 6px; }}
                QPushButton:hover {{ background-color: #e0443e; }}
            """)
            self.btn_min.setStyleSheet(f"""
                QPushButton {{ background-color: #ffbd2e; border: none; border-radius: 6px; }}
                QPushButton:hover {{ background-color: #dfa220; }}
            """)
            self.btn_max.setStyleSheet(f"""
                QPushButton {{ background-color: #27c93f; border: none; border-radius: 6px; }}
                QPushButton:hover {{ background-color: #1aab30; }}
            """)
            
            self.btn_close.setFixedSize(12, 12)
            self.btn_min.setFixedSize(12, 12)
            self.btn_max.setFixedSize(12, 12)
        else:
            # Standard Windows Style — full-height, flush buttons like native chrome
            btn_h = self._height
            btn_w = 46
            self.btn_min.setFixedSize(btn_w, btn_h)
            self.btn_max.setFixedSize(btn_w, btn_h)
            self.btn_close.setFixedSize(btn_w, btn_h)
            
            # Explicitly set icon size to prevent Qt from scaling small bitmaps, maintaining pixel sharpness
            from PySide6.QtCore import QSize
            self.btn_min.setIconSize(QSize(12, 12))
            self.btn_max.setIconSize(QSize(12, 12))
            self.btn_close.setIconSize(QSize(12, 12))

            window_radius = 0 if is_max else (getattr(self.parent_window, "_border_radius", 8) if self.parent_window else 8)
            pressed_color = "rgba(255, 255, 255, 0.14)" if self._is_dark_theme() else "rgba(0, 0, 0, 0.12)"
            
            self.btn_min.setStyleSheet(f"""
                QPushButton {{ background-color: transparent; border: none; border-radius: 0px; margin: 0px; padding: 0px; }}
                QPushButton:hover {{ background-color: {hover_color}; }}
                QPushButton:pressed {{ background-color: {pressed_color}; }}
            """)
            self.btn_max.setStyleSheet(f"""
                QPushButton {{ background-color: transparent; border: none; border-radius: 0px; margin: 0px; padding: 0px; }}
                QPushButton:hover {{ background-color: {hover_color}; }}
                QPushButton:pressed {{ background-color: {pressed_color}; }}
            """)
            if isinstance(self.btn_close, MkTitleBarCloseButton):
                self.btn_close.set_icons(self._icon_close, self._icon_close_hover)
                self.btn_close.setStyleSheet("QPushButton#TitleBarCloseButton { background-color: transparent; border: none; margin: 0px; padding: 0px; }")
                self.btn_close.update()
            else:
                self.btn_close.setStyleSheet(self._get_close_btn_stylesheet(window_radius))

    def rebuild_layout(self):
        # Remove all items first — handle both widgets and sub-layouts
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.layout():
                # Clear sub-layout widgets (don't delete the buttons themselves)
                sub = item.layout()
                while sub.count():
                    sub.takeAt(0)
        
        # Build layout according to macOS or Windows styling
        if self._button_style == "macos":
            # Buttons on the left, then icon, title, center container
            # Spacing for macos traffic lights
            mac_buttons_layout = QHBoxLayout()
            mac_buttons_layout.setContentsMargins(6, 0, 6, 0)
            mac_buttons_layout.setSpacing(6)
            mac_buttons_layout.addWidget(self.btn_close)
            mac_buttons_layout.addWidget(self.btn_min)
            mac_buttons_layout.addWidget(self.btn_max)
            
            self.main_layout.addLayout(mac_buttons_layout)
            self.main_layout.addWidget(self.icon_label)
            self.main_layout.addWidget(self.title_label)
            self.main_layout.addWidget(self.center_container, stretch=1)
        else:
            # Icon, Title, Center Container, then Buttons flush-right
            self.main_layout.addWidget(self.icon_label)
            self.main_layout.addWidget(self.title_label)
            self.main_layout.addWidget(self.center_container, stretch=1)
            
            # Group buttons with 0 spacing for native Windows chrome look
            win_buttons_layout = QHBoxLayout()
            win_buttons_layout.setContentsMargins(0, 0, 0, 0)
            win_buttons_layout.setSpacing(0)
            win_buttons_layout.addWidget(self.btn_min)
            win_buttons_layout.addWidget(self.btn_max)
            win_buttons_layout.addWidget(self.btn_close)
            self.main_layout.addLayout(win_buttons_layout)

        # Enforce the height — sizeHint() alone is only advisory
        self.setFixedHeight(self._height)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            window = self.window()
            if window.isMaximized():
                # If moving a maximized window, restore it first
                # Calculate proper ratio so it doesn't jump
                normal_geom = getattr(window, "_normal_geometry", None)
                if normal_geom and normal_geom.isValid():
                    normal_width = normal_geom.width()
                else:
                    normal_width = window.normalGeometry().width()
                click_x_ratio = event.position().x() / max(1, self.width())
                
                window.showNormal()
                
                # Move window under mouse cursor
                new_x = event.globalPosition().toPoint().x() - int(normal_width * click_x_ratio)
                new_y = event.globalPosition().toPoint().y() - event.position().y()
                if hasattr(window, "_get_safe_normal_geometry"):
                    safe = window._get_safe_normal_geometry(QRect(new_x, new_y, window.width(), window.height()))
                    new_x, new_y = safe.x(), safe.y()
                window.move(new_x, new_y)
            else:
                window.move(window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_maximize()
            event.accept()

    def sizeHint(self) -> QSize:
        return QSize(100, self._height)

    def _on_minimize(self):
        self.minimizeClicked.emit()
        if self.parent_window:
            self.parent_window.showMinimized()

    def _on_maximize(self):
        self.maximizeClicked.emit()
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
            else:
                self.parent_window.showMaximized()
            self.update_buttons()

    def _on_close(self):
        self.closeClicked.emit()
        if self.parent_window:
            self.parent_window.close()

# Custom resize direction flags
RESIZE_NONE = 0
RESIZE_LEFT = 1
RESIZE_RIGHT = 2
RESIZE_TOP = 4
RESIZE_BOTTOM = 8

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    class _MSG(ctypes.Structure):
        _fields_ = [
            ("hwnd", wintypes.HWND),
            ("message", wintypes.UINT),
            ("wParam", wintypes.WPARAM),
            ("lParam", wintypes.LPARAM),
            ("time", wintypes.DWORD),
            ("pt", wintypes.POINT),
        ]

class MkWindow(QMainWindow):
    """
    Standard window class for MonkeyQt supporting native frames or custom title bars
    with border resizing, custom presets, and drop shadows.
    """
    
    def __init__(
        self,
        use_custom_title_bar=True,
        preset="default",
        parent=None,
        sidebar_full_height=False,
        auto_scroll=True,
    ):
        super().__init__(parent)
        self.use_custom_title_bar = use_custom_title_bar
        self._preset = preset
        self._sidebar_full_height = bool(sidebar_full_height)
        self._auto_scroll = bool(auto_scroll)
        self.content_scroll_area = None
        self._auto_content_container = None
        self._close_behavior = "close"  # "close" or "hide"
        self._border_radius = 8
        self._normal_geometry = None
        self._is_maximizing = False
        
        # Resizing states
        self._resize_margin = 8
        self._resizing_dir = RESIZE_NONE
        self._resize_start_pos = None
        self._resize_start_geometry = None
        
        # Structure elements
        self._shadow_effect = None
        self.shadow_layout = None
        self.outer_layout = None
        self.container_frame = None
        self.container_layout = None
        self.titlebar = None
        self.user_central_widget = None
        self._desktop_shell = None
        self._desktop_shell_layout = None
        self._sidebar_host = None
        self._sidebar_host_layout = None
        self._content_host = None
        self._content_host_layout = None
        self._promoted_sidebar = None
        self._sidebar_source_layout = None
        self._sidebar_source_index = -1
        
        self.setMouseTracking(True)
        
        if self.use_custom_title_bar:
            self.init_custom_frame()
        else:
            self.init_native_frame()

        # Connect to ThemeEngine for dynamic style updates
        try:
            from monkeyqt.themes.engine import ThemeEngine
            ThemeEngine.instance().themeChanged.connect(self._on_theme_changed)
        except Exception:
            pass

    def _on_theme_changed(self, theme_name: str = ""):
        self.update_style()
        if self.titlebar:
            self.titlebar.apply_theme_colors()
            self.titlebar.update_buttons()

    def init_native_frame(self):
        # Standard QMainWindow behavior
        self.setWindowFlags(Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

    def init_custom_frame(self):
        # Custom frameless behavior
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # 1. Root outer layout to support padding for drop shadow
        self._root_widget = QWidget(self)
        self._root_widget.setMouseTracking(True)
        self.shadow_layout = QVBoxLayout(self._root_widget)
        # Default to 0px margins to eliminate the 10px white gap and achieve flush titlebar/buttons
        self._use_zero_margins = True
        margin = 0 if self._use_zero_margins else 10
        self.shadow_layout.setContentsMargins(margin, margin, margin, margin)
        self.shadow_layout.setSpacing(0)
        
        # 2. Main container widget that has styling (border, radius, background)
        self.container_frame = QWidget(self._root_widget)
        self.container_frame.setObjectName("MkWindowContainer")
        self.container_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.container_frame.setMouseTracking(True)
        
        self.container_layout = QVBoxLayout(self.container_frame)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        # Desktop shell. In the default mode the hidden sidebar host takes no
        # space, so the layout is identical to the original top/bottom layout.
        self._desktop_shell = QWidget(self.container_frame)
        self._desktop_shell.setObjectName("MkWindowDesktopShell")
        self._desktop_shell.setProperty("mkDesktopShell", True)
        self._desktop_shell_layout = QHBoxLayout(self._desktop_shell)
        self._desktop_shell_layout.setContentsMargins(0, 0, 0, 0)
        self._desktop_shell_layout.setSpacing(0)

        self._sidebar_host = QWidget(self._desktop_shell)
        self._sidebar_host.setObjectName("MkWindowSidebarHost")
        self._sidebar_host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._sidebar_host.setProperty("mkSidebarHost", True)
        self._sidebar_host.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        self._sidebar_host_layout = QVBoxLayout(self._sidebar_host)
        self._sidebar_host_layout.setContentsMargins(0, 0, 0, 0)
        self._sidebar_host_layout.setSpacing(0)
        self._sidebar_host.hide()

        self._content_host = QWidget(self._desktop_shell)
        self._content_host.setObjectName("MkWindowContentHost")
        self._content_host.setProperty("mkContentHost", True)
        self._content_host.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._content_host_layout = QVBoxLayout(self._content_host)
        self._content_host_layout.setContentsMargins(0, 0, 0, 0)
        self._content_host_layout.setSpacing(0)

        self._desktop_shell_layout.addWidget(self._sidebar_host)
        self._desktop_shell_layout.addWidget(self._content_host, stretch=1)
        self.container_layout.addWidget(self._desktop_shell, stretch=1)
        
        # Apply Shadow Effect (only if margins > 0, otherwise rely on OS/DWM shadow)
        self._shadow_effect = QGraphicsDropShadowEffect(self)
        self._shadow_effect.setBlurRadius(15)
        self._shadow_effect.setColor(QColor(0, 0, 0, 45))
        self._shadow_effect.setOffset(0, 4)
        if margin > 0:
            self.container_frame.setGraphicsEffect(self._shadow_effect)
        else:
            self._shadow_effect.setEnabled(False)
        
        # 3. Create Title Bar
        self.titlebar = MkTitleBar(self, preset=self._preset)
        self._sync_sidebar_mode_properties()
        self._content_host_layout.addWidget(self.titlebar)
        
        self.shadow_layout.addWidget(self.container_frame)
        super().setCentralWidget(self._root_widget)
        
        self.update_style()

    def set_preset(self, preset: str):
        self._preset = preset
        if self.titlebar:
            self.titlebar.apply_preset(preset)
            self.update_style()

    def set_close_behavior(self, behavior: str):
        if behavior in ["close", "hide"]:
            self._close_behavior = behavior

    def set_border_radius(self, radius: int):
        self._border_radius = radius
        self.update_style()

    def set_sidebar_full_height(self, enabled: bool):
        """
        Switch between the classic top title bar layout and a desktop layout
        where the sidebar occupies the full window height.

        The first direct MkMenu child in the central widget is detected
        automatically, so callers only need to toggle this one option.
        """
        self._sidebar_full_height = bool(enabled)
        self._sync_sidebar_mode_properties()
        self._apply_sidebar_layout()

    def _sync_sidebar_mode_properties(self):
        """Expose the desktop split mode to the global theme adapter."""
        if self.titlebar is None:
            return

        self.titlebar.setProperty(
            "mkContentAlignedTitleBar",
            self._sidebar_full_height,
        )
        self.titlebar.apply_theme_colors()
        style = self.titlebar.style()
        style.unpolish(self.titlebar)
        style.polish(self.titlebar)
        self.titlebar.update()

    def update_style(self, is_max: bool | None = None):
        if not self.use_custom_title_bar:
            return
            
        if is_max is None:
            is_max = self.isMaximized()
            
        self._current_is_max_state = is_max
        radius = 0 if is_max else self._border_radius
        
        from monkeyqt.themes.engine import ThemeEngine
        theme_active = bool(ThemeEngine.current_theme())
        tokens = ThemeEngine.current_tokens() if theme_active else {}
        is_dark = ThemeEngine.is_dark() if theme_active else (self._preset in ["ida", "sunlogin", "soda", "ide"])

        # Determine window background
        if theme_active:
            window_bg = tokens.get("--bg", "#ffffff")
        elif self._preset in ["ida", "sunlogin", "soda", "ide"]:
            window_bg = "#1e1e2e" if self._preset == "ide" else "#1e1f22" if self._preset == "sunlogin" else "#121212" if self._preset == "soda" else "#1a1a1a"
        elif self._preset == "shadcn":
            window_bg = "#ffffff"
        else:
            window_bg = "#f8fafc"

        # Determine border rule (no border when maximized, theme-aware border when windowed)
        if is_max:
            border_rule = "none"
        else:
            if theme_active:
                border_color = tokens.get("--border", "#303030" if is_dark else "#e2e8f0")
            elif self._preset == "shadcn":
                border_color = "#e4e4e7"
            elif self._preset == "ida":
                border_color = "#3f3f3f"
            elif self._preset == "ide":
                border_color = "#313244"
            else:
                border_color = "#e2e8f0"
            border_rule = f"1px solid {border_color}"

        if self.container_frame:
            self.container_frame.setStyleSheet(f"""
                QWidget#MkWindowContainer, QFrame#MkWindowContainer {{
                    background-color: {window_bg};
                    border: {border_rule};
                    border-radius: {radius}px;
                }}
                QWidget#MkWindowContainer[mk_maximized="true"], QFrame#MkWindowContainer[mk_maximized="true"] {{
                    border: none;
                    border-radius: 0px;
                }}
            """)
            self.container_frame.setProperty("mk_maximized", "true" if is_max else "false")

        # Eliminate sharp dead corners by coordinating outer boundary widget radii
        if self._sidebar_host is not None:
            self._sidebar_host.setStyleSheet(f"""
                QWidget#MkWindowSidebarHost {{
                    border-top-left-radius: {radius}px;
                    border-bottom-left-radius: {radius}px;
                    border-top-right-radius: 0px;
                    border-bottom-right-radius: 0px;
                }}
                QWidget#MkWindowSidebarHost[mk_maximized="true"] {{
                    border-top-left-radius: 0px;
                    border-bottom-left-radius: 0px;
                }}
            """)
            self._sidebar_host.setProperty("mk_maximized", "true" if is_max else "false")

        if self._content_host is not None:
            is_sidebar_full = bool(getattr(self, "_sidebar_full_height", False))
            bl_r = 0 if is_sidebar_full else radius
            self._content_host.setStyleSheet(f"""
                QWidget#MkWindowContentHost {{
                    border-bottom-right-radius: {radius}px;
                    border-bottom-left-radius: {bl_r}px;
                }}
                QWidget#MkWindowContentHost[mk_maximized="true"] {{
                    border-bottom-right-radius: 0px;
                    border-bottom-left-radius: 0px;
                }}
            """)
            self._content_host.setProperty("mk_maximized", "true" if is_max else "false")

        if self._desktop_shell is not None:
            self._desktop_shell.setStyleSheet(f"""
                QWidget#MkWindowDesktopShell {{
                    border-radius: {radius}px;
                }}
                QWidget#MkWindowDesktopShell[mk_maximized="true"] {{
                    border-radius: 0px;
                }}
            """)
            self._desktop_shell.setProperty("mk_maximized", "true" if is_max else "false")

        candidate_sidebar = self._promoted_sidebar
        if candidate_sidebar is None and self.user_central_widget is not None:
            info = self._find_sidebar_candidate(self.user_central_widget)
            if info:
                candidate_sidebar = info[0]

        if candidate_sidebar is not None:
            candidate_sidebar.setProperty("mk_maximized", "true" if is_max else "false")
            tl_r = radius if self._sidebar_full_height else 0
            if hasattr(candidate_sidebar, "inner_frame"):
                sb_bg = tokens.get("--sidebar-surface", tokens.get("--surface", "#f1f5f9")) if theme_active else "#f1f5f9"
                sb_border_right = f"1px solid {tokens.get('--border', '#e2e8f0')}" if theme_active else "none"
                if hasattr(candidate_sidebar, "_border_right_style") and candidate_sidebar._border_right_style:
                    sb_border_right = candidate_sidebar._border_right_style
                elif getattr(candidate_sidebar, "_border_right", None) == "none":
                    sb_border_right = "none"

                candidate_sidebar.inner_frame.setStyleSheet(f"""
                    QFrame#SidebarInnerFrame {{
                        background-color: {sb_bg};
                        border: none;
                        border-right: {sb_border_right};
                        border-top-left-radius: {tl_r}px;
                        border-bottom-left-radius: {radius}px;
                        border-top-right-radius: 0px;
                        border-bottom-right-radius: 0px;
                    }}
                    QFrame#SidebarInnerFrame[mk_maximized="true"] {{
                        border-top-left-radius: 0px;
                        border-bottom-left-radius: 0px;
                    }}
                """)
                candidate_sidebar.inner_frame.setProperty("mk_maximized", "true" if is_max else "false")

        if self.titlebar:
            self.titlebar.apply_theme_colors()
            self.titlebar.update_buttons(is_max=is_max)

    def setCentralWidget(self, widget: QWidget):
        if not self.use_custom_title_bar:
            super().setCentralWidget(widget)
            return
            
        # If custom frame, place the page under the title bar in the content
        # column. The sidebar can then be promoted beside this column.
        if self.user_central_widget:
            self._restore_promoted_sidebar()
            if self.content_scroll_area and self.content_scroll_area.widget() == self.user_central_widget:
                self.content_scroll_area.takeWidget()
            else:
                self._content_host_layout.removeWidget(self.user_central_widget)
            self.user_central_widget.deleteLater()
            
        self.user_central_widget = widget
        if widget:
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            widget.setMouseTracking(True)
            self._apply_sidebar_layout()
            
            needs_wrap = self._auto_scroll and not self._is_scrollable_target(widget)
            if needs_wrap:
                from monkeyqt.components.layout.scroll_area import MkScrollArea
                sidebar_info = self._find_sidebar_candidate(widget)
                if sidebar_info is not None and not self._sidebar_full_height:
                    # In non-full-height mode, sidebar is on the left, right widget is on the right.
                    # Wrap only the right widget in MkScrollArea so the sidebar does not scroll!
                    sidebar, s_layout, s_idx = sidebar_info
                    right_child = None
                    for idx in range(s_layout.count()):
                        child = s_layout.itemAt(idx).widget()
                        if child and child != sidebar and not self._is_scrollable_target(child):
                            right_child = child
                            break
                    if right_child:
                        s_layout.removeWidget(right_child)
                        if self.content_scroll_area is None:
                            self.content_scroll_area = MkScrollArea(widget)
                        self.content_scroll_area.setWidget(right_child)
                        s_layout.addWidget(self.content_scroll_area, stretch=1)
                    self._content_host_layout.addWidget(widget, stretch=1)
                else:
                    if self.content_scroll_area is None:
                        self.content_scroll_area = MkScrollArea(self._content_host)
                        self._content_host_layout.addWidget(self.content_scroll_area, stretch=1)
                    self.content_scroll_area.setWidget(widget)
                    self.content_scroll_area.show()
            else:
                if self.content_scroll_area is not None:
                    self.content_scroll_area.hide()
                self._content_host_layout.addWidget(widget, stretch=1)

            self._auto_detect_and_name_right_widget()
            self.update_style()

    def _is_scrollable_target(self, w: Optional[QWidget]) -> bool:
        """检查组件是否自身已具备滚动能力，避免在外部产生双重嵌套滚动条"""
        if w is None:
            return False
        from PySide6.QtWidgets import QAbstractScrollArea
        if isinstance(w, QAbstractScrollArea):
            return True
        if getattr(w, "_scrollable", False) is True:
            return True
        if hasattr(w, "is_scrollable") and callable(w.is_scrollable):
            try:
                if w.is_scrollable():
                    return True
            except Exception:
                pass
        return False

    def set_auto_scroll(self, enabled: bool):
        """Enable or disable automatic vertical scrolling for the content area."""
        self._auto_scroll = bool(enabled)
        if self.user_central_widget:
            w = self.user_central_widget
            self.user_central_widget = None
            self.setCentralWidget(w)

    def get_content_scroll_area(self):
        """Return the active MkScrollArea for the content area, if any."""
        return self.content_scroll_area

    def scroll_to_top(self):
        """Scroll the main content area smoothly to the top."""
        if self.content_scroll_area:
            self.content_scroll_area.scroll_to_top()

    def scroll_to_bottom(self):
        """Scroll the main content area to the bottom."""
        if self.content_scroll_area:
            self.content_scroll_area.scroll_to_bottom()

    def scroll_to_widget(self, target: QWidget, x_margin: int = 0, y_margin: int = 0):
        """Ensure the specified child widget is scrolled into view."""
        if self.content_scroll_area:
            self.content_scroll_area.scroll_to_widget(target, x_margin, y_margin)

    def add_widget(self, widget: QWidget, stretch: int = 0):
        """
        Directly add a child component/widget to MkWindow's main content area.
        Automatically sets up an adaptive scrollable container if no central widget exists.
        """
        if self._auto_content_container is None:
            from monkeyqt.components.layout.widget import MkQWidget
            self._auto_content_container = MkQWidget(role="transparent", layout="v", margins=20, spacing=15)
            self._auto_content_container.setObjectName("MkAutoContentContainer")
            self.setCentralWidget(self._auto_content_container)

        layout = self._auto_content_container.layout()
        if layout:
            layout.addWidget(widget, stretch)

    def add_stretch(self, stretch: int = 1):
        """Add stretch space to the automatic content container."""
        if self._auto_content_container is not None:
            layout = self._auto_content_container.layout()
            if layout:
                layout.addStretch(stretch)

    def add_layout(self, layout):
        """Add a sub-layout to the automatic content container."""
        if self._auto_content_container is None:
            from monkeyqt.components.layout.widget import MkQWidget
            self._auto_content_container = MkQWidget(role="transparent", layout="v", margins=20, spacing=15)
            self._auto_content_container.setObjectName("MkAutoContentContainer")
            self.setCentralWidget(self._auto_content_container)

        main_layout = self._auto_content_container.layout()
        if main_layout:
            main_layout.addLayout(layout)

    def _apply_sidebar_layout(self):
        if not self.use_custom_title_bar or not self.user_central_widget:
            return

        if not self._sidebar_full_height:
            self._restore_promoted_sidebar()
            return

        if self._promoted_sidebar is not None:
            return

        sidebar_info = self._find_sidebar_candidate(self.user_central_widget)
        if sidebar_info is None:
            return

        sidebar, source_layout, source_index = sidebar_info
        self._promoted_sidebar = sidebar
        self._sidebar_source_layout = source_layout
        self._sidebar_source_index = source_index

        source_layout.removeWidget(sidebar)
        sidebar.setParent(self._sidebar_host)
        sidebar.installEventFilter(self)
        self._sidebar_host_layout.addWidget(sidebar)
        self._sidebar_host.setFixedWidth(sidebar.width())
        self._sidebar_host.show()
        sidebar.show()
        self._sidebar_host.updateGeometry()
        self._desktop_shell.updateGeometry()
        self.update_style()

    def _restore_promoted_sidebar(self):
        sidebar = self._promoted_sidebar
        source_layout = self._sidebar_source_layout
        if sidebar is None:
            if self._sidebar_host:
                self._sidebar_host.hide()
            return

        self._sidebar_host_layout.removeWidget(sidebar)
        sidebar.removeEventFilter(self)
        sidebar.setParent(self.user_central_widget)

        if source_layout is not None:
            index = max(0, self._sidebar_source_index)
            if hasattr(source_layout, "insertWidget"):
                source_layout.insertWidget(index, sidebar)
            else:
                source_layout.addWidget(sidebar)

        sidebar.show()
        self._sidebar_host.hide()
        self._promoted_sidebar = None
        self._sidebar_source_layout = None
        self._sidebar_source_index = -1

    @staticmethod
    def _find_sidebar_candidate(widget: QWidget):
        layout = widget.layout()
        if layout is None:
            return None

        for index in range(layout.count()):
            candidate = layout.itemAt(index).widget()
            if candidate is None:
                continue

            class_name = candidate.__class__.__name__
            is_sidebar = (
                class_name == "MkMenu"
                or bool(candidate.property("mkSidebar"))
                or candidate.objectName() in {"MkMenu", "Sidebar", "AppSidebar"}
            )
            if is_sidebar:
                return candidate, layout, index

        return None

    def _auto_detect_and_name_right_widget(self):
        if not self.user_central_widget:
            return
            
        layout = self.user_central_widget.layout()
        if not layout:
            return
            
        sidebar = None
        sidebar_info = self._find_sidebar_candidate(self.user_central_widget)
        if sidebar_info:
            sidebar = sidebar_info[0]
            
        for index in range(layout.count()):
            item = layout.itemAt(index).widget()
            if item and item != sidebar:
                if not item.objectName():
                    item.setObjectName("MainRightWidget")
                    from monkeyqt.themes.adapter import apply_monkeyqt_theme
                    from monkeyqt.themes.engine import ThemeEngine
                    if ThemeEngine.current_theme():
                        item.setProperty("_mk_auto_theme_name", None)
                        apply_monkeyqt_theme(item)
                        item.setProperty("_mk_auto_theme_name", ThemeEngine.current_theme())
                break

    def eventFilter(self, watched, event):
        if (
            watched is self._promoted_sidebar
            and event.type() in {
                QEvent.Type.Resize,
                QEvent.Type.Show,
                QEvent.Type.LayoutRequest,
            }
        ):
            self._sidebar_host.setFixedWidth(watched.width())
            self._sidebar_host.updateGeometry()

        return super().eventFilter(watched, event)

    def setWindowTitle(self, title: str):
        super().setWindowTitle(title)
        if self.titlebar:
            self.titlebar.set_title(title)

    def setWindowIcon(self, icon: QIcon):
        super().setWindowIcon(icon)
        if self.titlebar:
            pixmap = icon.pixmap(32, 32)
            self.titlebar.set_icon(pixmap)

    # ── Titlebar Extras: Avatar Menu + History Navigation ──────────

    def enable_titlebar_extras(
        self,
        avatar=True,
        history_nav=True,
        user_name="",
        subtitle="",
        avatar_image="",
        avatar_size=32,
        avatar_actions=None,
        animation_duration=280,
        stack=None,
        nav_icon_only=False,
    ):
        """One-line API to add avatar menu and forward/back navigation to the title bar.

        Args:
            avatar: Whether to show the clickable avatar menu.
            history_nav: Whether to show forward/back navigation buttons.
            user_name: Display name shown in the avatar dropdown header.
            subtitle: Subtitle shown below the user name in the dropdown.
            avatar_image: Path to the avatar image file.
            avatar_size: Avatar circle size in pixels.
            avatar_actions: List of action dicts for the dropdown menu.
            animation_duration: Page slide animation duration in ms.
            stack: Explicit QStackedWidget to bind. If None, auto-detected.
            nav_icon_only: Whether the forward/back buttons should be icon-only (no background/hover effects).
        """
        if not self.use_custom_title_bar or not self.titlebar:
            return



        self.disable_titlebar_extras()

        target_stack = stack
        if target_stack is None and self.user_central_widget:
            target_stack = self._find_stacked_widget(self.user_central_widget)

        if target_stack is not None and not isinstance(target_stack, MkAnimatedStackedWidget):
            target_stack = self._upgrade_to_animated_stack(target_stack, animation_duration)

        self._extras_stack = target_stack

        self.titlebar_history_nav = None
        if history_nav and target_stack is not None:
            pages = self._build_page_map(target_stack)
            current_page = self._current_page_id(target_stack, pages)
            self.titlebar_history_nav = MkHistoryNavigation(
                stack=target_stack,
                pages=pages,
                initial_page=current_page,
                animation_duration=animation_duration,
                icon_only=nav_icon_only,
                parent=self.titlebar.center_container,
            )
            self.titlebar.center_layout.insertWidget(0, self.titlebar_history_nav)

        self.titlebar_avatar = None
        if avatar:
            default_actions = avatar_actions or [
                {"id": "profile", "text": "个人主页", "icon": "user"},
                {"id": "settings", "text": "设置", "icon": "gear"},
            ]
            self.titlebar_avatar = MkAvatarMenu(
                text=user_name[:2] if user_name else "U",
                image_path=avatar_image,
                shape="circle",
                size=avatar_size,
                user_name=user_name,
                subtitle=subtitle,
                actions=default_actions,
                parent=self.titlebar.center_container,
            )
            self.titlebar.center_layout.addStretch()
            self.titlebar.center_layout.addWidget(self.titlebar_avatar)
            self.titlebar.center_layout.addSpacing(8)
        elif self.titlebar_history_nav:
            self.titlebar.center_layout.addStretch()

        self._titlebar_extras_enabled = True

    def disable_titlebar_extras(self):
        """Remove avatar and history navigation from the title bar."""
        if not getattr(self, "_titlebar_extras_enabled", False):
            return

        if getattr(self, "titlebar_history_nav", None) is not None:
            self.titlebar.center_layout.removeWidget(self.titlebar_history_nav)
            self.titlebar_history_nav.setParent(None)
            self.titlebar_history_nav.deleteLater()
            self.titlebar_history_nav = None

        if getattr(self, "titlebar_avatar", None) is not None:
            self.titlebar.center_layout.removeWidget(self.titlebar_avatar)
            self.titlebar_avatar.setParent(None)
            self.titlebar_avatar.deleteLater()
            self.titlebar_avatar = None

        for i in range(self.titlebar.center_layout.count() - 1, -1, -1):
            item = self.titlebar.center_layout.itemAt(i)
            if item and item.spacerItem():
                self.titlebar.center_layout.removeItem(item)

        self._titlebar_extras_enabled = False
        self._extras_stack = None

    @staticmethod
    def _find_stacked_widget(widget):
        from PySide6.QtWidgets import QStackedWidget
        for child in widget.findChildren(QStackedWidget):
            return child
        return None

    @staticmethod
    def _upgrade_to_animated_stack(old_stack, animation_duration=280):
        from monkeyqt.components.navigation.history import MkAnimatedStackedWidget

        parent_layout = old_stack.parentWidget().layout() if old_stack.parentWidget() else None
        if parent_layout is None:
            return old_stack

        index = -1
        for i in range(parent_layout.count()):
            item = parent_layout.itemAt(i)
            if item and item.widget() is old_stack:
                index = i
                break

        if index < 0:
            return old_stack

        new_stack = MkAnimatedStackedWidget(
            parent=old_stack.parentWidget(),
            animation_duration=animation_duration,
        )

        widgets = []
        while old_stack.count() > 0:
            w = old_stack.widget(0)
            old_stack.removeWidget(w)
            widgets.append(w)

        for w in widgets:
            new_stack.addWidget(w)
        if widgets:
            new_stack.setCurrentIndex(0)

        new_stack.setObjectName(old_stack.objectName())
        new_stack.setStyleSheet(old_stack.styleSheet())

        parent_layout.removeWidget(old_stack)
        parent_layout.insertWidget(index, new_stack, stretch=1)
        old_stack.setParent(None)
        old_stack.deleteLater()

        return new_stack

    @staticmethod
    def _build_page_map(stack):
        pages = {}
        for i in range(stack.count()):
            w = stack.widget(i)
            name = w.objectName() or f"page_{i}"
            pages[name] = w
        return pages

    @staticmethod
    def _current_page_id(stack, pages):
        current = stack.currentWidget()
        for page_id, w in pages.items():
            if w is current:
                return page_id
        return None

    def _enable_native_corners(self, is_max: bool | None = None):
        import sys
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = getattr(self, "_mk_cached_hwnd", None)
                if hwnd is None:
                    hwnd = int(self.winId())
                    self._mk_cached_hwnd = hwnd
                if is_max is None:
                    is_max = self.isMaximized()
                # Windows 11 DWMWA_WINDOW_CORNER_PREFERENCE (33):
                # 1 = DWMWCP_DONOTROUND (Straight right angles, fills screen without rounding)
                # 2 = DWMWCP_ROUND (Standard Windows 11 rounded corners)
                # 3 = DWMWCP_ROUNDSMALL (Restrained Windows 11 rounded corners)
                pref = ctypes.c_int(1 if is_max else 2)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(pref), ctypes.sizeof(pref))

                border_color = ctypes.c_uint(0xFFFFFFFE)  # DWMWA_COLOR_NONE
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    34,  # DWMWA_BORDER_COLOR
                    ctypes.byref(border_color),
                    ctypes.sizeof(border_color),
                )
            except Exception:
                pass

    def _apply_window_state_immediate(self, is_max: bool, force: bool = False):
        try:
            if not force and getattr(self, "_current_is_max_state", None) == is_max:
                return
            self._current_is_max_state = is_max
            if self.use_custom_title_bar:
                margin = 0 if (is_max or getattr(self, "_use_zero_margins", True) or sys.platform == "win32") else 10
                if self.shadow_layout:
                    self.shadow_layout.setContentsMargins(margin, margin, margin, margin)
                if self.container_frame and self.container_frame.graphicsEffect():
                    self.container_frame.graphicsEffect().setEnabled(not is_max and margin > 0)
                if self._root_widget and self._root_widget.layout():
                    self._root_widget.layout().activate()

            # Fast dynamic property update: use 'mk_maximized'
            max_str = "true" if is_max else "false"
            for target in (
                self.container_frame,
                self._sidebar_host,
                getattr(self, "_content_host", None),
                getattr(self, "_desktop_shell", None),
            ):
                if target is not None:
                    target.setProperty("mk_maximized", max_str)
                    st = target.style()
                    st.unpolish(target)
                    st.polish(target)

            candidate_sidebar = self._promoted_sidebar
            if candidate_sidebar is None and self.user_central_widget is not None:
                info = self._find_sidebar_candidate(self.user_central_widget)
                if info:
                    candidate_sidebar = info[0]

            if candidate_sidebar is not None:
                candidate_sidebar.setProperty("mk_maximized", max_str)
                st = candidate_sidebar.style()
                st.unpolish(candidate_sidebar)
                st.polish(candidate_sidebar)
                if hasattr(candidate_sidebar, "inner_frame"):
                    candidate_sidebar.inner_frame.setProperty("mk_maximized", max_str)
                    st2 = candidate_sidebar.inner_frame.style()
                    st2.unpolish(candidate_sidebar.inner_frame)
                    st2.polish(candidate_sidebar.inner_frame)

            if self.titlebar:
                self.titlebar.set_maximized_state(is_max)

            self.update_style(is_max)
            self._enable_native_corners(is_max)
        except RuntimeError:
            pass

    def _get_safe_normal_geometry(self, geom=None) -> QRect:
        """
        Calculate a safe normal geometry that fits entirely within the screen availableGeometry.
        - Automatically centers if unpositioned ((0, 0) or unmapped).
        - Clamps dimensions to avoid exceeding screen work area.
        - Keeps all 4 window edges strictly inside the available area.
        """
        screen = self.screen() or QGuiApplication.primaryScreen()
        if not screen:
            return geom if (geom and geom.isValid()) else self.geometry()

        avail = screen.availableGeometry()
        if geom is None or not geom.isValid():
            geom = self.geometry()

        # Clamp width and height to available screen size
        w = min(geom.width(), int(avail.width() * 0.96))
        h = min(geom.height(), int(avail.height() * 0.92))

        # Check if unpositioned (e.g. at (0, 0) before being shown) or outside available area
        if (geom.x() == 0 and geom.y() == 0) or not avail.contains(geom.topLeft()):
            x = avail.x() + (avail.width() - w) // 2
            y = avail.y() + (avail.height() - h) // 2
        else:
            x = geom.x()
            y = geom.y()
            if x + w > avail.right():
                x = max(avail.left(), avail.right() - w)
            if y + h > avail.bottom():
                y = max(avail.top(), avail.bottom() - h)
            if x < avail.left():
                x = avail.left()
            if y < avail.top():
                y = avail.top()

        return QRect(x, y, w, h)

    def showMaximized(self):
        if not self.isMaximized():
            self._normal_geometry = self._get_safe_normal_geometry(self.geometry())
        self._is_maximizing = True
        self._apply_window_state_immediate(True, force=True)
        super().showMaximized()
        self._is_maximizing = False
        self._apply_window_state_immediate(True, force=True)

    def showNormal(self):
        self._apply_window_state_immediate(False, force=True)
        super().showNormal()
        safe_geo = self._get_safe_normal_geometry(self._normal_geometry)
        self.setGeometry(safe_geo)
        self._normal_geometry = safe_geo
        self._apply_window_state_immediate(False, force=True)

    def showEvent(self, event):
        super().showEvent(event)
        if not self.isMaximized():
            if self._normal_geometry is None or not self._normal_geometry.isValid():
                self._normal_geometry = self._get_safe_normal_geometry(self.geometry())
        is_max = True if getattr(self, "_is_maximizing", False) else self.isMaximized()
        self._apply_window_state_immediate(is_max, force=True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.use_custom_title_bar:
            is_max = True if getattr(self, "_is_maximizing", False) else self.isMaximized()
            if getattr(self, "_current_is_max_state", None) != is_max:
                self._apply_window_state_immediate(is_max, force=True)
            if not is_max and not getattr(self, "_is_maximizing", False):
                self._normal_geometry = self.geometry()

    def moveEvent(self, event):
        super().moveEvent(event)
        if not self.isMaximized() and not getattr(self, "_is_maximizing", False):
            self._normal_geometry = self.geometry()

    def nativeEvent(self, eventType, message):
        if sys.platform == "win32" and eventType == b"windows_generic_MSG" and self.use_custom_title_bar:
            try:
                msg = _MSG.from_address(int(message))
                if msg.message == 0x0084:  # WM_NCHITTEST
                    if self.isMaximized():
                        return super().nativeEvent(eventType, message)

                    rect = wintypes.RECT()
                    ctypes.windll.user32.GetWindowRect(msg.hwnd, ctypes.byref(rect))

                    x = wintypes.SHORT(msg.lParam & 0xFFFF).value
                    y = wintypes.SHORT((msg.lParam >> 16) & 0xFFFF).value

                    win_x = x - rect.left
                    win_y = y - rect.top
                    win_w = rect.right - rect.left
                    win_h = rect.bottom - rect.top

                    dpr = max(1.0, float(self.devicePixelRatio()))
                    margin = int(self._resize_margin * dpr)

                    # Check 4 corners first (corners take priority over borders)
                    if win_x <= margin and win_y <= margin:
                        return True, 13  # HTTOPLEFT
                    elif win_x >= win_w - margin and win_y <= margin:
                        return True, 14  # HTTOPRIGHT
                    elif win_x <= margin and win_y >= win_h - margin:
                        return True, 16  # HTBOTTOMLEFT
                    elif win_x >= win_w - margin and win_y >= win_h - margin:
                        return True, 17  # HTBOTTOMRIGHT

                    # Check 4 edges
                    elif win_x <= margin:
                        return True, 10  # HTLEFT
                    elif win_x >= win_w - margin:
                        return True, 11  # HTRIGHT
                    elif win_y <= margin:
                        return True, 12  # HTTOP
                    elif win_y >= win_h - margin:
                        return True, 15  # HTBOTTOM
            except Exception:
                pass

        try:
            return super().nativeEvent(eventType, message)
        except Exception:
            return False, 0

    def changeEvent(self, event: QEvent):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            is_max = self.isMaximized()
            if getattr(self, "_current_is_max_state", None) != is_max:
                self._apply_window_state_immediate(is_max)

    def _handle_window_state_change(self):
        self._apply_window_state_immediate(self.isMaximized())

    def closeEvent(self, event):
        if self._close_behavior == "hide":
            event.ignore()
            self.hide()
        else:
            event.accept()

    # --- Border Resizing Logic ---
    def mousePressEvent(self, event: QMouseEvent):
        if not self.use_custom_title_bar or self.isMaximized():
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            direction = self._get_resize_direction(event.position().toPoint())
            if direction != RESIZE_NONE:
                self._resizing_dir = direction
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geometry = self.geometry()
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.use_custom_title_bar or self.isMaximized():
            super().mouseMoveEvent(event)
            return

        if self._resizing_dir != RESIZE_NONE:
            delta = event.globalPosition().toPoint() - self._resize_start_pos
            geom = QRect(self._resize_start_geometry)
            min_size = self.minimumSizeHint()

            if self._resizing_dir & RESIZE_LEFT:
                new_width = geom.width() - delta.x()
                if new_width >= min_size.width():
                    geom.setLeft(geom.left() + delta.x())
            elif self._resizing_dir & RESIZE_RIGHT:
                new_width = geom.width() + delta.x()
                if new_width >= min_size.width():
                    geom.setRight(geom.right() + delta.x())

            if self._resizing_dir & RESIZE_TOP:
                new_height = geom.height() - delta.y()
                if new_height >= min_size.height():
                    geom.setTop(geom.top() + delta.y())
            elif self._resizing_dir & RESIZE_BOTTOM:
                new_height = geom.height() + delta.y()
                if new_height >= min_size.height():
                    geom.setBottom(geom.bottom() + delta.y())

            self.setGeometry(geom)
            event.accept()
            return

        direction = self._get_resize_direction(event.position().toPoint())
        self._update_cursor(direction)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._resizing_dir = RESIZE_NONE
        self.unsetCursor()
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if self._resizing_dir == RESIZE_NONE:
            self.unsetCursor()
        super().leaveEvent(event)

    def _get_resize_direction(self, pos: QPoint) -> int:
        direction = RESIZE_NONE
        w = self.width()
        h = self.height()
        margin = self._resize_margin
        offset = self.shadow_layout.contentsMargins().left() if self.shadow_layout else 0

        if pos.x() < margin + offset:
            direction |= RESIZE_LEFT
        elif pos.x() > w - margin - offset:
            direction |= RESIZE_RIGHT

        if pos.y() < margin + offset:
            direction |= RESIZE_TOP
        elif pos.y() > h - margin - offset:
            direction |= RESIZE_BOTTOM

        return direction

    def _update_cursor(self, direction: int):
        if direction == RESIZE_NONE:
            self.unsetCursor()
        elif (direction & RESIZE_LEFT and direction & RESIZE_TOP) or (direction & RESIZE_RIGHT and direction & RESIZE_BOTTOM):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif (direction & RESIZE_RIGHT and direction & RESIZE_TOP) or (direction & RESIZE_LEFT and direction & RESIZE_BOTTOM):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif direction & RESIZE_LEFT or direction & RESIZE_RIGHT:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif direction & RESIZE_TOP or direction & RESIZE_BOTTOM:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
