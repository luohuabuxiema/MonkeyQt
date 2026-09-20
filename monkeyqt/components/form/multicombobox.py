# -*- coding: utf-8 -*-
"""
@File ：multicombobox.py
@Desc ：Modern web-style multi-select combobox (checklist popup) component for PySide6.
"""
import time
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QRectF, QEvent
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from monkeyqt import MkCheckBox
from monkeyqt.components.layout.widget import MkQWidget
from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import parse_px, qcolor

class MkMultiComboItem(MkQWidget):
    """Container widget representing a single item in the checklist dropdown."""
    def __init__(self, checkbox, parent=None):
        super().__init__(parent)
        self.checkbox = checkbox
        self.checkbox.setParent(self)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)
        layout.addWidget(self.checkbox)
        
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.update_theme_style()

    def on_theme_changed(self, theme_name: str = ""):
        self.update_theme_style()

    def update_theme_style(self):
        t = ThemeEngine
        hover_bg = t.get('--surface-muted', '#f1f5f9') if not t.is_dark() else 'rgba(255, 255, 255, 0.08)'
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border-radius: 4px;
            }}
            QWidget:hover {{
                background-color: {hover_bg};
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.checkbox.toggle()
            event.accept()
        else:
            super().mousePressEvent(event)

class MkMultiComboPopup(MkQWidget):
    """
    无边框透明浮动卡片多选下拉弹窗 (Frameless Floating Card Checklist Dropdown)
    彻底消除 Windows 平台原生 HWND 方形黑角与锯齿遮挡，
    呈现媲美 Web/macOS 的真实抗锯齿圆角、柔和外发散阴影与高质感卡片。
    """
    MARGIN = 10

    def __init__(self, parent_combo):
        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.parent_combo = parent_combo
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        root_layout.setSpacing(0)

        # 核心浮动卡片
        self.card = QFrame(self)
        self.card.setObjectName("mkMultiComboCard")
        self._card_layout = QVBoxLayout(self.card)
        self._card_layout.setContentsMargins(4, 4, 4, 4)
        self._card_layout.setSpacing(0)

        # 弥散外阴影
        self.shadow = QGraphicsDropShadowEffect(self.card)
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(QColor(0, 0, 0, 38))
        self.card.setGraphicsEffect(self.shadow)

        root_layout.addWidget(self.card)

        # Scroll Area
        self.scroll_area = QScrollArea(self.card)
        self.scroll_area.setObjectName("MultiComboPopupScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.scroll_widget = QWidget(self.scroll_area)
        self.scroll_widget.setObjectName("scroll_widget")
        self.scroll_widget.setStyleSheet("QWidget#scroll_widget { background: transparent; }")

        self.list_layout = QVBoxLayout(self.scroll_widget)
        self.list_layout.setContentsMargins(2, 2, 2, 2)
        self.list_layout.setSpacing(2)
        self.list_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_widget)
        self._card_layout.addWidget(self.scroll_area)

        self.items = []
        self.update_theme_style()

    def update_theme_style(self):
        t = ThemeEngine
        is_dark = t.is_dark()
        surface = t.get("--surface", "#FFFFFF") if not is_dark else t.get("--surface", "#18181B")
        border = t.get("--border", "#E2E8F0") if not is_dark else t.get("--border", "#3F3F46")
        radius = parse_px(t.get("--radius", "8px"), 8, 0, 20)

        if t.is_brutal() or t.is_pixel():
            self.shadow.setEnabled(False)
            card_border = "2px solid #000000"
            card_radius = 0
            card_bg = "#FFFFFF"
        else:
            self.shadow.setEnabled(True)
            shadow_color = QColor(0, 0, 0, 130) if is_dark else QColor(0, 0, 0, 38)
            self.shadow.setColor(shadow_color)
            self.shadow.setBlurRadius(20)
            self.shadow.setOffset(0, 4)
            card_border = f"1px solid {t.get('--glass-border', border) if t.is_glass() else border}"
            card_radius = radius
            card_bg = surface

        self.card.setStyleSheet(f"""
            QFrame#mkMultiComboCard {{
                background-color: {card_bg};
                border: {card_border};
                border-radius: {card_radius}px;
            }}
        """)

        # 统一封装美化的滚动条（扁平微型胶囊、无上下箭头、自适应主题深浅）
        thumb = "rgba(255, 255, 255, 0.25)" if is_dark else "rgba(148, 163, 184, 0.5)"
        thumb_hover = "rgba(255, 255, 255, 0.45)" if is_dark else "rgba(148, 163, 184, 0.8)"
        self.scroll_area.setStyleSheet(f"""
            QScrollArea#MultiComboPopupScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin: 4px 2px 4px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {thumb};
                min-height: 24px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {thumb_hover};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
                border: none;
                height: 0px;
                width: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        for data, text, chk, item_widget in getattr(self, "items", []):
            if hasattr(item_widget, "update_theme_style"):
                item_widget.update_theme_style()

    def add_item(self, text, data):
        chk = MkCheckBox(text, self.scroll_widget)
        chk.mk_size = "small"

        item_widget = MkMultiComboItem(chk, self.scroll_widget)
        self.list_layout.insertWidget(self.list_layout.count() - 1, item_widget)

        self.items.append((data, text, chk, item_widget))
        chk.stateChanged.connect(self.parent_combo._on_item_state_changed)

    def clear(self):
        for data, text, chk, item_widget in self.items:
            self.list_layout.removeWidget(item_widget)
            item_widget.deleteLater()
        self.items.clear()

    def show_popup(self):
        if not self.items:
            return

        combo = self.parent_combo
        item_count = len(self.items)
        content_h = min(220, item_count * 32 + 10)
        total_h = content_h + self.MARGIN * 2
        card_w = combo.width()
        total_w = card_w + self.MARGIN * 2
        self.resize(total_w, total_h)

        screen = combo.screen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)
        global_pos = combo.mapToGlobal(QPoint(0, 0))

        space_below = avail.bottom() - (global_pos.y() + combo.height())
        space_above = global_pos.y() - avail.top()

        if space_below < content_h + 10 and space_above > space_below:
            popup_y = global_pos.y() - total_h + self.MARGIN - 4
        else:
            popup_y = global_pos.y() + combo.height() - self.MARGIN + 4

        popup_x = global_pos.x() - self.MARGIN
        if popup_x + total_w > avail.right():
            popup_x = avail.right() - total_w
        if popup_x < avail.left():
            popup_x = avail.left()

        self.move(popup_x, popup_y)
        self.show()
        self.raise_()
        self.activateWindow()

    def hideEvent(self, event):
        self.parent_combo._last_close_time = time.time()
        self.parent_combo.setProperty("focused", "false")
        self.parent_combo.style().unpolish(self.parent_combo)
        self.parent_combo.style().polish(self.parent_combo)
        self.parent_combo.update()
        super().hideEvent(event)

class MkMultiComboBox(QFrame):
    """
    MkMultiComboBox - Element Plus styled multi-select dropdown.
    Displays selected options in a horizontal scroll area face, showing checklist popover on click.
    """
    selectionChanged = Signal(list)
    
    def __init__(self, placeholder="默认检测所有类别", parent=None):
        from PySide6.QtWidgets import QWidget
        if isinstance(placeholder, QWidget):
            parent = placeholder
            placeholder = "默认检测所有类别"
            
        super().__init__(parent)
        self.setObjectName("combo_frame")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        
        self._placeholder = placeholder
        self._last_close_time = 0
        self._hovered = False
        self.setProperty("focused", "false")
        
        # Main Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 28, 2) # Extra right padding for chevron arrow
        layout.setSpacing(0)
        
        # Scroll Area for the selected text labels
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("MultiComboFaceScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Beautified horizontal scrollbar style
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:horizontal {
                background: #f1f5f9;
                height: 6px;
                margin: 0px;
                border-radius: 3px;
            }
            QScrollBar::handle:horizontal {
                background: #cbd5e1;
                min-width: 15px;
                border-radius: 3px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
                border: none;
                width: 0px;
            }
        """)
        
        # Content label for text display
        self.text_label = QLabel(self.scroll_area)
        self.text_label.setObjectName("text_label")
        self.text_label.setWordWrap(False)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.text_label.setContentsMargins(4, 0, 0, 0)
        self.text_label.setStyleSheet("""
            QLabel#text_label {
                color: #94a3b8;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 13px;
                background: transparent;
                border: none;
            }
        """)
        self.text_label.setText(placeholder)
        
        self.scroll_area.setWidget(self.text_label)
        self._sync_text_label_geometry()
        layout.addWidget(self.scroll_area)
        
        # Setup popup
        self.popup = MkMultiComboPopup(self)
        
        ThemeEngine.instance().themeChanged.connect(self.update_theme_style)
        self.update_theme_style()
        
        # Install event filters to handle clicks on child components
        self.scroll_area.installEventFilter(self)
        self.scroll_area.viewport().installEventFilter(self)
        self.text_label.installEventFilter(self)

    def update_theme_style(self, style_name: str = None):
        t = ThemeEngine
        is_dark = t.is_dark()
        surface = t.get("--surface", "#FFFFFF")
        border = t.get("--border", "#E2E8F0")
        radius = parse_px(t.get("--radius", "6px"), 6, 0, 20)
        focus_border = t.get("--input-focus-border", "#FFFFFF" if is_dark else "#0F172A")
        hover_border = t.get("--input-hover-border", "rgba(255, 255, 255, 0.40)" if is_dark else "#94A3B8")

        self.setStyleSheet("""
            QFrame#combo_frame {
                background: transparent;
                border: none;
                min-height: 32px;
                max-height: 32px;
            }
        """)
        scroll_thumb = "rgba(255, 255, 255, 0.25)" if is_dark else "rgba(148, 163, 184, 0.5)"
        scroll_hover = "rgba(255, 255, 255, 0.45)" if is_dark else "rgba(148, 163, 184, 0.8)"
        self.scroll_area.setStyleSheet(f"""
            QScrollArea#MultiComboFaceScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:horizontal {{
                background: transparent;
                height: 5px;
                margin: 0px;
                border-radius: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {scroll_thumb};
                min-width: 15px;
                border-radius: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {scroll_hover};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                background: none;
                border: none;
                width: 0px;
                height: 0px;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)
        self._update_text()
        if hasattr(self, "popup") and hasattr(self.popup, "update_theme_style"):
            self.popup.update_theme_style()
        self.update()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self._handle_click()
                return True
        return super().eventFilter(obj, event)

    def _handle_click(self):
        # Debounce popup reopen clicks
        now = time.time()
        if now - self._last_close_time < 0.15:
            return
            
        self.setProperty("focused", "true")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        
        self.popup.show_popup()

    def show_popup(self):
        if hasattr(self, "popup") and not self.popup.isVisible():
            self._handle_click()

    def hide_popup(self):
        if hasattr(self, "popup") and self.popup.isVisible():
            self.popup.hide()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.update()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_click()
        else:
            super().mousePressEvent(event)

    def addItem(self, text, data=None):
        if data is None:
            data = text
        self.popup.add_item(text, data)
        self._update_text()

    def addItems(self, items):
        if isinstance(items, dict):
            for data, text in sorted(items.items()):
                self.addItem(f"{data}: {text}", data)
        elif isinstance(items, list):
            for item in items:
                if isinstance(item, tuple) and len(item) == 2:
                    self.addItem(item[0], item[1])
                else:
                    self.addItem(str(item), item)
        self._update_text()

    def clear(self):
        self.popup.clear()
        self._update_text()

    def get_checked_data(self):
        return [data for data, text, chk, item_widget in self.popup.items if chk.isChecked()]

    def get_checked_texts(self):
        return [text for data, text, chk, item_widget in self.popup.items if chk.isChecked()]

    def setCheckedData(self, datas):
        for data, text, chk, item_widget in self.popup.items:
            chk.blockSignals(True)
            chk.setChecked(data in datas)
            chk.blockSignals(False)
        self._update_text()
        self.selectionChanged.emit(self.get_checked_data())

    def clear_checked(self):
        for data, text, chk, item_widget in self.popup.items:
            chk.blockSignals(True)
            chk.setChecked(False)
            chk.blockSignals(False)
        self._update_text()
        self.selectionChanged.emit([])

    def _on_item_state_changed(self):
        self._update_text()
        self.selectionChanged.emit(self.get_checked_data())

    def _sync_text_label_geometry(self):
        """Keep the face text vertically centered and wide enough for its content."""
        metrics = self.text_label.fontMetrics()
        self.text_label.setMinimumWidth(max(1, metrics.horizontalAdvance(self.text_label.text()) + 8))
        self.text_label.setMinimumHeight(max(24, metrics.height() + 4))
        self.text_label.adjustSize()
        self.scroll_area.viewport().updateGeometry()

    def _update_text(self):
        checked_texts = self.get_checked_texts()
        
        try:
            from monkeyqt.themes.engine import ThemeEngine
            is_themed = bool(ThemeEngine.current_theme())
        except ImportError:
            is_themed = False
            
        if is_themed:
            color_active = ThemeEngine.get("--fg", "#0f172a")
            color_placeholder = ThemeEngine.get("--text-muted", "#94a3b8")
        else:
            color_active = "#0f172a"
            color_placeholder = "#94a3b8"
            
        if checked_texts:
            full_text = ", ".join(checked_texts)
            self.text_label.setText(full_text)
            self.text_label.setStyleSheet(f"""
                QLabel#text_label {{
                    color: {color_active};
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    font-size: 13px;
                    background: transparent;
                    border: none;
                }}
            """)
            self.text_label.adjustSize()
        else:
            self.text_label.setText(self._placeholder)
            self.text_label.setStyleSheet(f"""
                QLabel#text_label {{
                    color: {color_placeholder};
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    font-size: 13px;
                    background: transparent;
                    border: none;
                }}
            """)
        self._sync_text_label_geometry()

    def paintEvent(self, event):
        t = ThemeEngine
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = parse_px(t.get("--radius", "6px"), 6, 0, 32)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        # Background
        if not self.isEnabled():
            bg_color = qcolor(t.get("--surface-muted", "#F1F5F9"))
        else:
            bg_color = qcolor(t.get("--surface", "#FFFFFF"))
        painter.fillPath(path, bg_color)

        # Border
        is_focused = (self.property("focused") == "true") or self.hasFocus() or (hasattr(self, "popup") and self.popup.isVisible())
        if not self.isEnabled():
            pen_color = qcolor(t.get("--border", "#E2E8F0"))
        elif is_focused:
            pen_color = qcolor(t.get("--input-focus-border", "#FFFFFF" if t.is_dark() else "#0F172A"))
        elif getattr(self, "_hovered", False):
            pen_color = qcolor(t.get("--input-hover-border", "rgba(255, 255, 255, 0.40)" if t.is_dark() else "#94A3B8"))
        else:
            pen_color = qcolor(t.get("--border", "#E2E8F0"))

        painter.strokePath(path, QPen(pen_color, 1.0))

        # Chevron arrow
        active_color = t.get("--input-focus-border", "#FFFFFF" if t.is_dark() else "#0F172A") if not (t.is_glow() or t.is_brutal()) else t.get("--primary", "#409EFF")
        arrow_color = qcolor(active_color if (getattr(self, "_hovered", False) or is_focused) else t.get("--text-muted", "#64748B"))
        if t.is_brutal() or t.is_pixel():
            arrow_color = QColor("#000000")
            
        painter.setPen(QPen(arrow_color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        cx = int(rect.width() - 18)
        cy = int(rect.height() // 2 + 1)
        painter.drawLine(cx - 5, cy - 3, cx, cy + 3)
        painter.drawLine(cx, cy + 3, cx + 5, cy - 3)
        painter.end()

        super().paintEvent(event)

    set_theme_style = update_theme_style
