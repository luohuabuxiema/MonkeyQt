# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QPushButton, QWidget, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont, QLinearGradient
from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import (
    darken,
    draw_liquid_glass,
    lighten,
    luminance,
    parse_px,
    qcolor,
    qss_color,
    readable_text,
)
from monkeyqt.common.enums import MkType, MkSize
from monkeyqt_icons import Ph


def _contrast_ratio(foreground, background):
    """Return the WCAG contrast ratio for two opaque theme colors."""
    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def _button_text_color(preferred, background):
    """Keep the theme foreground when readable, otherwise use the best neutral."""
    preferred_color = qcolor(preferred, "#1E293B")
    background_color = qcolor(background, "#FFFFFF")
    if _contrast_ratio(preferred_color, background_color) >= 4.5:
        return preferred_color.name(QColor.NameFormat.HexRgb).upper()

    candidates = (QColor("#FFFFFF"), QColor("#000000"))
    best = max(candidates, key=lambda color: _contrast_ratio(color, background_color))
    return best.name(QColor.NameFormat.HexRgb).upper()


class MkButton(QPushButton):
    """
    MkButton 组件 - 完美融合 68 种内置主题（玻璃拟态、新拟物化、科幻等）的 3D 自定义绘制，
    并完美兼容已有的 mk_type 和 mk_size API。
    """
    def __init__(self, text="", parent=None, type=None, size=None, btn_type=None, icon=None):
        if isinstance(text, QWidget):
            parent = text
            text = ""
            
        super().__init__(text, parent)
        
        # 自动推断类型，兼容 type 与 btn_type 参数
        resolved_type = MkType.DEFAULT.value
        if type is not None:
            resolved_type = type
        elif btn_type is not None:
            resolved_type = btn_type
            
        resolved_size = MkSize.DEFAULT.value if size is None else size

        self._btn_type = resolved_type
        self._mk_type = resolved_type
        self._mk_size = resolved_size
        self._hovered = False
        self._pressed = False
        self._ph_icon_spec = None

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self._time_angle = 0.0

        self.setProperty("mk_type", resolved_type)
        self.setProperty("mk_size", resolved_size)

        if icon is not None:
            self.setIcon(icon)

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self._update_style()

    def _update_style(self):
        t = ThemeEngine

        if t.is_liquid_glass():
            if not hasattr(self, "_liquid_timer"):
                from PySide6.QtCore import QTimer
                self._liquid_timer = QTimer(self)
                self._liquid_timer.timeout.connect(self._on_liquid_timeout)
            if not self._liquid_timer.isActive():
                self._liquid_timer.start(33)
        else:
            if hasattr(self, "_liquid_timer") and self._liquid_timer.isActive():
                self._liquid_timer.stop()

        primary = t.get("--primary", "#409EFF")
        bg = t.get("--bg", "#FFFFFF")
        fg = t.get("--fg", "#1E293B")
        border = t.get("--border", "#E2E8F0")
        radius = t.get("--radius", "6px")
        border_w = t.get("--border-width", "1px")

        if t.is_neumorphic() or t.is_glass() or t.is_brutal() or t.is_glow() or t.is_pixel():
            text = t.get("--glass-text", fg) if t.is_glass() else fg
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: {text};
                    padding: 8px 20px;
                    font-weight: 700;
                }}
                QPushButton:disabled {{
                    color: #94A3B8;
                }}
            """)
            self.setGraphicsEffect(None)
            self._apply_size_qss()
            self.update()
            return

        hover_primary = t._lighten_hex(primary, 0.15) if primary.startswith("#") else primary
        press_primary = t._darken_hex(primary, 0.1) if primary.startswith("#") else primary

        if self._btn_type == "primary":
            btn_bg = primary
            btn_fg = "#FFFFFF"
            btn_border = primary
            btn_hover_bg = hover_primary
            btn_press_bg = press_primary
        elif self._btn_type == "danger":
            btn_bg = "#EF4444"
            btn_fg = "#FFFFFF"
            btn_border = "#EF4444"
            btn_hover_bg = "#F87171"
            btn_press_bg = "#DC2626"
        elif self._btn_type == "success":
            btn_bg = "#22C55E"
            btn_fg = "#FFFFFF"
            btn_border = "#22C55E"
            btn_hover_bg = "#4ADE80"
            btn_press_bg = "#16A34A"
        elif self._btn_type == "warning":
            btn_bg = "#F59E0B"
            btn_fg = "#FFFFFF"
            btn_border = "#F59E0B"
            btn_hover_bg = "#FBBF24"
            btn_press_bg = "#D97706"
        elif self._btn_type == "secondary":
            btn_bg = "transparent"
            btn_fg = primary
            btn_border = primary
            btn_hover_bg = t._lighten_hex(primary, 0.9) if primary.startswith("#") else "#F0F4FF"
            btn_press_bg = t._lighten_hex(primary, 0.8) if primary.startswith("#") else "#E0E7FF"
        else:
            neutral = self._neutral_palette()
            btn_bg = neutral["background"]
            btn_fg = neutral["foreground"]
            btn_border = neutral["border"]
            btn_hover_bg = neutral["hover_background"]
            btn_press_bg = neutral["pressed_background"]

        if self._btn_type in ("default", "info"):
            neutral = self._neutral_palette()
            btn_hover_fg = neutral["hover_foreground"]
            btn_press_fg = neutral["pressed_foreground"]
            btn_hover_border = neutral["hover_border"]
            btn_press_border = neutral["pressed_border"]
            disabled_bg = neutral["disabled_background"]
            disabled_fg = neutral["disabled_foreground"]
            disabled_border = neutral["disabled_border"]
        else:
            btn_hover_fg = btn_fg
            btn_press_fg = btn_fg
            btn_hover_border = btn_border
            btn_press_border = btn_border
            disabled_bg = "#E2E8F0"
            disabled_fg = "#94A3B8"
            disabled_border = "#E2E8F0"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_bg};
                color: {btn_fg};
                border: {border_w} solid {btn_border};
                border-radius: {radius};
                padding: 8px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {btn_hover_bg};
                color: {btn_hover_fg};
                border-color: {btn_hover_border};
            }}
            QPushButton:pressed {{
                background-color: {btn_press_bg};
                color: {btn_press_fg};
                border-color: {btn_press_border};
            }}
            QPushButton:disabled {{
                opacity: 0.5;
                background-color: {disabled_bg};
                color: {disabled_fg};
                border-color: {disabled_border};
            }}
        """)
        self.setGraphicsEffect(None)
        self._apply_size_qss()

    def _neutral_palette(self):
        """Build theme-aware states for the neutral default and info variants."""
        t = ThemeEngine
        bg = t.get("--bg", "#FFFFFF")
        surface = t.get("--surface", bg)
        surface_muted = t.get("--surface-muted", surface)
        fg = t.get("--fg", "#1E293B")
        text_muted = t.get("--text-muted", fg)
        border = t.get("--border", "#E2E8F0")
        primary = t.get("--primary", border)
        dark_theme = t.is_dark()
        is_info = self._btn_type == "info"

        background = surface_muted if is_info else surface
        if is_info:
            hover_background = (
                lighten(background, 0.10)
                if dark_theme
                else darken(background, 0.055)
            )
            pressed_background = darken(background, 0.10)
        else:
            hover_background = surface_muted
            if qcolor(hover_background).rgba() == qcolor(background).rgba():
                hover_background = (
                    lighten(background, 0.08)
                    if dark_theme
                    else darken(background, 0.045)
                )
            pressed_background = darken(background, 0.08)

        disabled_background = darken(surface_muted, 0.14 if dark_theme else 0.03)
        hover_border = border if is_info else primary

        return {
            "background": qss_color(background, bg),
            "foreground": _button_text_color(fg, background),
            "border": qss_color(border, "#E2E8F0"),
            "hover_background": qss_color(hover_background, surface_muted),
            "hover_foreground": _button_text_color(fg, hover_background),
            "hover_border": qss_color(hover_border, border),
            "pressed_background": qss_color(pressed_background, surface),
            "pressed_foreground": _button_text_color(fg, pressed_background),
            "pressed_border": qss_color(border, "#E2E8F0"),
            "disabled_background": qss_color(disabled_background, surface_muted),
            "disabled_foreground": qss_color(text_muted, fg),
            "disabled_border": qss_color(border, "#E2E8F0"),
        }

    def _apply_size_qss(self):
        size_qss = ""
        if getattr(self, "_mk_size", "default") == "large":
            size_qss = "padding: 12px 19px; font-size: 14px;"
        elif getattr(self, "_mk_size", "default") == "small":
            size_qss = "padding: 5px 11px; font-size: 12px; border-radius: 3px;"
        if size_qss:
            self.setStyleSheet(self.styleSheet() + f"\nQPushButton {{ {size_qss} }}")

    def paintEvent(self, event):
        t = ThemeEngine

        if not (t.is_neumorphic() or t.is_glass() or t.is_glow() or t.is_brutal() or t.is_pixel()):
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        primary = t.get("--primary", "#409EFF")
        bg = t.get("--bg", "#FFFFFF")
        fg = t.get("--fg", "#1E293B")
        r_str = t.get("--radius", "6px")
        radius = parse_px(r_str, 6, 0, 32)

        if self._btn_type == "primary":
            btn_color = qcolor(primary)
        elif self._btn_type == "danger":
            btn_color = qcolor("#EF4444")
        elif self._btn_type == "success":
            btn_color = qcolor("#22C55E")
        elif self._btn_type == "warning":
            btn_color = qcolor("#F59E0B")
        else:
            neutral = self._neutral_palette()
            btn_color = qcolor(neutral["background"], bg)

        text_color = QColor(readable_text(btn_color)) if self._btn_type in ("primary", "danger", "success", "warning") else qcolor(fg)
        if self._btn_type in ("default", "info"):
            neutral = self._neutral_palette()
            if not self.isEnabled():
                btn_color = qcolor(neutral["disabled_background"])
                text_color = qcolor(neutral["disabled_foreground"])
            elif self._pressed:
                btn_color = qcolor(neutral["pressed_background"])
                text_color = qcolor(neutral["pressed_foreground"])
            elif self._hovered:
                btn_color = qcolor(neutral["hover_background"])
                text_color = qcolor(neutral["hover_foreground"])
            else:
                text_color = qcolor(neutral["foreground"])
        else:
            if not self.isEnabled():
                btn_color = qcolor("#CBD5E1")
                text_color = qcolor("#64748B")
            if self._hovered:
                btn_color = btn_color.lighter(115)
            if self._pressed:
                btn_color = btn_color.darker(110)

        if t.is_neumorphic():
            inset = rect.adjusted(4, 4, -4, -4)
            painter.setPen(Qt.PenStyle.NoPen)
            shadow_dark = QColor(0, 0, 0, 25)
            painter.setBrush(QBrush(shadow_dark))
            painter.drawRoundedRect(inset.translated(3, 3), radius, radius)
            shadow_light = QColor(255, 255, 255, 180)
            painter.setBrush(QBrush(shadow_light))
            painter.drawRoundedRect(inset.translated(-2, -2), radius, radius)
            painter.setBrush(QBrush(btn_color))
            painter.drawRoundedRect(inset, radius, radius)

        elif t.is_glass():
            inset = rect.adjusted(2, 2, -2, -2)
            if t.is_liquid_glass():
                angle = getattr(self, "_time_angle", 0.0)
                draw_liquid_glass(
                    painter,
                    inset,
                    max(radius, 14),
                    primary,
                    dark=t.is_dark(),
                    hovered=self._hovered,
                    pressed=self._pressed,
                    angle=angle,
                    intensity=0.75,
                )
                text_color = qcolor(t.get("--glass-text", fg))
            else:
                glass_bg = QColor(btn_color)
                glass_bg.setAlphaF(0.22 if self._btn_type not in ("primary", "danger", "success", "warning") else 0.42)
                painter.setPen(QPen(qcolor(t.get("--glass-border", "rgba(255, 255, 255, 120)")), 1))
                painter.setBrush(QBrush(glass_bg))
                painter.drawRoundedRect(inset, radius, radius)
                text_color = qcolor(t.get("--glass-text", fg))

        elif t.is_brutal():
            radius = 0
            inset = rect.adjusted(2, 2, -6, -6)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#000000")))
            painter.drawRect(inset.translated(4, 4))
            painter.setBrush(QBrush(btn_color))
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(inset)
            if self._btn_type in ("primary", "danger", "success", "warning"):
                text_color = QColor("#FFFFFF")
            elif self._btn_type not in ("default", "info"):
                text_color = QColor("#000000")

        elif t.is_glow():
            inset = rect.adjusted(1, 1, -1, -1)
            if self._btn_type in ("primary", "danger", "success", "warning"):
                btn_fill = QColor(primary)
            elif self._btn_type in ("default", "info"):
                btn_fill = QColor(btn_color)
            else:
                btn_fill = QColor(20, 20, 30)
            painter.setBrush(QBrush(btn_fill))
            painter.setPen(QPen(QColor(primary), 1))
            painter.drawRoundedRect(inset, radius, radius)
            if self._btn_type not in ("default", "info"):
                text_color = QColor(primary) if self._btn_type not in ("primary", "danger", "success", "warning") else QColor("#FFFFFF")

        elif t.is_pixel():
            radius = 0
            pixel = 3
            inset = rect.adjusted(2, 2, -2, -2)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#000000")))
            for x in range(inset.left() + pixel, inset.right() + pixel, pixel):
                painter.drawRect(x, inset.bottom(), pixel, pixel)
            for y in range(inset.top() + pixel, inset.bottom() + pixel, pixel):
                painter.drawRect(inset.right(), y, pixel, pixel)
            painter.setBrush(QBrush(btn_color))
            painter.drawRect(inset)
            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawRect(inset)

        if self._btn_type in ("default", "info") and not self.isEnabled():
            text_color = qcolor(self._neutral_palette()["disabled_foreground"])

        painter.setPen(text_color)
        font = self.font()
        if t.is_brutal():
            font.setWeight(QFont.Weight.Black)
            font.setCapitalization(QFont.Capitalization.AllUppercase)
        elif t.is_pixel():
            font.setFamily("Consolas")
        painter.setFont(font)

        icon = self.icon()
        text = self.text()
        has_icon = not icon.isNull()

        if has_icon:
            icon_sz = self.iconSize()
            icon_w = icon_sz.width()
            icon_h = icon_sz.height()
            spacing = 6 if text else 0
            fm = painter.fontMetrics()
            text_w = fm.horizontalAdvance(text) if text else 0
            total_w = icon_w + spacing + text_w

            start_x = rect.left() + (rect.width() - total_w) // 2
            icon_y = rect.top() + (rect.height() - icon_h) // 2

            pixmap = icon.pixmap(icon_sz)
            painter.drawPixmap(start_x, icon_y, pixmap)

            if text:
                text_rect = QRect(start_x + icon_w + spacing, rect.top(), text_w + 10, rect.height())
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
        else:
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

        painter.end()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def _on_liquid_timeout(self):
        import math
        self._time_angle += 0.04
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()

    def _get_button_text_color(self) -> str:
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--fg", "#1E293B")

        if self._btn_type in ("default", "info"):
            return self._neutral_palette()["foreground"]
        if self._btn_type == "primary":
            return readable_text(qcolor(primary))
        elif self._btn_type in ("danger", "success", "warning"):
            return "#FFFFFF"
        elif self._btn_type in ("text", "outline"):
            return primary

        if t.is_glow():
            return primary
        elif t.is_glass():
            return t.get("--glass-text", fg)
        elif t.is_brutal():
            return "#000000"
        return fg

    def setIcon(self, icon):
        if hasattr(icon, "_ph_spec"):
            self._ph_icon_spec = getattr(icon, "_ph_spec", None)
            try:
                spec = dict(self._ph_icon_spec)
                orig_color = spec.get("color")
                if orig_color in (None, "auto", "default", "fg", "foreground", "currentcolor"):
                    spec["color"] = self._get_button_text_color()
                icon = Ph.icon(**spec)
            except Exception:
                pass
        super().setIcon(icon)

    def set_theme_style(self, style_name: str = None):
        if getattr(self, "_ph_icon_spec", None):
            try:

                spec = dict(self._ph_icon_spec)
                orig_color = spec.get("color")
                if orig_color in (None, "auto", "default", "fg", "foreground", "currentcolor"):
                    spec["color"] = self._get_button_text_color()
                new_icon = Ph.icon(**spec)
                super().setIcon(new_icon)
            except Exception as e:
                pass
        self._update_style()
        self.update()

    @Property(str)
    def btn_type(self):
        return self._btn_type

    @btn_type.setter
    def btn_type(self, value):
        if self._btn_type == value:
            return
        self._btn_type = value
        self._mk_type = value
        self.setProperty("mk_type", value)
        self._update_style()

    @Property(str)
    def mk_type(self):
        return self._mk_type

    @mk_type.setter
    def mk_type(self, value):
        if self._mk_type == value:
            return
        self.btn_type = value

    @Property(str)
    def mk_size(self):
        return self._mk_size

    @mk_size.setter
    def mk_size(self, value):
        if self._mk_size == value:
            return
        self._mk_size = value
        self.setProperty("mk_size", value)
        self._update_style()
        self.style().unpolish(self)
        self.style().polish(self)
