# -*- coding: utf-8 -*-
"""
@File : segmented.py
@Desc : Modern Segmented Control & Capsule Tabs for MonkeyQt.
        Benchmarked against:
        - Apple visionOS / iOS / macOS Segmented Controls
        - Ultralytics HUB Experiment Detail Navigation Tabs
        - Linear / Raycast / Shadcn UI Tabs

Features:
- Pure controller mode (MkSegmented) & integrated page view mode (MkSegmentedTabs)
- Customizable radius (pill semicircular mode or arbitrary border-radius e.g. 6px, 8px, 12px, 0px)
- Multi-size presets: "small" (28-30px), "default"/"medium" (34-36px), "large" (42-44px)
- Smooth animated sliding indicator card (QPropertyAnimation) with soft diffusion shadow
- Badges support (e.g. "Export [1]", notification count, pill badges)
- Full 68-theme dynamic adaptation (Light, Dark, OLED, Glass, Brutalism, Glow, etc.)
- 100% backward compatible with TrainingPlatform's SegmentedTabBar (attach_to_stack, etc.)
"""
from __future__ import annotations

from typing import Optional, List, Dict, Any, Union
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QStackedWidget, QSizePolicy, QGraphicsDropShadowEffect, QFrame
)
from PySide6.QtCore import (
    Qt, Signal, QSize, QRect, QPropertyAnimation, QEasingCurve, QTimer
)
from PySide6.QtGui import QFont, QColor, QIcon, QPainter, QPainterPath

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.components.layout.widget import MkQWidget
from monkeyqt.components.layout.scroll_area import MkStackedWidget


