# -*- coding: utf-8 -*-
from .components.basic.button import MkButton
from .components.basic.checkbox import MkCheckBox
# Navigation
from .components.navigation.sidebar import MkMenu
from .components.navigation.topbar import MkTopbar
from .components.navigation.breadcrumb import MkBreadcrumb
from .components.navigation.tabs import MkTabs
from .components.navigation.pagination import MkPagination
from .components.navigation.dropdown import MkDropdown
from .components.navigation.history import MkAnimatedStackedWidget, MkHistoryNavigation
from .components.navigation.avatar_menu import MkAvatarMenu

# Form
from .components.form.switch import MkSwitch
from .components.form.slider import MkSlider
from .components.form.date_picker import MkDatePicker
from .components.form.form import MkForm
from .components.form.input import MkInput
from .components.form.captcha import MkCaptchaWidget
from .components.form.auth import MkAuthScreen, MkMessage
from .components.form.upload import MkUpload
from .components.form.combobox import MkComboBox
from .components.form.multicombobox import MkMultiComboBox

# Data
from .components.data.avatar import MkAvatar
from .components.data.pro_table import MkProTable
from .components.data.image_compare import MkImageCompare
from .components.data.image_split import MkImageSplit
from .components.data.console import MkConsole

# Feedback
from .components.feedback.alert import MkAlert
from .components.feedback.progress_bar import MkProgressBar
from .components.feedback.progress_ring import MkProgressRing
from .components.feedback.card import MkCard
from .components.feedback.tooltip import (
    MkTooltipPopover,
    MkInfoIcon,
    MkInfoIconButton,
    MkTooltip,
    create_field_header,
    create_input_field,
    create_switch_field,
)

# Layout
from .components.layout.window import MkTitleBar, MkWindow
from .components.layout.window_shell import MkWindowShell
from .components.layout.box import MkQVBoxLayout, MkQHBoxLayout, MkVBox, MkHBox
from .components.layout.widget import MkQWidget, MkWidget


# Themes (68 UI Styles)
from .themes import (
    ThemeEngine,
    apply_monkeyqt_theme,
    use_theme,
    set_theme_chrome,
    clear_theme_chrome,
    clear_theme,
    set_theme_enabled,
    exclude_from_theme,
    include_in_theme,
    MkThemeSelector,
)

__version__ = "0.2.1"

__all__ = [
    "MkButton",
    "MkCheckBox",
    "MkMenu",
    "MkTopbar",
    "MkBreadcrumb",
    "MkTabs",
    "MkPagination",
    "MkDropdown",
    "MkAnimatedStackedWidget",
    "MkHistoryNavigation",
    "MkAvatarMenu",
    "MkSwitch",
    "MkSlider",
    "MkDatePicker",
    "MkForm",
    "MkInput",
    "MkComboBox",
    "MkMultiComboBox",
    "MkCaptchaWidget",
    "MkAuthScreen",
    "MkMessage",
    "MkUpload",
    "MkAvatar",
    "MkProTable",
    "MkImageCompare",
    "MkImageSplit",
    "MkConsole",
    "MkAlert",
    "MkProgressBar",
    "MkProgressRing",
    "MkCard",
    "MkTooltipPopover",
    "MkInfoIcon",
    "MkInfoIconButton",
    "MkTooltip",
    "create_field_header",
    "create_input_field",
    "create_switch_field",
    "MkTitleBar",
    "MkWindow",
    "MkWindowShell",
    "MkQVBoxLayout",
    "MkQHBoxLayout",
    "MkVBox",
    "MkHBox",
    "MkQWidget",
    "MkWidget",
    # Theme engine and helpers
    "ThemeEngine",
    "apply_monkeyqt_theme",
    "use_theme",
    "set_theme_chrome",
    "clear_theme_chrome",
    "clear_theme",
    "set_theme_enabled",
    "exclude_from_theme",
    "include_in_theme",
    "MkThemeSelector",
]
