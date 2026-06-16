# -*- coding: utf-8 -*-
"""ThemedAvatarMenu — clickable avatar with themed dropdown, 68-style support."""

from __future__ import annotations

import math
import os
from collections.abc import Callable, Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPalette,
)
from PySide6.QtWidgets import QMenu

from monkeyqt.components.navigation.avatar_menu import MkAvatarMenu
from monkeyqt.core.icons import MkPhosphorIcon
from ..engine import ThemeEngine
from ..style_utils import draw_liquid_glass, parse_px, qcolor, readable_text


class ThemedAvatarMenu(MkAvatarMenu):
    """MkAvatarMenu with automatic 68-theme visual adaptation.

    The avatar rendering follows the same style logic as ``ThemedAvatar``
    (gradient fills, glass/brutal/pixel/glow treatments) while retaining
    the full click-to-open-menu API of ``MkAvatarMenu``.

    Usage::

        avatar = ThemedAvatarMenu(
            text="Me",
            image_path="avatar.png",
            user_name="落花不写码",
            subtitle="PySide6 开发者",
            size=32,
        )
        avatar.add_action("profile", "个人主页", icon="user")
        avatar.add_action("settings", "设置", icon="gear")
    """

    def __init__(
        self,
        text: str = "",
        image_path: str = "",
        shape: str = "circle",
        size: int = 32,
        user_name: str = "",
        subtitle: str = "",
        actions: Iterable[dict] | None = None,
        parent=None,
    ):
        super().__init__(text, image_path, shape, size, user_name, subtitle, actions, parent)
        self._time_angle = 0.0
        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    # ── Theme-aware painting ──────────────────────────────────────────

    def set_theme_style(self, style_name: str = None) -> None:
        t = ThemeEngine
        if t.is_liquid_glass():
            if not hasattr(self, "_liquid_timer"):
                from PySide6.QtCore import QTimer
                self._liquid_timer = QTimer(self)
                self._liquid_timer.timeout.connect(self._on_liquid_timeout)
            if not self._liquid_timer.isActive():
                self._liquid_timer.start(33)
        elif hasattr(self, "_liquid_timer") and self._liquid_timer.isActive():
            self._liquid_timer.stop()

        font = self.font()
        font.setPixelSize(max(10, int(self._avatar_size * 0.38)))
        font.setWeight(QFont.Weight.Black)
        if t.is_pixel():
            font.setFamily("Consolas")
        self.setFont(font)
        self.update()

    def paintEvent(self, event) -> None:
        t = ThemeEngine

        # If no theme is active, fall back to the base MkAvatar paint
        if t.current_theme() == t.DEFAULT_THEME_NAME:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = rect.width() / 2 if self._shape == "circle" else parse_px(t.get("--radius", "6px"), 6, 0, 18)

        path = QPainterPath()
        if self._shape == "circle":
            path.addEllipse(rect)
        elif t.is_brutal() or t.is_pixel():
            path.addRect(rect)
        else:
            path.addRoundedRect(rect, radius, radius)

        primary = t.get("--primary", "#409EFF")
        accent = t.get("--accent", "#7DD3FC")

        # Liquid glass underlay
        if t.is_liquid_glass():
            draw_liquid_glass(
                painter, rect, int(radius), primary,
                dark=t.is_dark(), hovered=True, angle=self._time_angle, intensity=0.65,
            )

        painter.save()
        painter.setClipPath(path)
        if self._image_path and os.path.exists(self._image_path):
            pixmap = QPixmap(self._image_path)
            scaled = pixmap.scaled(
                self.rect().size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
            if t.is_brutal() or t.is_pixel():
                grad.setColorAt(0.0, qcolor(primary))
                grad.setColorAt(1.0, qcolor(primary))
            elif t.is_glass():
                c1 = qcolor(primary, "#409EFF", 0.58)
                c2 = qcolor(accent, "#7DD3FC", 0.42)
                grad.setColorAt(0.0, c1)
                grad.setColorAt(1.0, c2)
            else:
                grad.setColorAt(0.0, qcolor(primary))
                grad.setColorAt(1.0, qcolor(accent))
            painter.fillPath(path, QBrush(grad))

            if self._text:
                text_str = self._text[:2].upper()
                text_color = QColor("#000000") if (t.is_brutal() or t.is_pixel()) else QColor(readable_text(primary))
                painter.setPen(text_color)
                painter.setFont(self.font())
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text_str)
        painter.restore()

        # Rim / border
        if t.is_brutal() or t.is_pixel():
            painter.setPen(QPen(QColor("#000000"), 2))
        elif t.is_glass():
            painter.setPen(QPen(qcolor(t.get("--glass-border", "rgba(255, 255, 255, 120)")), 1.2))
        else:
            painter.setPen(QPen(qcolor(t.get("--border", "#E2E8F0")), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self._shape == "circle":
            painter.drawEllipse(rect)
        elif t.is_brutal() or t.is_pixel():
            painter.drawRect(rect)
        else:
            painter.drawRoundedRect(rect, radius, radius)
        painter.end()

    # ── Theme-aware dropdown menu ─────────────────────────────────────

    def show_menu(self) -> None:
        """Override to apply ThemeEngine-aware QSS to the popup menu."""
        menu = QMenu(self)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        t = ThemeEngine

        if t.current_theme() == t.DEFAULT_THEME_NAME:
            palette = self.palette()
            base = palette.color(QPalette.ColorRole.Base).name()
            text = palette.color(QPalette.ColorRole.Text).name()
            border = palette.color(QPalette.ColorRole.Mid).name()
            hover = palette.color(QPalette.ColorRole.Highlight).name()
            hover_text = palette.color(QPalette.ColorRole.HighlightedText).name()
            muted = palette.color(QPalette.ColorRole.PlaceholderText).name()
            menu.setStyleSheet(
                f"""
                QMenu {{
                    background-color: {base};
                    color: {text};
                    border: 1px solid {border};
                    border-radius: 6px;
                    padding: 6px;
                }}
                QMenu::item {{
                    min-width: 150px;
                    padding: 7px 24px 7px 10px;
                    border-radius: 5px;
                }}
                QMenu::item:selected {{
                    background-color: {hover};
                    color: {hover_text};
                }}
                QMenu::item:disabled {{ color: {muted}; }}
                QMenu::separator {{
                    height: 1px;
                    background: {border};
                    margin: 5px 7px;
                }}
                """
            )
        else:
            surface = t.get("--surface", "#FFFFFF")
            fg = t.get("--fg", "#1E293B")
            border = t.get("--border", "#E2E8F0")
            primary = t.get("--primary", "#409EFF")
            muted = t.get("--text-muted", "#64748B")
            surface_muted = t.get("--surface-muted", "#F1F5F9")
            radius = "0px" if (t.is_brutal() or t.is_pixel()) else t.get("--radius", "6px")
            border_rule = "2px solid #000000" if (t.is_brutal() or t.is_pixel()) else f"1px solid {border}"

            if t.is_glass():
                surface = t.get("--glass-surface", surface)
                fg = t.get("--glass-text", fg)
                border = t.get("--glass-border", border)
                border_rule = f"1px solid {border}"

            primary_text = readable_text(primary)

            menu.setStyleSheet(f"""
                QMenu {{
                    background-color: {surface};
                    color: {fg};
                    border: {border_rule};
                    border-radius: {radius};
                    padding: 6px;
                }}
                QMenu::item {{
                    min-width: 150px;
                    padding: 7px 24px 7px 10px;
                    border-radius: {parse_px(radius, 6, 0, 12) - 2 if parse_px(radius, 6, 0, 12) > 2 else 0}px;
                }}
                QMenu::item:selected {{
                    background-color: {primary};
                    color: {primary_text};
                }}
                QMenu::item:disabled {{
                    color: {muted};
                }}
                QMenu::separator {{
                    height: 1px;
                    background: {border};
                    margin: 5px 7px;
                }}
            """)

        if self.user_name:
            header = menu.addAction(self.user_name)
            header.setEnabled(False)
        if self.subtitle:
            subtitle_act = menu.addAction(self.subtitle)
            subtitle_act.setEnabled(False)
        if self.user_name or self.subtitle:
            menu.addSeparator()

        fg_color = self.palette().color(QPalette.ColorRole.Text).name() if t.current_theme() == t.DEFAULT_THEME_NAME else fg
        for config in self._actions:
            if config.get("separator_before"):
                menu.addSeparator()
            action = menu.addAction(str(config.get("text", "")))
            action.setEnabled(bool(config.get("enabled", True)))
            icon_name = str(config.get("icon", ""))
            if icon_name:
                action.setIcon(MkPhosphorIcon.get_icon(icon_name, fg_color, size=16))

            action_id = str(config.get("id", ""))
            callback = config.get("callback")
            action.triggered.connect(
                lambda _checked=False, aid=action_id, cb=callback: self._trigger_action(aid, cb)
            )

        menu_width = menu.sizeHint().width()
        position = self.mapToGlobal(self.rect().bottomRight())
        # Align right edge of menu to right edge of avatar and give 4px gap
        position.setX(position.x() - menu_width)
        position.setY(position.y() + 4)
        menu.popup(position)

    # ── Liquid glass animation ────────────────────────────────────────

    def _on_liquid_timeout(self) -> None:
        self._time_angle += 0.03
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()
