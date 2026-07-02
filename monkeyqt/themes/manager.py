# -*- coding: utf-8 -*-
"""Global theme entry points for MonkeyQt applications."""

from __future__ import annotations

import re

from PySide6.QtCore import QObject, QEvent, QTimer
from PySide6.QtWidgets import QApplication, QWidget

from .adapter import (
    _THEME_DISABLED_PROP,
    _THEME_ENABLED_PROP,
    apply_monkeyqt_theme,
    restore_monkeyqt_theme,
)
from .engine import ThemeEngine
from .names import DEFAULT_THEME_CN_NAME, THEME_CN_NAMES
from .tokens import THEME_NAMES

_AUTO_THEME_MARK_PROP = "_mk_auto_theme_name"


def _alias_variants(name: str) -> set[str]:
    """Build practical Chinese/English variants for one theme name."""
    text = str(name).strip()
    if not text:
        return set()

    variants = {
        text,
        text.lower(),
        text.casefold(),
        text.replace(" ", ""),
        text.replace(" ", "").lower(),
        re.sub(r"[\s\-_]+", "-", text),
        re.sub(r"[\s\-_]+", "-", text).lower(),
        re.sub(r"[\s\-_]+", "_", text),
        re.sub(r"[\s\-_]+", "_", text).lower(),
    }

    no_punctuation = re.sub(r"[\s\-_()/&]+", "", text)
    variants.add(no_punctuation)
    variants.add(no_punctuation.lower())

    words_only = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", " ", text).strip()
    if words_only and words_only != text:
        variants.add(words_only)
        variants.add(words_only.lower())
        variants.add(words_only.replace(" ", ""))
        variants.add(words_only.replace(" ", "").lower())
        variants.add(words_only.replace(" ", "-"))
        variants.add(words_only.replace(" ", "-").lower())
        variants.add(words_only.replace(" ", "_"))
        variants.add(words_only.replace(" ", "_").lower())

    no_parentheses = re.sub(r"\s*\([^)]*\)", "", text).strip()
    if no_parentheses and no_parentheses != text:
        variants.update(_alias_variants(no_parentheses))

    for parenthetical in re.findall(r"\(([^)]*)\)", text):
        if parenthetical.strip():
            variants.update(_alias_variants(parenthetical.strip()))

    readable_parentheses = text.replace("(", "").replace(")", "")
    if readable_parentheses != text:
        variants.add(readable_parentheses)
        variants.add(readable_parentheses.lower())

    return {item.strip() for item in variants if item and item.strip()}


def _add_alias(aliases: dict[str, str], alias: str, target: str) -> None:
    alias = str(alias).strip()
    if not alias:
        return
    aliases[alias] = target
    aliases[alias.lower()] = target
    aliases[alias.casefold()] = target


def _build_theme_name_aliases() -> dict[str, str]:
    aliases: dict[str, str] = {}

    for alias in (
        DEFAULT_THEME_CN_NAME,
        ThemeEngine.DEFAULT_THEME_NAME,
        ThemeEngine.DEFAULT_THEME_KEY,
        "MonkeyQt",
        "MonkeyQt Default",
        "MonkeyQt默认",
        "MonkeyQt默认样式",
        "默认",
        "默认样式",
        "default",
    ):
        _add_alias(aliases, alias, ThemeEngine.DEFAULT_THEME_NAME)

    for theme_name in THEME_NAMES:
        display_name = THEME_CN_NAMES.get(theme_name, "")

        for alias in _alias_variants(theme_name):
            _add_alias(aliases, alias, theme_name)

        for alias in _alias_variants(display_name):
            _add_alias(aliases, alias, theme_name)

        if display_name:
            for alias in _alias_variants(f"{display_name} ({theme_name})"):
                _add_alias(aliases, alias, theme_name)

    extra_aliases = {
        "Dark": "Dark Mode (OLED)",
        "Dark Mode": "Dark Mode (OLED)",
        "OLED": "Dark Mode (OLED)",
        "深色": "Dark Mode (OLED)",
        "深色模式": "Dark Mode (OLED)",
        "暗黑": "Dark Mode (OLED)",
        "暗黑模式": "Dark Mode (OLED)",
        "黑色模式": "Dark Mode (OLED)",
        "夜间模式": "Dark Mode (OLED)",
        "夜间": "Dark Mode (OLED)",
        "LiquidGlass": "Liquid Glass",
        "Liquid Glass": "Liquid Glass",
        "Glass": "Glassmorphism",
        "玻璃": "Glassmorphism",
        "玻璃拟态": "Glassmorphism",
        "流态玻璃": "Liquid Glass",
        "液态玻璃": "Liquid Glass",
        "液体玻璃": "Liquid Glass",
        "流体玻璃": "Liquid Glass",
    }
    for alias, target in extra_aliases.items():
        for item in _alias_variants(alias):
            _add_alias(aliases, item, target)

    return aliases