class MkSegmentedBadge(QLabel):
    """
    Superscript number badge attached to the top-right of a segmented tab title.
    Borderless, transparent background, top-aligned (strictly benchmarked against Image 2).
    """

    def __init__(self, text: str = "", size_mode: str = "default", parent: Optional[QWidget] = None):
        super().__init__(str(text), parent)
        self.size_mode = size_mode
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._is_active = False
        self._update_badge_style()

    def set_size_mode(self, size_mode: str):
        self.size_mode = size_mode
        self._update_badge_style()

    def sizeHint(self) -> QSize:
        txt = self.text()
        if not txt:
            return QSize(0, 0)
        fm = self.fontMetrics()
        tw = fm.horizontalAdvance(txt) if hasattr(fm, "horizontalAdvance") else fm.width(txt)
        return QSize(tw + 2, fm.height() + 4)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def set_active(self, active: bool):
        if self._is_active != active:
            self._is_active = active
            self._update_badge_style()

    def _update_badge_style(self):
        t = ThemeEngine
        is_dark = t.is_dark()
        primary = t.get("--primary", "#3B82F6")

        if t.is_brutal():
            fg = "#000000" if not is_dark else "#FFFFFF"
        elif t.is_glow():
            fg = primary
        elif is_dark:
            # Subtle neutral top-right superscript
            fg = "#D4D4D8" if self._is_active else "#71717A"
        else:
            # Elegant Light mode: subtle slate gray superscript (Reference Image 2)
            fg = "#475569" if self._is_active else "#94A3B8"

        font_sz = 9 if self.size_mode == "small" else (11 if self.size_mode == "large" else 10)
        top_margin = 2 if self.size_mode == "small" else (5 if self.size_mode == "large" else 4)

        self.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                background-color: transparent;
                border: none;
                color: {fg};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
                font-size: {font_sz}px;
                font-weight: 700;
                padding: 0px;
                margin-top: {top_margin}px;
            }}
        """)


class MkSegmentedButton(QPushButton):
    """
    Individual tab item button inside MkSegmented.
    Hosts icon, title label, and optional superscript badge.
    """

    def __init__(
        self,
        key: str,
        label: str,
        icon: Any = None,
        badge: Optional[Union[str, int]] = None,
        size_mode: str = "default",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.key = key
        self.label_text = label
        self.icon_source = icon
        self.badge_value = badge
        self.size_mode = size_mode
        self._is_active = False
        self._button_radius = 15

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Internal layout: [Icon] [Label with native superscript]
        self._btn_layout = QHBoxLayout(self)
        self._btn_layout.setContentsMargins(12, 0, 12, 0)
        self._btn_layout.setSpacing(6)
        self._btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon Label / Setup
        self._icon_label = QLabel(self)
        self._icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._icon_label.hide()
        self._btn_layout.addWidget(self._icon_label)

        # Text Label (hosts label and native superscript badge)
        self._text_label = QLabel(label, self)
        self._text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._btn_layout.addWidget(self._text_label)

        self._apply_size_config()
        self._apply_icon()
        self._apply_badge()
        self._update_style()

    def set_button_radius(self, radius: int):
        self._button_radius = max(0, radius)
        self._update_style()

    def sizeHint(self) -> QSize:
        fm = self._text_label.fontMetrics()
        text_w = fm.horizontalAdvance(self.label_text) if hasattr(fm, "horizontalAdvance") else fm.width(self.label_text)
        left, top, right, bottom = self._btn_layout.getContentsMargins()
        w = text_w + left + right

        if self.icon_source and self._icon_label.isVisible():
            px_w = self._icon_label.pixmap().width() if self._icon_label.pixmap() else 16
            w += px_w + self._btn_layout.spacing()

        if self.badge_value is not None and str(self.badge_value).strip() != "":
            badge_w = fm.horizontalAdvance(str(self.badge_value)) if hasattr(fm, "horizontalAdvance") else fm.width(str(self.badge_value))
            w += badge_w + 4

        min_w = 42 if self.size_mode == "small" else (60 if self.size_mode == "large" else 50)
        return QSize(max(w, min_w), self.height())

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def _apply_size_config(self):
        if self.size_mode == "small":
            self.setFixedHeight(24)
            self._btn_layout.setContentsMargins(10, 0, 10, 0)
            self._text_label.setFont(QFont("Microsoft YaHei UI", 9, QFont.Weight.Medium))
            self._button_radius = 12
        elif self.size_mode == "large":
            self.setFixedHeight(36)
            self._btn_layout.setContentsMargins(18, 0, 18, 0)
            self._text_label.setFont(QFont("Microsoft YaHei UI", 10, QFont.Weight.DemiBold))
            self._button_radius = 18
        else:  # default / medium
            self.setFixedHeight(30)
            self._btn_layout.setContentsMargins(14, 0, 14, 0)
            self._text_label.setFont(QFont("Microsoft YaHei UI", 9, QFont.Weight.Medium))
            self._button_radius = 15

    def _apply_icon(self):
        if not self.icon_source:
            self._icon_label.hide()
            return

        icon_sz = 14 if self.size_mode == "small" else (18 if self.size_mode == "large" else 16)
        try:
            # 1. Phosphor icon factory (supports .regular(size=..., color=...))
            if hasattr(self.icon_source, "regular"):
                t = ThemeEngine
                is_dark = t.is_dark()
                ico_col = ("#FFFFFF" if self._is_active else "#94A3B8") if is_dark else ("#0F172A" if self._is_active else "#64748B")
                pixmap = self.icon_source.regular(size=icon_sz, color=ico_col).pixmap(icon_sz, icon_sz)
                self._icon_label.setPixmap(pixmap)
                self._icon_label.show()
            # 2. QIcon instance
            elif isinstance(self.icon_source, QIcon):
                pixmap = self.icon_source.pixmap(icon_sz, icon_sz)
                self._icon_label.setPixmap(pixmap)
                self._icon_label.show()
            else:
                self._icon_label.hide()
        except Exception:
            self._icon_label.hide()

    def _apply_badge(self):
        t = ThemeEngine
        is_dark = t.is_dark()
        primary = t.get("--primary", "#3B82F6")

        if t.is_brutal():
            badge_color = "#000000" if not is_dark else "#FFFFFF"
        elif t.is_glow():
            badge_color = primary
        elif is_dark:
            badge_color = "#A1A1AA" if self._is_active else "#71717A"
        else:
            # Subtle slate gray superscript (Reference Image 2)
            badge_color = "#64748B" if self._is_active else "#94A3B8"

        sup_sz = 9 if self.size_mode == "small" else (11 if self.size_mode == "large" else 10)

        if self.badge_value is not None and str(self.badge_value).strip() != "":
            self._text_label.setText(
                f"{self.label_text}&nbsp;<sup style='font-size:{sup_sz}px; font-weight:700; color:{badge_color};'>{self.badge_value}</sup>"
            )
        else:
            self._text_label.setText(self.label_text)

    def set_badge(self, badge: Optional[Union[str, int]]):
        self.badge_value = badge
        self._apply_badge()
        self.updateGeometry()

    def set_active(self, active: bool):
        if self._is_active != active:
            self._is_active = active
            self._apply_icon()
            self._apply_badge()
            self._update_style()

    def update_theme(self):
        self._apply_icon()
        self._apply_badge()
        self._update_style()

    def _update_style(self):
        t = ThemeEngine
        is_dark = t.is_dark()
        fg = t.get("--fg", "#0F172A")
        text_muted = t.get("--text-muted", "#64748B")
        primary = t.get("--primary", "#3B82F6")

        if t.is_brutal():
            active_color = "#000000"
            inactive_color = "#333333"
            hover_color = "#000000"
            weight = "700" if self._is_active else "600"
        elif t.is_glow() or t.is_pixel():
            active_color = primary
            inactive_color = text_muted
            hover_color = primary
            weight = "700" if self._is_active else "500"
        elif is_dark:
            active_color = "#FFFFFF"
            inactive_color = text_muted
            hover_color = "#F8FAFC"
            weight = "600" if self._is_active else "500"
        else:
            active_color = fg
            inactive_color = text_muted
            hover_color = "#0F172A"
            weight = "600" if self._is_active else "500"

        cur_color = active_color if self._is_active else inactive_color
        self._text_label.setStyleSheet(f"""
            QLabel {{
                color: {cur_color};
                font-weight: {weight};
                background: transparent;
                border: none;
            }}
        """)

        hover_bg = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.04)"
        if self._is_active:
            hover_bg = "transparent"

        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                outline: none;
                margin: 0px;
                padding: 0px;
                border-radius: {self._button_radius}px;
            }}
            QPushButton:hover {{
                background: {hover_bg};
            }}
        """)


