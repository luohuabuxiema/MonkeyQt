"""
Core Engine and API for monkeyqt-icons.
Provides 1-to-1 Phosphor Icons rendering for PySide6 / PyQt.
"""

import os
import pathlib
import xml.etree.ElementTree as ET
from functools import lru_cache
from typing import Union, Tuple, Optional, List, Dict, Any

from .qt_compat import QtCore, QtGui, QtWidgets, QtSvg
from .metadata import CATALOG, PASCAL_TO_NAME, NAME_TO_PASCAL

ASSETS_DIR = pathlib.Path(__file__).parent / "assets"

VALID_WEIGHTS = {"regular", "bold", "fill", "light", "thin", "duotone"}


try:
    from monkeyqt.themes import ThemeEngine
    HAS_THEME_ENGINE = True
except ImportError:
    ThemeEngine = None
    HAS_THEME_ENGINE = False


def _get_theme_color(token_or_role: str) -> str:
    """Helper to resolve ThemeEngine colors if available."""
    if not HAS_THEME_ENGINE or not ThemeEngine:
        return ""
    role = token_or_role.lower().strip()
    if role in ("none", "auto", "default", "fg", "foreground", "currentcolor"):
        return ThemeEngine.get("--fg", "#1E293B")
    elif role in ("primary", "main"):
        return ThemeEngine.get("--primary", "#409EFF")
    elif role in ("secondary", "muted", "text-muted"):
        return ThemeEngine.get("--text-muted", "#64748B")
    elif role in ("accent",):
        return ThemeEngine.get("--accent", "#7DD3FC")
    elif role in ("border",):
        return ThemeEngine.get("--border", "#E2E8F0")
    elif role.startswith("--"):
        return ThemeEngine.get(role, "")
    return ""


def _parse_color(color: Union[str, QtGui.QColor, None]) -> str:
    """Helper to convert color input to hex or css color string, with ThemeEngine token support."""
    if color is None or color == "currentColor" or color == "auto":
        theme_col = _get_theme_color("auto")
        return theme_col if theme_col else "#1E293B"

    if isinstance(color, QtGui.QColor):
        if color.alpha() < 255:
            return f"rgba({color.red()},{color.green()},{color.blue()},{color.alpha()/255:.2f})"
        return color.name()

    color_str = str(color).strip()
    theme_col = _get_theme_color(color_str)
    if theme_col:
        return theme_col

    return color_str


class PhosphorEngine:
    """Engine for parsing, tinting, and rendering Phosphor SVG icons to QIcon / QPixmap."""

    @staticmethod
    def get_svg_path(name: str, weight: str = "regular") -> pathlib.Path:
        weight = weight.lower()
        if weight not in VALID_WEIGHTS:
            weight = "regular"

        # Kebab-case conversion if needed
        kebab_name = PASCAL_TO_NAME.get(name, name).lower()

        filename = f"{kebab_name}-{weight}.svg" if weight != "regular" else f"{kebab_name}.svg"
        path = ASSETS_DIR / weight / filename
        if not path.exists():
            # Fallback check
            path = ASSETS_DIR / weight / f"{kebab_name}.svg"
            if not path.exists():
                path = ASSETS_DIR / "regular" / f"{kebab_name}.svg"
        return path

    @staticmethod
    def process_svg(
        svg_text: str,
        color: str = "currentColor",
        secondary_color: Optional[str] = None,
        secondary_opacity: float = 0.2,
        mirrored: bool = False,
        rotation: int = 0
    ) -> str:
        """Processes SVG text: applies colors, duotone opacity, mirroring, and rotation."""
        main_color = _parse_color(color)
        sec_color = _parse_color(secondary_color) if secondary_color else main_color

        # Duotone handling: Phosphor SVGs have the background path with opacity="0.2"
        if "opacity=" in svg_text and "duotone" in svg_text or ("opacity=" in svg_text and secondary_color):
            # Parse duotone elements
            # Replace opacity with custom secondary_opacity if provided
            svg_text = re_sub_opacity(svg_text, secondary_opacity)
            
        # Color replacement
        if secondary_color and "opacity=" in svg_text:
            # Separate foreground and background fills
            parts = svg_text.split('<path ')
            if len(parts) > 2:
                # First path is usually background (with opacity)
                new_parts = [parts[0]]
                for idx, part in enumerate(parts[1:], 1):
                    if 'opacity=' in part:
                        part = part.replace('fill="currentColor"', f'fill="{sec_color}"')
                    else:
                        part = part.replace('fill="currentColor"', f'fill="{main_color}"')
                    new_parts.append(part)
                svg_text = '<path '.join(new_parts)
            else:
                svg_text = svg_text.replace('fill="currentColor"', f'fill="{main_color}"')
        else:
            svg_text = svg_text.replace('fill="currentColor"', f'fill="{main_color}"')

        # Mirroring and Rotation
        transforms = []
        if mirrored:
            transforms.append("scale(-1, 1)")
        if rotation in (90, 180, 270):
            transforms.append(f"rotate({rotation} 128 128)")

        if transforms:
            transform_str = " ".join(transforms)
            svg_text = svg_text.replace(
                '<svg ',
                f'<svg transform-origin="center" '
            )
            # Wrap content in <g> with transform
            content_start = svg_text.find('>') + 1
            content_end = svg_text.rfind('</svg>')
            if content_start > 0 and content_end > content_start:
                header = svg_text[:content_start]
                body = svg_text[content_start:content_end]
                svg_text = f'{header}<g transform="{transform_str}" transform-origin="128 128">{body}</g></svg>'

        return svg_text


