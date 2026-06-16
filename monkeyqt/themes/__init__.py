# -*- coding: utf-8 -*-
"""
MonkeyQt Themes — 67 种 UI 风格主题系统

用法:
    from monkeyqt.themes import ThemeEngine, ThemedButton, ThemedCard

    ThemeEngine.set_theme("Glassmorphism")
    btn = ThemedButton("Hello", btn_type="primary")
"""
from .engine import ThemeEngine
from .adapter import apply_monkeyqt_theme
from .manager import (
    clear_theme,
    clear_theme_chrome,
    exclude_from_theme,
    include_in_theme,
    set_theme_chrome,
    set_theme_enabled,
    use_theme,
)
from .components.button import ThemedButton
from .components.input import ThemedInput
from .components.switch import ThemedSwitch
from .components.card import ThemedCard
from .components.progress import ThemedProgressBar
from .components.alert import ThemedAlert
from .components.combobox import ThemedComboBox
from .components.slider import ThemedSlider
from .components.tabs import ThemedTabs
from .components.checkbox import ThemedCheckBox
from .components.progress_ring import ThemedProgressRing
from .components.avatar import ThemedAvatar
from .components.pagination import ThemedPagination
from .components.breadcrumb import ThemedBreadcrumb
from .components.dropdown import ThemedDropdown
from .components.table import ThemedTable
from .components.form import ThemedForm
from .components.date_picker import ThemedDatePicker
from .components.multicombobox import ThemedMultiComboBox
from .components.upload import ThemedUpload
from .components.topbar import ThemedTopbar
from .components.menu import ThemedMenu
from .components.message import ThemedMessage
from .components.captcha import ThemedCaptchaWidget
from .components.data_table import ThemedDataTable
from .components.image_compare import ThemedImageCompare
from .components.image_split import ThemedImageSplit
from .components.window import ThemedTitleBar, ThemedWindowShell
from .components.history_nav import ThemedHistoryNavigation
from .components.avatar_menu import ThemedAvatarMenu
from .components.theme_selector import MkThemeSelector

__all__ = [
    "ThemeEngine",
    "apply_monkeyqt_theme",
    "use_theme",
    "set_theme_chrome",
    "clear_theme_chrome",
    "clear_theme",
    "set_theme_enabled",
    "exclude_from_theme",
    "include_in_theme",
    "ThemedButton",
    "ThemedCheckBox",
    "ThemedInput",
    "ThemedSwitch",
    "ThemedCard",
    "ThemedProgressBar",
    "ThemedProgressRing",
    "ThemedAlert",
    "ThemedComboBox",
    "ThemedSlider",
    "ThemedTabs",
    "ThemedAvatar",
    "ThemedPagination",
    "ThemedBreadcrumb",
    "ThemedDropdown",
    "ThemedTable",
    "ThemedForm",
    "ThemedDatePicker",
    "ThemedMultiComboBox",
    "ThemedUpload",
    "ThemedTopbar",
    "ThemedMenu",
    "ThemedMessage",
    "ThemedCaptchaWidget",
    "ThemedDataTable",
    "ThemedImageCompare",
    "ThemedImageSplit",
    "ThemedTitleBar",
    "ThemedWindowShell",
    "ThemedHistoryNavigation",
    "ThemedAvatarMenu",
    "MkThemeSelector",
]