_THEME_NAME_ALIASES = _build_theme_name_aliases()


class _ThemeAutoApplier(QObject):
    """Install once on QApplication and re-apply themes as widgets appear."""

    def __init__(self):
        super().__init__()
        self.root: QWidget | None = None
        self.enabled = True
        self._pending = False
        self._pending_full = False
        self._pending_widgets: list[QWidget] = []
        self._installed_app: QApplication | None = None

    def eventFilter(self, obj, event):
        if not self.enabled:
            return False
        if not ThemeEngine.current_theme():
            return False

        event_type = event.type()
        if event_type == QEvent.Type.ChildAdded:
            child = event.child() if hasattr(event, "child") else None
            if isinstance(child, QWidget):
                self.schedule(child)
        elif event_type == QEvent.Type.Show and isinstance(obj, QWidget):
            # Constructors may add or restyle internal children after ChildAdded
            # was handled. A forced Show pass catches the completed widget tree.
            self.schedule(obj, force=True)
        return False

    def install(self) -> None:
        app = QApplication.instance()
        if app is not None and app is not self._installed_app:
            app.installEventFilter(self)
            self._installed_app = app

    def schedule(self, widget: QWidget | None = None, *, force: bool = False) -> None:
        if widget is None:
            self._pending_full = True
        elif self._belongs_to_root(widget):
            self._queue_widget(widget, force=force)

        if self._pending:
            return
        self._pending = True
        QTimer.singleShot(16, self.apply)

    def apply(self) -> None:
        self._pending = False
        if self._pending_full:
            self._pending_full = False
            self._pending_widgets.clear()
            apply_monkeyqt_theme(self.root)
            self._mark_applied(self.root)
            return

        widgets = self._take_compact_widgets()
        for widget in widgets:
            try:
                if not self._belongs_to_root(widget):
                    continue
                apply_monkeyqt_theme(widget)
                self._mark_applied(widget)
            except RuntimeError:
                continue

    def _queue_widget(self, widget: QWidget, *, force: bool = False) -> None:
        try:
            if not force and widget.property(_AUTO_THEME_MARK_PROP) == ThemeEngine.current_theme():
                return
        except RuntimeError:
            return

        for existing in self._pending_widgets:
            if existing is widget or self._is_ancestor(existing, widget):
                return
        self._pending_widgets = [
            existing for existing in self._pending_widgets
            if not self._is_ancestor(widget, existing)
        ]
        self._pending_widgets.append(widget)

    def _take_compact_widgets(self) -> list[QWidget]:
        widgets = self._pending_widgets
        self._pending_widgets = []
        compact: list[QWidget] = []
        for widget in widgets:
            if any(self._is_ancestor(existing, widget) for existing in compact):
                continue
            compact = [existing for existing in compact if not self._is_ancestor(widget, existing)]
            compact.append(widget)
        return compact

    def _belongs_to_root(self, widget: QWidget) -> bool:
        if self.root is None:
            return True
        return widget is self.root or self._is_ancestor(self.root, widget)

    @staticmethod
    def _is_ancestor(ancestor: QWidget, widget: QWidget) -> bool:
        try:
            current = widget
            while current is not None:
                if current is ancestor:
                    return True
                current = current.parentWidget()
        except RuntimeError:
            return False
        return False

    def _mark_applied(self, root: QWidget | None) -> None:
        theme = ThemeEngine.current_theme()
        if root is not None:
            widgets = [root]
            widgets.extend(root.findChildren(QWidget))
        else:
            app = QApplication.instance()
            widgets = app.allWidgets() if app is not None else []

        for widget in widgets:
            try:
                widget.setProperty(_AUTO_THEME_MARK_PROP, theme)
            except RuntimeError:
                pass


_auto_applier: _ThemeAutoApplier | None = None


def _manager() -> _ThemeAutoApplier:
    global _auto_applier
    if _auto_applier is None:
        _auto_applier = _ThemeAutoApplier()
    _auto_applier.install()
    return _auto_applier