class MkSegmentedIndicator(QFrame):
    """
    Elevated sliding indicator card with soft diffusion drop shadow.
    Dynamically tracks the geometry of the active MkSegmentedButton.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._radius = 16
        self._indicator_style = "auto"
        self._shadow_effect: Optional[QGraphicsDropShadowEffect] = None
        self._init_shadow()
        self.update_theme()

    def _init_shadow(self):
        self._shadow_effect = QGraphicsDropShadowEffect(self)
        self._shadow_effect.setBlurRadius(10)
        self._shadow_effect.setOffset(0, 2)
        self._shadow_effect.setColor(QColor(0, 0, 0, 24))
        self.setGraphicsEffect(self._shadow_effect)

    def set_radius(self, radius: int):
        self._radius = max(0, radius)
        self.update_theme()

    def set_indicator_style(self, style: str):
        self._indicator_style = style
        self.update_theme()

    def update_theme(self):
        t = ThemeEngine
        is_dark = t.is_dark()
        primary = t.get("--primary", "#3B82F6")
        surface = t.get("--surface", "#FFFFFF")
        border = t.get("--border", "#E2E8F0")

        if self._indicator_style == "primary":
            bg = primary
            bd = "none"
            if self._shadow_effect:
                self._shadow_effect.setColor(QColor(0, 0, 0, 40))
        elif t.is_brutal():
            bg = "#FFDE59" if not is_dark else primary
            bd = "2px solid #000000"
            if self._shadow_effect:
                self._shadow_effect.setEnabled(False)
        elif t.is_glass():
            bg = t.get("--glass-surface", "rgba(255, 255, 255, 0.40)")
            bd = f"1px solid {t.get('--glass-border', 'rgba(255, 255, 255, 0.55)')}"
            if self._shadow_effect:
                self._shadow_effect.setEnabled(True)
                self._shadow_effect.setBlurRadius(12)
                self._shadow_effect.setColor(QColor(0, 0, 0, 20))
        elif is_dark:
            # High-end Dark / OLED mode: elevated card surface with crisp subtle border
            if t.is_glow():
                bg = "rgba(255, 255, 255, 0.12)"
                bd = f"1px solid {primary}"
            else:
                bg = "#27272A" if surface in ("#121212", "#000000", "#0F172A") else surface
                bd = "1px solid rgba(255, 255, 255, 0.12)"
            if self._shadow_effect:
                self._shadow_effect.setEnabled(True)
                self._shadow_effect.setBlurRadius(8)
                self._shadow_effect.setOffset(0, 2)
                self._shadow_effect.setColor(QColor(0, 0, 0, 70))
        else:
            # Elegant Light mode: pure white floating card with soft border & diffusion shadow
            bg = "#FFFFFF"
            bd = "1px solid rgba(0, 0, 0, 0.08)"
            if self._shadow_effect:
                self._shadow_effect.setEnabled(True)
                self._shadow_effect.setBlurRadius(10)
                self._shadow_effect.setOffset(0, 2)
                self._shadow_effect.setColor(QColor(0, 0, 0, 22))

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: {bd};
                border-radius: {self._radius}px;
            }}
        """)