def re_sub_opacity(svg_text: str, opacity: float) -> str:
    import re
    return re.sub(r'opacity="[^"]+"', f'opacity="{opacity}"', svg_text)


@lru_cache(maxsize=1024)
def _render_pixmap_cached(
    name: str,
    weight: str,
    width: int,
    height: int,
    color: str,
    secondary_color: Optional[str],
    secondary_opacity: float,
    mirrored: bool,
    rotation: int,
    dpr: float = 1.0
) -> QtGui.QPixmap:
    """Internal LRU-cached pixmap renderer."""
    svg_path = PhosphorEngine.get_svg_path(name, weight)
    if not svg_path.exists():
        # Empty transparent pixmap if missing
        pm = QtGui.QPixmap(width, height)
        pm.fill(QtCore.Qt.GlobalColor.transparent)
        return pm

    raw_svg = svg_path.read_text(encoding="utf-8")
    processed_svg = PhosphorEngine.process_svg(
        raw_svg,
        color=color,
        secondary_color=secondary_color,
        secondary_opacity=secondary_opacity,
        mirrored=mirrored,
        rotation=rotation
    )

    # Physical resolution accounting for DPR
    phys_w = int(width * dpr)
    phys_h = int(height * dpr)

    renderer = QtSvg.QSvgRenderer(QtCore.QByteArray(processed_svg.encode("utf-8")))
    pixmap = QtGui.QPixmap(phys_w, phys_h)
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)

    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()

    if dpr != 1.0:
        pixmap.setDevicePixelRatio(dpr)

    return pixmap


@lru_cache(maxsize=1024)
def _render_icon_cached(
    name: str,
    weight: str,
    size: int,
    color: str,
    secondary_color: Optional[str],
    secondary_opacity: float,
    mirrored: bool,
    rotation: int
) -> QtGui.QIcon:
    """Internal LRU-cached icon renderer."""
    pixmap = _render_pixmap_cached(
        name=name,
        weight=weight,
        width=size,
        height=size,
        color=color,
        secondary_color=secondary_color,
        secondary_opacity=secondary_opacity,
        mirrored=mirrored,
        rotation=rotation
    )
    return QtGui.QIcon(pixmap)


def clear_theme_icon_cache(theme_name: str = ""):
    """Clears the icon LRU caches so theme token colors re-render with new colors."""
    _render_pixmap_cached.cache_clear()
    _render_icon_cached.cache_clear()


if HAS_THEME_ENGINE and ThemeEngine:
    try:
        ThemeEngine.instance().themeChanged.connect(clear_theme_icon_cache)
    except Exception:
        pass