def use_theme(
    style_name: str, 
    root: QWidget | None = None, 
    *, 
    auto: bool = True,
    chrome_bg: str | None = None,
    titlebar_bg: str | None = None,
    sidebar_bg: str | None = None
) -> bool:
    """Set a global MonkeyQt theme and auto-apply it to current/future widgets.

    Usage:
        app = QApplication(sys.argv)
        use_theme("Dark Mode (OLED)", titlebar_bg="#121212", sidebar_bg="#1E1E1E")
        use_theme("Liquid Glass", chrome_bg="#F8FBFF")
        window = MainWindow()

    Pass root to limit automatic styling to one window or one subtree.
    """
    manager = _manager()
    manager.root = root
    manager.enabled = auto

    _set_chrome_overrides(
        chrome_bg=chrome_bg,
        titlebar_bg=titlebar_bg,
        sidebar_bg=sidebar_bg,
        clear_missing=True,
        refresh=False,
    )

    ok = ThemeEngine.set_theme(_normalize_theme_name(style_name))
    if ok:
        apply_monkeyqt_theme(root)
        manager._mark_applied(root)
    return ok


def set_theme_chrome(
    *,
    chrome_bg: str | None = None,
    titlebar_bg: str | None = None,
    sidebar_bg: str | None = None,
    root: QWidget | None = None,
) -> None:
    """Override titlebar/sidebar colors for the active theme in one line."""
    _set_chrome_overrides(
        chrome_bg=chrome_bg,
        titlebar_bg=titlebar_bg,
        sidebar_bg=sidebar_bg,
        clear_missing=False,
        refresh=True,
    )
    apply_monkeyqt_theme(root)
    _manager()._mark_applied(root)


def clear_theme_chrome(root: QWidget | None = None) -> None:
    """Return titlebar/sidebar colors to the current theme's automatic palette."""
    ThemeEngine.set_overrides(remove=["--titlebar-bg", "--sidebar-bg"], refresh=True)
    apply_monkeyqt_theme(root)
    _manager()._mark_applied(root)


def _set_chrome_overrides(
    *,
    chrome_bg: str | None,
    titlebar_bg: str | None,
    sidebar_bg: str | None,
    clear_missing: bool,
    refresh: bool,
) -> None:
    if chrome_bg is not None:
        titlebar_bg = titlebar_bg or chrome_bg
        sidebar_bg = sidebar_bg or chrome_bg

    updates: dict[str, str] = {}
    remove: list[str] = []

    if titlebar_bg is None:
        if clear_missing:
            remove.append("--titlebar-bg")
    else:
        updates["--titlebar-bg"] = titlebar_bg

    if sidebar_bg is None:
        if clear_missing:
            remove.append("--sidebar-bg")
    else:
        updates["--sidebar-bg"] = sidebar_bg

    ThemeEngine.set_overrides(updates, remove=remove, refresh=refresh)


def _normalize_theme_name(style_name: str) -> str:
    """Accept both internal English keys and Chinese display names."""
    name = str(style_name).strip()
    if name in _THEME_NAME_ALIASES:
        return _THEME_NAME_ALIASES[name]
    lowered = name.lower()
    if lowered in _THEME_NAME_ALIASES:
        return _THEME_NAME_ALIASES[lowered]
    return name


def clear_theme(root: QWidget | None = None) -> bool:
    """Restore MonkeyQt default styling and remove token QSS."""
    manager = _manager()
    if root is not None:
        manager.root = root
    ok = ThemeEngine.clear_theme()
    if ok:
        apply_monkeyqt_theme(root)
    return ok


def set_theme_enabled(widget: QWidget, enabled: bool = True, *, recursive: bool = True) -> None:
    """Enable or disable global theme adaptation for one widget subtree.

    Disabled widgets keep their own local styles. Re-enabling applies the current
    global theme again.
    """
    if widget is None:
        return

    widgets = [widget]
    if recursive:
        widgets.extend(widget.findChildren(QWidget))

    for item in widgets:
        item.setProperty(_THEME_ENABLED_PROP, enabled)
        item.setProperty(_THEME_DISABLED_PROP, not enabled)
        item.style().unpolish(item)
        item.style().polish(item)
        item.update()

    if enabled:
        apply_monkeyqt_theme(widget)
    else:
        restore_monkeyqt_theme(widget)


def exclude_from_theme(widget: QWidget, *, recursive: bool = True) -> None:
    """Convenience wrapper for set_theme_enabled(widget, False)."""
    set_theme_enabled(widget, False, recursive=recursive)


def include_in_theme(widget: QWidget, *, recursive: bool = True) -> None:
    """Convenience wrapper for set_theme_enabled(widget, True)."""
    set_theme_enabled(widget, True, recursive=recursive)
