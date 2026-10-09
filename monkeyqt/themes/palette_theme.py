"""Opt-in palette-backed light/dark styling for Qt Widgets.

Geometry rules stay installed while colors follow the application palette. Other
MonkeyQt styles retain their existing stylesheet implementation.
"""
from functools import lru_cache
import re

from PySide6.QtGui import QPalette

from .style_utils import qcolor, readable_text

THEMES = frozenset(("Elegant Light", "Dark Mode (OLED)"))
_COLOR = re.compile(r"#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)")
_BLOCK = re.compile(r"([^{}]+)\{([^{}]*)\}")
_DECLARATION = re.compile(r"([\w-]+)\s*:\s*([^;{}]+)")
_MUTED = frozenset(("#64748b", "#606266", "#909399", "#6b7280", "#71717a", "#737373", "#94a3b8", "#a1a1aa", "#a6a6a6", "#9ca3af", "#a1a1a1", "#475569", "#52525b", "#cbd5e1", "#cbd5e0"))


def make_palette(tokens, dark, original):
    palette = QPalette(original)
    role = QPalette.ColorRole
    surface = tokens.get("--surface", "#242424" if dark else "#FFFFFF")
    fg = tokens.get("--fg", "#F5F5F5" if dark else "#0F172A")
    primary = tokens.get("--primary", "#FFFFFF" if dark else "#171717")
    colors = {
        role.Window: tokens.get("--bg", surface),
        role.Base: surface,
        role.AlternateBase: tokens.get("--surface-muted", surface),
        role.WindowText: fg, role.Text: fg, role.ButtonText: fg,
        role.Button: tokens.get("--titlebar-bg", surface),
        role.Mid: tokens.get("--border", "#303030" if dark else "#E2E8F0"),
        role.Midlight: tokens.get("--sidebar-bg", "#202020" if dark else "#F1F5F9"),
        role.PlaceholderText: tokens.get("--text-muted", "#A6A6A6" if dark else "#64748B"),
        role.Highlight: primary, role.HighlightedText: readable_text(primary),
        role.Light: "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.04)",
        role.Dark: "rgba(255,255,255,0.14)" if dark else "rgba(0,0,0,0.08)",
        role.Shadow: "rgba(255,255,255,0.25)" if dark else "rgba(0,0,0,0.20)",
        role.ToolTipBase: surface, role.ToolTipText: fg,
        role.Link: "#60A5FA" if dark else "#2563EB",
    }
    for color_role, value in colors.items():
        palette.setColor(color_role, qcolor(value))
    disabled = qcolor(tokens.get("--text-disabled", "#71717A" if dark else "#94A3B8"))
    for color_role in (role.WindowText, role.Text, role.ButtonText):
        palette.setColor(QPalette.ColorGroup.Disabled, color_role, disabled)
    return palette


def _role(value, prop, selector):
    lower = value.lower().replace(" ", "")
    color = qcolor(value)
    # Preserve semantic status/accent colors; only neutral UI colors are bound.
    r, g, b, _ = color.getRgb()
    neutral = max(r, g, b) - min(r, g, b) <= 38 or lower in _MUTED
    if not neutral:
        return value
    selector = selector.lower()
    sidebar = any(s in selector for s in ("sidebar", "submenu", "mkmenuitem"))
    if "scrollbar" in selector and "background" in prop:
        return "palette(shadow)" if "handle" in selector else value
    if "color" == prop:
        if sidebar:
            return "palette(placeholder-text)" if lower in _MUTED else "palette(window-text)"
        if any(s in selector for s in ('="success"', '="danger"', '="warning"', '="error"')):
            return value
        if any(s in selector for s in ('="primary"', "='primary'", ':checked', ':selected')):
            return "palette(highlighted-text)"
        return "palette(placeholder-text)" if lower in _MUTED else "palette(window-text)"
    if "border" in prop or prop == "outline-color":
        return "palette(highlight)" if any(s in selector for s in (":focus", ':checked', ':selected')) else "palette(mid)"
    if "background" in prop or prop == "selection-background-color":
        if sidebar:
            if ':checked' in selector or 'checked="true"' in selector:
                return "palette(dark)"
            if ':hover' in selector:
                return "palette(light)"
            return "palette(midlight)"
        if any(s in selector for s in ('="primary"', "='primary'", ':checked', ':selected')):
            return "palette(highlight)"
        if ":pressed" in selector:
            return "palette(dark)"
        if ":hover" in selector or color.alpha() < 255:
            return "palette(light)"
        if "titlebar" in selector:
            return "palette(button)"
        if any(s in selector for s in ("windowcontainer", "qmainwindow", "qdialog", "qstackedwidget", "maincentralwidget", "mainrightwidget", "gallerycentralwidget", "mkcontenthost", "mkdesktopshell")):
            return "palette(window)"
        if "tooltip" in selector:
            return "palette(tool-tip-base)"
        return "palette(base)"
    if prop == "selection-color":
        return "palette(highlighted-text)"
    return value


@lru_cache(maxsize=4096)
def palette_stylesheet(qss):
    """Bind neutral colors to palette roles without changing geometry/selectors."""
    def declarations(body, selector):
        def replace(match):
            prop, value = match.groups()
            value = _COLOR.sub(lambda color: _role(color.group(), prop.lower(), selector), value)
            return f"{prop}: {value}"
        return _DECLARATION.sub(replace, body)

    if "{" not in qss:
        return declarations(qss, "")
    return _BLOCK.sub(lambda match: match[1] + "{" + declarations(match[2], match[1]) + "}", qss)
