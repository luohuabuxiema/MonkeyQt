# -*- coding: utf-8 -*-
"""ThemedConsole — console log output component."""

from monkeyqt.components.data.console import MkConsole
from ..engine import ThemeEngine


class ThemedConsole(MkConsole):
    """Themed console log output component with auto-updating styles."""

    def __init__(self, title="控制台日志 / Console Logs", parent=None):
        super().__init__(title, parent)
        ThemeEngine.instance().themeChanged.connect(self.apply_theme_colors)
        self.apply_theme_colors()

    def set_theme_style(self, style_name: str = None):
        """Standard themed component method interface"""
        self.apply_theme_colors()
