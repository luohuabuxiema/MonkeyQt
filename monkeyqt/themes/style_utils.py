# -*- coding: utf-8 -*-
"""Small helpers for translating web-style tokens into PySide6 paint/QSS values."""

from __future__ import annotations

import math
import re
from typing import Iterable

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient


HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
RGBA_RE = re.compile(
    r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(?:\s*,\s*([0-9.]+))?\s*\)"
)


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def is_color(value: str) -> bool:
    if not isinstance(value, str):
        return False
    value = value.strip()
    return bool(HEX_RE.match(value) or RGBA_RE.match(value) or QColor(value).isValid())


def qcolor(value: str, fallback: str = "#409EFF", alpha: float | None = None) -> QColor:
    """Return a valid QColor even when generated tokens contain CSS fragments."""
    value = (value or "").strip()
    color = QColor()

    match = RGBA_RE.match(value)
    if match:
        r, g, b = [int(clamp(int(match.group(i)), 0, 255)) for i in range(1, 4)]
        a = float(match.group(4)) if match.group(4) is not None else 1.0
        color = QColor(r, g, b, int(clamp(a, 0, 1) * 255))
    elif HEX_RE.match(value):
        if len(value) == 4:
            value = "#" + "".join(ch * 2 for ch in value[1:])
        color = QColor(value)
    elif QColor(value).isValid():
        color = QColor(value)

    if not color.isValid():
        color = QColor(fallback)
    if alpha is not None:
        color.setAlphaF(clamp(alpha, 0.0, 1.0))
    return color


def qss_color(value: str, fallback: str = "#409EFF") -> str:
    color = qcolor(value, fallback)
    if color.alpha() < 255:
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"
    return color.name(QColor.NameFormat.HexRgb).upper()


def parse_px(value: str, default: int = 6, minimum: int = 0, maximum: int = 48) -> int:
    """Parse values like '6px', '3-4px', '' into a bounded integer pixel value."""
    if not value:
        return default
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", str(value))]
    if not nums:
        return default
    parsed = sum(nums) / len(nums)
    return int(clamp(round(parsed), minimum, maximum))


def mix(color_a: str | QColor, color_b: str | QColor, amount: float) -> QColor:
    amount = clamp(amount, 0.0, 1.0)
    a = color_a if isinstance(color_a, QColor) else qcolor(color_a)
    b = color_b if isinstance(color_b, QColor) else qcolor(color_b)
    return QColor(
        round(a.red() + (b.red() - a.red()) * amount),
        round(a.green() + (b.green() - a.green()) * amount),
        round(a.blue() + (b.blue() - a.blue()) * amount),
        round(a.alpha() + (b.alpha() - a.alpha()) * amount),
    )


def lighten(value: str, amount: float) -> str:
    return mix(value, "#FFFFFF", amount).name(QColor.NameFormat.HexRgb).upper()


def darken(value: str, amount: float) -> str:
    return mix(value, "#000000", amount).name(QColor.NameFormat.HexRgb).upper()


def luminance(value: str | QColor) -> float:
    c = value if isinstance(value, QColor) else qcolor(value)

    def channel(v: int) -> float:
        s = v / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(c.red()) + 0.7152 * channel(c.green()) + 0.0722 * channel(c.blue())


def readable_text(background: str | QColor) -> str:
    return "#FFFFFF" if luminance(background) < 0.45 else "#111827"


def rounded_path(rect: QRectF, radii: Iterable[float] | float) -> QPainterPath:
    if isinstance(radii, (int, float)):
        radii = (float(radii),) * 4
    tl, tr, br, bl = [max(0.0, float(r)) for r in radii]
    left, top, right, bottom = rect.left(), rect.top(), rect.right(), rect.bottom()

    path = QPainterPath()
    path.moveTo(left + tl, top)
    path.lineTo(right - tr, top)
    path.quadTo(right, top, right, top + tr)
    path.lineTo(right, bottom - br)
    path.quadTo(right, bottom, right - br, bottom)
    path.lineTo(left + bl, bottom)
    path.quadTo(left, bottom, left, bottom - bl)
    path.lineTo(left, top + tl)
    path.quadTo(left, top, left + tl, top)
    path.closeSubpath()
    return path


def liquid_radii(radius: int, angle: float, amplitude: float) -> tuple[float, float, float, float]:
    return (
        max(4, radius + amplitude * math.sin(angle)),
        max(4, radius + amplitude * math.cos(angle + 0.8)),
        max(4, radius + amplitude * math.sin(angle + 1.7)),
        max(4, radius + amplitude * math.cos(angle + 2.5)),
    )