class MkSegmented(QWidget):
    """
    Modern Segmented Control & Navigation Pill Bar (胶囊分段任务栏).
    Benchmarked against Apple visionOS, Ultralytics HUB, Linear, and Shadcn UI.

    Signals:
        currentChanged(int index, str key): Emitted when active tab changes.
        valueChanged(str key): Emitted with active tab's key.
        indexChanged(int index): Emitted with active tab's index.
    """

    currentChanged = Signal(int, str)
    valueChanged = Signal(str)
    indexChanged = Signal(int)

    def __init__(
        self,
        items: Optional[List[Union[str, Dict[str, Any]]]] = None,
        radius: Optional[int] = None,
        pill: bool = True,
        size: str = "default",
        fill: bool = False,
        animated: bool = True,
        indicator_style: str = "auto",
        parent: Optional[QWidget] = None,
    ):
        """
        Args:
            items: Initial list of items (e.g. ["7 天", "30 天"] or [{"key": "train", "label": "Train"}]).
            radius: Custom border radius in pixels. If None and pill=True, auto-computed as height // 2.
            pill: If True, uses semicircular pill ends. If False, uses modern sleek rectangular card corners.
            size: Preset height: "small" (30px), "default" / "medium" (36px), "large" (44px).
            fill: If True, tab buttons expand equally to fill the entire container width.
            animated: If True, smooth sliding indicator animation when switching tabs.
            indicator_style: "auto", "card", or "primary".
            parent: Parent QWidget.
        """
        super().__init__(parent)
        self.custom_radius = radius
        self.is_pill = pill
        self.size_mode = size.lower()
        self.is_fill = fill
        self.is_animated = animated
        self.indicator_style = indicator_style

        self._current_index: int = -1
        self._buttons: List[MkSegmentedButton] = []
        self._keys: List[str] = []

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding if fill else QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed
        )

        # Sliding Indicator (rendered under buttons)
        self._indicator = MkSegmentedIndicator(self)
        self._indicator.set_indicator_style(self.indicator_style)
        self._indicator.hide()

        # Layout for buttons
        self._layout = QHBoxLayout(self)
        self._padding = 4 if self.size_mode == "large" else 3
        self._layout.setContentsMargins(self._padding, self._padding, self._padding, self._padding)
        self._layout.setSpacing(2)

        # Geometry animation
        self._anim = QPropertyAnimation(self._indicator, b"geometry", self)
        self._anim.setDuration(190)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Height & sizing
        self._update_container_height()
        self._apply_container_style()

        # Connect theme engine
        ThemeEngine.instance().themeChanged.connect(self._on_theme_changed)

        # Populate initial items if provided
        if items:
            for item in items:
                if isinstance(item, dict):
                    self.add_item(
                        key=item.get("key", item.get("label", "")),
                        label=item.get("label", item.get("key", "")),
                        icon=item.get("icon", None),
                        badge=item.get("badge", None),
                    )
                else:
                    self.add_item(key=str(item), label=str(item))

    # ──────────────────────── Items Management ────────────────────────

    def add_item(
        self,
        key: str,
        label: str,
        icon: Any = None,
        badge: Optional[Union[str, int]] = None,
        enabled: bool = True,
    ) -> MkSegmentedButton:
        """Add a tab item to the segmented control."""
        btn = MkSegmentedButton(
            key=key,
            label=label,
            icon=icon,
            badge=badge,
            size_mode=self.size_mode,
            parent=self,
        )
        btn.setEnabled(enabled)

        _, i_rad = self._calc_radii()
        btn.set_button_radius(i_rad)

        idx = len(self._buttons)
        btn.clicked.connect(lambda *args, i=idx: self.set_current_index(i))

        if self.is_fill:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._buttons.append(btn)
        self._keys.append(key)
        self._layout.addWidget(btn)

        # If first item, set as active
        if len(self._buttons) == 1:
            self.set_current_index(0)

        self.updateGeometry()
        return btn

    def sizeHint(self) -> QSize:
        left, top, right, bottom = self._layout.getContentsMargins()
        total_w = left + right
        for btn in self._buttons:
            total_w += btn.sizeHint().width()
        if len(self._buttons) > 1:
            total_w += (len(self._buttons) - 1) * self._layout.spacing()
        h = self.height() if self.height() > 0 else (30 if self.size_mode == "small" else (44 if self.size_mode == "large" else 36))
        return QSize(total_w, h)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def add_tab(self, key: str, label: str, icon=None, badge=None) -> MkSegmentedButton:
        """Alias for add_item for 100% backward compatibility with SegmentedTabBar."""
        return self.add_item(key=key, label=label, icon=icon, badge=badge)

    def set_badge(self, key_or_index: Union[str, int], badge: Optional[Union[str, int]]):
        """Update badge value for a specific tab item (e.g. set_badge('export', 1))."""
        idx = self._resolve_index(key_or_index)
        if 0 <= idx < len(self._buttons):
            self._buttons[idx].set_badge(badge)
            QTimer.singleShot(10, self._sync_indicator_to_current)

    def set_item_enabled(self, key_or_index: Union[str, int], enabled: bool):
        """Enable or disable a specific tab item."""
        idx = self._resolve_index(key_or_index)
        if 0 <= idx < len(self._buttons):
            self._buttons[idx].setEnabled(enabled)

    def count(self) -> int:
        """Return total number of tabs."""
        return len(self._buttons)

    def clear(self):
        """Remove all tab items."""
        for btn in self._buttons:
            self._layout.removeWidget(btn)
            btn.deleteLater()
        self._buttons.clear()
        self._keys.clear()
        self._current_index = -1
        self._indicator.hide()

    # ──────────────────────── Selection & Indexing ────────────────────────

    def set_current_index(self, index: int):
        """Set active item by numeric index."""
        if index < 0 or index >= len(self._buttons):
            return
        if self._current_index == index and self._indicator.isVisible():
            return

        old_index = self._current_index
        self._current_index = index

        for i, btn in enumerate(self._buttons):
            btn.set_active(i == index)

        self._animate_indicator(old_index, index)

        key = self._keys[index] if index < len(self._keys) else ""
        self.currentChanged.emit(index, key)
        self.valueChanged.emit(key)
        self.indexChanged.emit(index)

    def set_current_key(self, key: str):
        """Set active item by unique key string."""
        if key in self._keys:
            self.set_current_index(self._keys.index(key))

    def current_index(self) -> int:
        return self._current_index

    def current_key(self) -> str:
        if 0 <= self._current_index < len(self._keys):
            return self._keys[self._current_index]
        return ""

    def attach_to_stack(self, stack: QStackedWidget):
        """
        Seamlessly bind this segmented bar to a QStackedWidget / MkStackedWidget.
        100% backward compatible with TrainingPlatform code.
        """
        if not stack:
            return
        self.currentChanged.connect(lambda idx, *args: stack.setCurrentIndex(idx))
        if len(self._buttons) > 0 and self._current_index >= 0:
            stack.setCurrentIndex(self._current_index)

    # ──────────────────────── Indicator & Layout ────────────────────────

    def _resolve_index(self, key_or_index: Union[str, int]) -> int:
        if isinstance(key_or_index, int):
            return key_or_index
        if isinstance(key_or_index, str) and key_or_index in self._keys:
            return self._keys.index(key_or_index)
        return -1

    def _animate_indicator(self, old_index: int, new_index: int):
        if new_index < 0 or new_index >= len(self._buttons):
            self._indicator.hide()
            return

        target_btn = self._buttons[new_index]
        target_geo = target_btn.geometry()

        if not target_geo.isValid() or target_geo.width() == 0:
            # If button geometry is not yet finalized, sync after layout finishes
            QTimer.singleShot(0, self._sync_indicator_to_current)
            return

        self._indicator.show()
        self._indicator.lower()

        if self.is_animated and old_index >= 0 and self._indicator.isVisible() and self.isVisible():
            self._anim.stop()
            self._anim.setStartValue(self._indicator.geometry())
            self._anim.setEndValue(target_geo)
            self._anim.start()
        else:
            self._anim.stop()
            self._indicator.setGeometry(target_geo)

    def _sync_indicator_to_current(self):
        if 0 <= self._current_index < len(self._buttons):
            btn = self._buttons[self._current_index]
            geo = btn.geometry()
            if geo.isValid() and geo.width() > 0:
                self._indicator.setGeometry(geo)
                self._indicator.show()
                self._indicator.lower()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_indicator_to_current()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._sync_indicator_to_current)

    # ──────────────────────── Theme & Geometry Calculation ────────────────────────

    def _update_container_height(self):
        if self.size_mode == "small":
            h = 30
        elif self.size_mode == "large":
            h = 44
        else:
            h = 36
        self.setFixedHeight(h)

    def _calc_radii(self) -> tuple[int, int]:
        """Returns (container_radius, indicator_radius)."""
        h = self.height() if self.height() > 0 else 36
        if self.custom_radius is not None:
            c_rad = max(0, self.custom_radius)
            i_rad = max(0, c_rad - self._padding)
            return c_rad, i_rad

        if self.is_pill:
            c_rad = h // 2
            btn_h = h - self._padding * 2
            i_rad = btn_h // 2
            return c_rad, i_rad
        else:
            return 8, 5

    def _on_theme_changed(self, theme_name: str = ""):
        self._apply_container_style()
        self._indicator.update_theme()
        for btn in self._buttons:
            btn.update_theme()
        self._sync_indicator_to_current()

    def _apply_container_style(self):
        c_rad, i_rad = self._calc_radii()
        self._indicator.set_radius(i_rad)
        for btn in self._buttons:
            btn.set_button_radius(i_rad)

        t = ThemeEngine
        is_dark = t.is_dark()
        border = t.get("--border", "#E2E8F0")

        if t.is_brutal():
            bg = "#FFFFFF" if not is_dark else "#18181B"
            bd = "2px solid #000000"
            c_rad = 0 if self.custom_radius is None else c_rad
            self._indicator.set_radius(0 if self.custom_radius is None else i_rad)
        elif t.is_glass():
            bg = "rgba(255, 255, 255, 0.12)" if not is_dark else "rgba(255, 255, 255, 0.05)"
            bd = f"1px solid {t.get('--glass-border', 'rgba(255, 255, 255, 0.35)')}"
        elif is_dark:
            # Dark / OLED mode track
            bg = "rgba(255, 255, 255, 0.05)"
            bd = "1px solid rgba(255, 255, 255, 0.08)"
        else:
            # Elegant Light mode track
            bg = "#F1F5F9"
            bd = "1px solid rgba(0, 0, 0, 0.05)"

        self.setStyleSheet(f"""
            MkSegmented {{
                background-color: {bg};
                border: {bd};
                border-radius: {c_rad}px;
            }}
        """)