class PhosphorIconBase:
    """Base class for every Phosphor Icon class (e.g. PhHouse, PhGear)."""
    name: str = ""
    pascal_name: str = ""

    @classmethod
    def icon(
        cls,
        size: int = 24,
        color: Union[str, QtGui.QColor, None] = None,
        weight: str = "regular",
        secondary_color: Union[str, QtGui.QColor, None] = None,
        secondary_opacity: float = 0.2,
        mirrored: bool = False,
        rotation: int = 0
    ) -> QtGui.QIcon:
        """Returns a QIcon for this icon."""
        c_str = _parse_color(color)
        sc_str = _parse_color(secondary_color) if secondary_color else None
        res = _render_icon_cached(
            name=cls.name,
            weight=weight,
            size=size,
            color=c_str,
            secondary_color=sc_str,
            secondary_opacity=secondary_opacity,
            mirrored=mirrored,
            rotation=rotation
        )
        try:
            res._ph_spec = {
                "name": cls.name,
                "weight": weight,
                "size": size,
                "color": color,
                "secondary_color": secondary_color,
                "secondary_opacity": secondary_opacity,
                "mirrored": mirrored,
                "rotation": rotation,
            }
        except Exception:
            pass
        return res

    @classmethod
    def pixmap(
        cls,
        size: Union[int, Tuple[int, int]] = 24,
        color: Union[str, QtGui.QColor, None] = None,
        weight: str = "regular",
        secondary_color: Union[str, QtGui.QColor, None] = None,
        secondary_opacity: float = 0.2,
        mirrored: bool = False,
        rotation: int = 0,
        dpr: float = 1.0
    ) -> QtGui.QPixmap:
        """Returns a QPixmap for this icon."""
        w, h = (size, size) if isinstance(size, int) else size
        c_str = _parse_color(color)
        sc_str = _parse_color(secondary_color) if secondary_color else None
        return _render_pixmap_cached(
            name=cls.name,
            weight=weight,
            width=w,
            height=h,
            color=c_str,
            secondary_color=sc_str,
            secondary_opacity=secondary_opacity,
            mirrored=mirrored,
            rotation=rotation,
            dpr=dpr
        )

    @classmethod
    def regular(cls, color=None, size=24, **kwargs) -> QtGui.QIcon:
        return cls.icon(size=size, color=color, weight="regular", **kwargs)

    @classmethod
    def bold(cls, color=None, size=24, **kwargs) -> QtGui.QIcon:
        return cls.icon(size=size, color=color, weight="bold", **kwargs)

    @classmethod
    def fill(cls, color=None, size=24, **kwargs) -> QtGui.QIcon:
        return cls.icon(size=size, color=color, weight="fill", **kwargs)

    @classmethod
    def light(cls, color=None, size=24, **kwargs) -> QtGui.QIcon:
        return cls.icon(size=size, color=color, weight="light", **kwargs)

    @classmethod
    def thin(cls, color=None, size=24, **kwargs) -> QtGui.QIcon:
        return cls.icon(size=size, color=color, weight="thin", **kwargs)

    @classmethod
    def duotone(cls, color=None, secondary_color=None, size=24, **kwargs) -> QtGui.QIcon:
        return cls.icon(size=size, color=color, weight="duotone", secondary_color=secondary_color, **kwargs)

    @classmethod
    def widget(cls, size=24, color=None, weight="regular", **kwargs) -> QtWidgets.QWidget:
        from .widget import PhIconWidget
        return PhIconWidget(icon=cls.name, size=size, color=color, weight=weight, **kwargs)


class PhFactory:
    """Namespace for accessing icons dynamically or listing/searching icon metadata."""

    @staticmethod
    def icon(
        name: str,
        weight: str = "regular",
        size: int = 24,
        color: Union[str, QtGui.QColor, None] = None,
        secondary_color: Union[str, QtGui.QColor, None] = None,
        secondary_opacity: float = 0.2,
        mirrored: bool = False,
        rotation: int = 0
    ) -> QtGui.QIcon:
        c_str = _parse_color(color)
        sc_str = _parse_color(secondary_color) if secondary_color else None
        res = _render_icon_cached(
            name=name,
            weight=weight,
            size=size,
            color=c_str,
            secondary_color=sc_str,
            secondary_opacity=secondary_opacity,
            mirrored=mirrored,
            rotation=rotation
        )
        try:
            res._ph_spec = {
                "name": name,
                "weight": weight,
                "size": size,
                "color": color,
                "secondary_color": secondary_color,
                "secondary_opacity": secondary_opacity,
                "mirrored": mirrored,
                "rotation": rotation,
            }
        except Exception:
            pass
        return res

    @staticmethod
    def pixmap(
        name: str,
        weight: str = "regular",
        size: Union[int, Tuple[int, int]] = 24,
        color: Union[str, QtGui.QColor, None] = None,
        secondary_color: Union[str, QtGui.QColor, None] = None,
        secondary_opacity: float = 0.2,
        mirrored: bool = False,
        rotation: int = 0,
        dpr: float = 1.0
    ) -> QtGui.QPixmap:
        w, h = (size, size) if isinstance(size, int) else size
        c_str = _parse_color(color)
        sc_str = _parse_color(secondary_color) if secondary_color else None
        return _render_pixmap_cached(
            name=name,
            weight=weight,
            width=w,
            height=h,
            color=c_str,
            secondary_color=sc_str,
            secondary_opacity=secondary_opacity,
            mirrored=mirrored,
            rotation=rotation,
            dpr=dpr
        )

    @staticmethod
    def widget(name: str, size=24, color=None, weight="regular", **kwargs) -> QtWidgets.QWidget:
        from .widget import PhIconWidget
        return PhIconWidget(icon=name, size=size, color=color, weight=weight, **kwargs)

    @staticmethod
    def search(query: str) -> List[Dict[str, Any]]:
        """Search icons by name, category, or tags."""
        q = query.lower().strip()
        results = []
        for item in CATALOG:
            if (
                q in item["name"].lower()
                or q in item["pascal_name"].lower()
                or any(q in cat for cat in item["categories"])
                or any(q in tag for tag in item["tags"])
            ):
                results.append(item)
        return results

    @staticmethod
    def list_all() -> List[str]:
        """List all icon kebab names."""
        return [item["name"] for item in CATALOG]

    @staticmethod
    def get_info(name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific icon."""
        kebab = PASCAL_TO_NAME.get(name, name).lower()
        for item in CATALOG:
            if item["name"] == kebab:
                return item
        return None


# Global namespace instance
Ph = PhFactory