def draw_liquid_glass(
    painter: QPainter,
    rect: QRectF,
    radius: int,
    primary: str,
    *,
    dark: bool = False,
    hovered: bool = False,
    pressed: bool = False,
    angle: float = 0.0,
    intensity: float = 1.0,
) -> QPainterPath:
    """Paint a PySide-friendly approximation of liquid glass.

    Qt Widgets cannot do real CSS backdrop-filter, so this builds the material from
    translucent fills, moving gradients, edge highlights, and soft refraction lines.
    """
    rect = QRectF(rect).adjusted(1.5, 1.5, -1.5, -1.5)
    amplitude = max(3.0, min(rect.width(), rect.height()) * 0.045 * intensity)
    path = rounded_path(rect, liquid_radii(radius, angle, amplitude))

    # Soft outside glow/shadow.
    shadow = qcolor(primary, "#409EFF", 0.10 if dark else 0.08)
    for i, alpha in enumerate((0.055, 0.035, 0.018), start=1):
        shadow.setAlphaF(alpha * (1.35 if hovered else 1.0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shadow)
        spread = i * 2.2
        painter.drawPath(rounded_path(rect.adjusted(-spread, -spread, spread, spread), radius + spread))

    # Frosted base and moving chroma wash.
    base = QColor(255, 255, 255, 60 if not dark else 30)
    if pressed:
        base = QColor(255, 255, 255, 45 if not dark else 22)
    painter.setBrush(base)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPath(path)

    gradient = QLinearGradient(
        rect.left() + rect.width() * (0.12 + 0.08 * math.sin(angle)),
        rect.top() + rect.height() * (0.10 + 0.10 * math.cos(angle * 0.8)),
        rect.right() - rect.width() * (0.10 + 0.08 * math.sin(angle + 1.1)),
        rect.bottom() - rect.height() * (0.12 + 0.08 * math.cos(angle + 0.7)),
    )
    p = qcolor(primary, "#409EFF", 0.20 if not hovered else 0.28)
    cyan = QColor(66, 211, 255, 34 if not hovered else 48)
    magenta = QColor(255, 90, 180, 24 if not hovered else 38)
    violet = QColor(150, 120, 255, 22 if not hovered else 34)
    gradient.setColorAt(0.0, p)
    gradient.setColorAt(0.35 + 0.08 * math.sin(angle), cyan)
    gradient.setColorAt(0.68, magenta)
    gradient.setColorAt(1.0, violet)
    painter.setBrush(gradient)
    painter.drawPath(path)

    # Inner lens highlight.
    radial = QRadialGradient(
        rect.left() + rect.width() * (0.28 + 0.08 * math.sin(angle * 0.7)),
        rect.top() + rect.height() * (0.22 + 0.06 * math.cos(angle)),
        max(rect.width(), rect.height()) * 0.75,
    )
    radial.setColorAt(0.0, QColor(255, 255, 255, 78 if not dark else 48))
    radial.setColorAt(0.35, QColor(255, 255, 255, 24 if not dark else 16))
    radial.setColorAt(1.0, QColor(255, 255, 255, 0))
    painter.setBrush(radial)
    painter.drawPath(path)

    # Crisp refractive rim.
    rim = QLinearGradient(rect.topLeft(), rect.bottomRight())
    rim.setColorAt(0.0, QColor(255, 255, 255, 190))
    rim.setColorAt(0.22, QColor(255, 255, 255, 58))
    rim.setColorAt(0.55, qcolor(primary, "#409EFF", 0.22))
    rim.setColorAt(0.78, QColor(255, 255, 255, 32))
    rim.setColorAt(1.0, QColor(255, 255, 255, 120))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(rim, 1.25 if not hovered else 1.7))
    painter.drawPath(path)

    # Top spectral glint.
    glint = QPainterPath()
    glint.moveTo(rect.left() + radius * 0.8, rect.top() + 3)
    glint.cubicTo(
        rect.left() + rect.width() * 0.35,
        rect.top() + 1 + 4 * math.sin(angle),
        rect.left() + rect.width() * 0.63,
        rect.top() + 9 + 3 * math.cos(angle),
        rect.right() - radius * 0.65,
        rect.top() + 4,
    )
    glint_grad = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
    glint_grad.setColorAt(0.0, QColor(255, 255, 255, 0))
    glint_grad.setColorAt(0.18, QColor(255, 255, 255, 165 if hovered else 120))
    glint_grad.setColorAt(0.62, QColor(255, 255, 255, 58))
    glint_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
    painter.setPen(QPen(glint_grad, 1.1))
    painter.drawPath(glint)

    return path