class MkSegmentedTabs(MkQWidget):
    """
    Integrated Segmented Tabs & Responsive Content View (一体化分段标签页视图容器).
    Combines MkSegmented bar on top with MkStackedWidget underneath.

    Features:
    - Add page views directly via add_tab(key, title, widget, icon=None, badge=None)
    - Automatic page switching and layout responsiveness
    - Customizable alignment: "left", "center", "right", "stretch"
    - Full 68-theme adaptation
    """

    currentChanged = Signal(int, str)
    tabChanged = Signal(str)

    def __init__(
        self,
        radius: Optional[int] = None,
        pill: bool = True,
        size: str = "default",
        tab_align: str = "left",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent, layout="v", margins=0, spacing=14)
        self.tab_align = tab_align.lower()

        # 1. Header Layout for Segmented Control
        self._header_widget = MkQWidget(role="transparent", layout="h", margins=0, spacing=0)
        self._header_layout = self._header_widget.inner_layout

        is_fill = (self.tab_align == "stretch")
        self._segmented = MkSegmented(
            radius=radius,
            pill=pill,
            size=size,
            fill=is_fill,
            parent=self,
        )

        if self.tab_align == "center":
            self._header_layout.addStretch()
            self._header_layout.addWidget(self._segmented)
            self._header_layout.addStretch()
        elif self.tab_align == "right":
            self._header_layout.addStretch()
            self._header_layout.addWidget(self._segmented)
        elif self.tab_align == "stretch":
            self._header_layout.addWidget(self._segmented, stretch=1)
        else:  # left (default)
            self._header_layout.addWidget(self._segmented)
            self._header_layout.addStretch()

        self.inner_layout.addWidget(self._header_widget)

        # 2. Content Stack Area (MkStackedWidget with adaptive geometry)
        self._stack = MkStackedWidget(self)
        self._stack.setStyleSheet("QStackedWidget { background: transparent; border: none; }")
        self.inner_layout.addWidget(self._stack, stretch=1)

        self._tabs_map: Dict[str, QWidget] = {}

        # Connect signals
        self._segmented.currentChanged.connect(self._on_segmented_changed)

    def add_tab(
        self,
        key: str,
        label: str,
        widget: QWidget,
        icon: Any = None,
        badge: Optional[Union[str, int]] = None,
    ) -> MkSegmentedButton:
        """Add a tab and its corresponding page widget."""
        btn = self._segmented.add_item(key=key, label=label, icon=icon, badge=badge)
        self._stack.addWidget(widget)
        self._tabs_map[key] = widget

        if len(self._tabs_map) == 1:
            self._stack.setCurrentWidget(widget)

        return btn

    def set_badge(self, key_or_index: Union[str, int], badge: Optional[Union[str, int]]):
        """Update badge count for a tab."""
        self._segmented.set_badge(key_or_index, badge)

    def set_active(self, key_or_index: Union[str, int]):
        """Programmatically switch active tab."""
        if isinstance(key_or_index, int):
            self._segmented.set_current_index(key_or_index)
        else:
            self._segmented.set_current_key(str(key_or_index))

    def current_key(self) -> str:
        return self._segmented.current_key()

    def current_index(self) -> int:
        return self._segmented.current_index()

    def current_widget(self) -> Optional[QWidget]:
        return self._stack.currentWidget()

    def tab_bar(self) -> MkSegmented:
        """Access underlying MkSegmented control bar directly."""
        return self._segmented

    def stacked_widget(self) -> MkStackedWidget:
        """Access underlying MkStackedWidget directly."""
        return self._stack

    def _on_segmented_changed(self, index: int, key: str):
        if 0 <= index < self._stack.count():
            self._stack.setCurrentIndex(index)
        self.currentChanged.emit(index, key)
        self.tabChanged.emit(key)


# Aliases for 100% compatibility and versatility
MkSegmentedControl = MkSegmented
MkCapsuleTabs = MkSegmentedTabs
SegmentedTabBar = MkSegmented
