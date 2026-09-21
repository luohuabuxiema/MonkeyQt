# -*- coding: utf-8 -*-
"""
Unified MonkeyQt Component QSS Builder
Encapsulates all MonkeyQt component styling into a modular, high-performance QSS stylesheet.
Dispatched natively via Qt's C++ cascading style engine on topLevelWidgets and QApplication,
enabling millisecond-level theme switching across all components.
"""
from __future__ import annotations
from typing import Optional, Dict, Any
from .adapter import _palette, CHECK_SVG_URL
from .style_utils import darken, lighten, readable_text


def build_button_qss(p: Dict[str, Any]) -> str:
    """Build QSS rules for QPushButton and MkButton types, sizes, and states."""
    primary = str(p["primary"])
    primary_text = str(p["primary_text"])
    primary_hover = lighten(primary, 0.12)
    primary_pressed = darken(primary, 0.10)
    radius = str(p["radius"])
    border = str(p["border"])
    surface = str(p["surface"])
    surface_muted = str(p["surface_muted"])
    text = str(p["text"])
    is_dark = bool(p["dark"])

    sec_hover_bg = "rgba(59, 130, 246, 0.18)" if is_dark else "rgba(59, 130, 246, 0.08)"

    if is_dark:
        # 参考图一暗黑现代化默认按钮规范（鼠标悬停保持深炭灰微亮提升，文字纯白，绝不变白）
        def_bg = "#212121"
        def_fg = "#FAFAFA"
        def_border = "#303030"
        def_hover_bg = "#282828"
        def_hover_fg = "#FAFAFA"
        def_hover_border = "#383838"
        def_press_bg = "#1C1C1C"
        def_press_fg = "#FAFAFA"
        def_press_border = "#2A2A2A"
        dis_bg = "#7E7E7E"
        dis_fg = "#212121"
        dis_border = "#7E7E7E"
    else:
        def_bg = surface
        def_fg = text
        def_border = border
        def_hover_bg = surface_muted
        def_hover_fg = primary
        def_hover_border = primary
        def_press_bg = darken(surface, 0.08)
        def_press_fg = primary
        def_press_border = primary
        dis_bg = surface_muted
        dis_fg = str(p["muted"])
        dis_border = border

    return f"""
        /* ── Base Buttons ── */
        QPushButton, MkButton {{
            font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
            font-size: 13px;
            font-weight: 500;
            border-radius: {radius};
            padding: 6px 14px;
            outline: none;
        }}

        /* Primary Type */
        QPushButton[mk_type="primary"], MkButton[mk_type="primary"] {{
            background-color: {primary};
            color: {primary_text};
            border: 1px solid {primary};
            font-weight: 600;
        }}
        QPushButton[mk_type="primary"]:hover, MkButton[mk_type="primary"]:hover {{
            background-color: {primary_hover};
            border-color: {primary_hover};
        }}
        QPushButton[mk_type="primary"]:pressed, MkButton[mk_type="primary"]:pressed {{
            background-color: {primary_pressed};
            border-color: {primary_pressed};
        }}

        /* Success Type */
        QPushButton[mk_type="success"], MkButton[mk_type="success"] {{
            background-color: #10B981;
            color: #FFFFFF;
            border: 1px solid #10B981;
            font-weight: 600;
        }}
        QPushButton[mk_type="success"]:hover, MkButton[mk_type="success"]:hover {{
            background-color: #34D399;
            border-color: #34D399;
        }}
        QPushButton[mk_type="success"]:pressed, MkButton[mk_type="success"]:pressed {{
            background-color: #059669;
            border-color: #059669;
        }}

        /* Danger & Error Type */
        QPushButton[mk_type="danger"], MkButton[mk_type="danger"],
        QPushButton[mk_type="error"], MkButton[mk_type="error"] {{
            background-color: #EF4444;
            color: #FFFFFF;
            border: 1px solid #EF4444;
            font-weight: 600;
        }}
        QPushButton[mk_type="danger"]:hover, MkButton[mk_type="danger"]:hover,
        QPushButton[mk_type="error"]:hover, MkButton[mk_type="error"]:hover {{
            background-color: #F87171;
            border-color: #F87171;
        }}
        QPushButton[mk_type="danger"]:pressed, MkButton[mk_type="danger"]:pressed,
        QPushButton[mk_type="error"]:pressed, MkButton[mk_type="error"]:pressed {{
            background-color: #DC2626;
            border-color: #DC2626;
        }}

        /* Warning Type */
        QPushButton[mk_type="warning"], MkButton[mk_type="warning"] {{
            background-color: #F59E0B;
            color: #111827;
            border: 1px solid #F59E0B;
            font-weight: 600;
        }}
        QPushButton[mk_type="warning"]:hover, MkButton[mk_type="warning"]:hover {{
            background-color: #FBBF24;
            border-color: #FBBF24;
        }}
        QPushButton[mk_type="warning"]:pressed, MkButton[mk_type="warning"]:pressed {{
            background-color: #D97706;
            border-color: #D97706;
        }}

        /* Secondary / Outline Type */
        QPushButton[mk_type="secondary"], MkButton[mk_type="secondary"],
        QPushButton[mk_type="outline"], MkButton[mk_type="outline"] {{
            background-color: transparent;
            color: {primary};
            border: 1px solid {primary};
            font-weight: 600;
        }}
        QPushButton[mk_type="secondary"]:hover, MkButton[mk_type="secondary"]:hover,
        QPushButton[mk_type="outline"]:hover, MkButton[mk_type="outline"]:hover {{
            background-color: {sec_hover_bg};
        }}

        /* Default & Fallback Type */
        QPushButton[mk_type="default"], MkButton[mk_type="default"], QPushButton {{
            background-color: {def_bg};
            color: {def_fg};
            border: 1px solid {def_border};
        }}
        QPushButton[mk_type="default"]:hover, MkButton[mk_type="default"]:hover {{
            background-color: {def_hover_bg};
            border-color: {def_hover_border};
            color: {def_hover_fg};
        }}
        QPushButton[mk_type="default"]:pressed, MkButton[mk_type="default"]:pressed {{
            background-color: {def_press_bg};
            border-color: {def_press_border};
            color: {def_press_fg};
        }}

        /* Disabled state */
        QPushButton:disabled, MkButton:disabled {{
            background-color: {dis_bg};
            color: {dis_fg};
            border-color: {dis_border};
        }}

        /* Size variants */
        QPushButton[mk_size="small"], MkButton[mk_size="small"] {{
            padding: 3px 10px;
            font-size: 12px;
            min-height: 24px;
        }}
        QPushButton[mk_size="large"], MkButton[mk_size="large"] {{
            padding: 9px 20px;
            font-size: 14px;
            min-height: 38px;
        }}
    """


def build_console_qss(p: Dict[str, Any]) -> str:
    """Build QSS rules for MkConsole, ensuring crisp scoped styling without border leaks."""
    # MkConsole manages its own rich modern styling, custom scrollbars and interactive pills
    return """
        /* ── MkConsole Scoped Base ── */
        QFrame#MkConsoleRoot {
            border: none;
        }
        QFrame#MkConsoleHeader {
            border: none;
            border-bottom: none;
        }
        QTextEdit#MkConsoleEditor {
            border: none;
            border-top: none;
            outline: none;
        }
    """


def build_menu_and_sidebar_qss(p: Dict[str, Any]) -> str:
    """Build QSS rules for sidebar navigation, MkMenu, and MkMenuItem."""
    is_dark = bool(p["dark"])
    sidebar_surface = str(p["sidebar_surface"])
    sidebar_text = str(p["sidebar_text"])
    sidebar_muted = str(p["sidebar_muted"])
    border = str(p["border"])
    radius = "8px"

    item_hover_bg = str(p.get("sidebar_hover_bg", "rgba(255, 255, 255, 0.06)" if is_dark else "rgba(0, 0, 0, 0.04)"))
    item_checked_bg = str(p.get("sidebar_active_bg", "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(0, 0, 0, 0.08)"))
    item_active_fg = str(p.get("sidebar_active_fg", "#FFFFFF" if is_dark else "#0F172A"))

    return f"""
        /* ── MkMenu & Sidebar Navigation ── */
        MkMenu {{
            background-color: {sidebar_surface};
            border: none;
        }}
        QFrame#SidebarInnerFrame {{
            background-color: {sidebar_surface};
            border: none;
            border-right: 1px solid {border};
        }}
        QFrame#SidebarInnerFrame[border_right_none="true"] {{
            border-right: none;
        }}
        QWidget#SidebarTitleArea {{
            background-color: transparent;
            border: none;
        }}
        QWidget#SidebarTitleArea QLabel, QLabel#SidebarTitleLabel {{
            background: transparent;
            color: {sidebar_text};
            font-size: 15px;
            font-weight: bold;
            border: none;
        }}
        QPushButton#SidebarHamburgerButton, QPushButton#SidebarHeaderCollapseButton {{
            border: none;
            background: transparent;
        }}
        QPushButton#SidebarHamburgerButton:hover, QPushButton#SidebarHeaderCollapseButton:hover {{
            background-color: {item_hover_bg};
            border-radius: 6px;
        }}

        MkMenuItem {{
            border: none;
            background: transparent;
            border-radius: 8px;
            margin: 2px 10px;
            padding: 0px 8px;
            color: {sidebar_muted};
        }}
        MkMenuItem QLabel {{
            background: transparent;
            border: none;
            color: {sidebar_muted};
            font-size: 14px;
            font-weight: 500;
        }}
        MkMenuItem:hover {{
            background-color: {item_hover_bg};
            border-radius: 8px;
        }}
        MkMenuItem:hover QLabel {{
            color: {item_active_fg};
        }}
        MkMenuItem[checked="true"], MkMenuItem:checked {{
            background-color: {item_checked_bg};
            color: {item_active_fg};
            border-radius: 8px;
        }}
        MkMenuItem[checked="true"] QLabel, MkMenuItem:checked QLabel {{
            color: {item_active_fg};
            font-weight: 600;
        }}

        MkSubMenu {{
            background: transparent;
            border: none;
        }}
        MkSubMenu QPushButton, SubMenuTitleButton, QPushButton#SubMenuTitleBtn {{
            border: none;
            background: transparent;
            border-radius: 8px;
            margin: 2px 10px;
            padding: 0px 8px;
            color: {sidebar_text};
            font-weight: 500;
        }}
        MkSubMenu QPushButton:hover, SubMenuTitleButton:hover, QPushButton#SubMenuTitleBtn:hover {{
            background-color: {item_hover_bg};
            border-radius: 8px;
        }}
        MkSubMenu QLabel {{
            background: transparent;
            border: none;
            color: {sidebar_text};
            font-size: 14px;
            font-weight: 500;
        }}
        MkSubMenu:hover QLabel {{
            color: {item_active_fg};
        }}
        QScrollArea#SidebarScrollArea {{
            background: transparent;
            border: none;
        }}
        QWidget#SidebarContentWidget {{
            background: transparent;
            border: none;
        }}
    """


def build_scrollbar_qss(p: Dict[str, Any]) -> str:
    """Build sleek, modern high-contrast scrollbar QSS."""
    is_dark = bool(p["dark"])
    thumb = "rgba(255, 255, 255, 0.22)" if is_dark else "rgba(0, 0, 0, 0.18)"
    thumb_hover = "rgba(255, 255, 255, 0.38)" if is_dark else "rgba(0, 0, 0, 0.32)"

    return f"""
        /* ── Universal Scrollbars ── */
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {thumb};
            min-height: 24px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {thumb_hover};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            width: 0px; height: 0px; border: none; background: none;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QScrollBar:horizontal {{
            border: none;
            background: transparent;
            height: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {thumb};
            min-width: 24px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {thumb_hover};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px; height: 0px; border: none; background: none;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        QScrollBar::corner {{
            background: transparent;
        }}
    """


def build_table_qss(p: Dict[str, Any]) -> str:
    """Build QSS rules for QTableWidget, QTableView, MkTable, and MkDataTable."""
    is_dark = bool(p["dark"])
    surface = str(p["surface"])
    surface_muted = str(p["surface_muted"])
    border = str(p["border"])
    text = str(p["text"])
    muted = str(p["muted"])
    radius = str(p["radius"])

    sel_bg = "rgba(59, 130, 246, 0.25)" if is_dark else "rgba(59, 130, 246, 0.12)"
    sel_fg = "#93C5FD" if is_dark else "#1D4ED8"

    return f"""
        /* ── Tables & DataGrids ── */
        QTableWidget, QTableView, MkTable, MkDataTable {{
            background-color: {surface};
            color: {text};
            gridline-color: {border};
            border: 1px solid {border};
            border-radius: {radius};
            selection-background-color: {sel_bg};
            selection-color: {sel_fg};
            alternate-background-color: {surface_muted};
            outline: none;
        }}
        QHeaderView::section {{
            background-color: {surface_muted};
            color: {muted};
            border: none;
            border-bottom: 1px solid {border};
            padding: 6px 10px;
            font-weight: 600;
            font-size: 12px;
        }}
        QTableCornerButton::section {{
            background-color: {surface_muted};
            border: none;
        }}
        MkTable QHeaderView, MkDataTable QHeaderView, MkProTable QHeaderView {{
            background-color: transparent;
            background: transparent;
            border: none;
        }}
        MkTable QHeaderView::section, MkDataTable QHeaderView::section, MkProTable QHeaderView::section {{
            background-color: transparent;
            background: transparent;
            border: none;
        }}
        QTableWidget::item, QTableView::item {{
            padding: 6px 8px;
            border-bottom: 1px solid {border};
        }}
        QTableWidget::item:selected, QTableView::item:selected {{
            background-color: {sel_bg};
            color: {sel_fg};
        }}
    """


def build_form_controls_qss(p: Dict[str, Any]) -> str:
    """Build QSS rules for Inputs, Checkboxes, ComboBoxes, Sliders, and Switches."""
    surface = str(p["surface"])
    surface_muted = str(p["surface_muted"])
    border = str(p["border"])
    text = str(p["text"])
    primary = str(p["primary"])
    primary_text = str(p["primary_text"])
    radius = str(p["radius"])
    is_dark = bool(p["dark"])
    input_focus_border = str(p.get("input_focus_border", "#FFFFFF" if is_dark else "#0F172A"))
    input_hover_border = str(p.get("input_hover_border", "rgba(255, 255, 255, 0.40)" if is_dark else "#94A3B8"))

    return f"""
        /* ── Form Controls & Inputs ── */
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, MkInput, MkDatePicker {{
            background-color: {surface};
            color: {text};
            border: 1px solid {border};
            border-radius: {radius};
            padding: 6px 10px;
            font-size: 13px;
            selection-background-color: {primary};
            selection-color: {primary_text};
        }}
        QLineEdit:hover, MkInput:hover, MkDatePicker:hover {{
            border-color: {input_hover_border};
        }}
        QLineEdit:focus, MkInput:focus, MkDatePicker:focus {{
            border-color: {input_focus_border};
        }}

        QComboBox, MkComboBox {{
            background-color: {surface};
            color: {text};
            border: 1px solid {border};
            border-radius: {radius};
            padding: 5px 10px;
            min-height: 28px;
        }}
        QComboBox:hover, MkComboBox:hover {{
            border-color: {primary};
        }}
        QComboBox::drop-down, MkComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox QAbstractItemView, MkComboBox QAbstractItemView {{
            background-color: {surface};
            color: {text};
            border: 1px solid {border};
            border-radius: {radius};
            selection-background-color: {primary};
            selection-color: {primary_text};
            padding: 4px;
            outline: none;
        }}

        /* Checkbox & Radio */
        MkCheckBox, QCheckBox, QRadioButton {{
            color: {text};
            spacing: 8px;
        }}
        MkCheckBox::indicator, QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {border};
            border-radius: 4px;
            background-color: {surface};
        }}
        MkCheckBox::indicator:hover, QCheckBox::indicator:hover {{
            border-color: {primary};
        }}
        MkCheckBox::indicator:checked, QCheckBox::indicator:checked {{
            background-color: {primary};
            border-color: {primary};
            image: url({CHECK_SVG_URL});
        }}

        /* Slider */
        QSlider {{
            background: transparent;
            border: none;
        }}
        QSlider::groove:horizontal {{
            height: 6px;
            background: {surface_muted};
            border: none;
            border-radius: 3px;
        }}
        QSlider::sub-page:horizontal {{
            background: {primary};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {primary};
            border: 2px solid {surface};
            width: 16px;
            height: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {lighten(primary, 0.12)};
        }}
    """


def build_card_and_feedback_qss(p: Dict[str, Any]) -> str:
    """Build QSS rules for MkCard, Tabs, Breadcrumbs, and Tooltips."""
    surface = str(p["surface"])
    border = str(p["border"])
    text = str(p["text"])
    muted = str(p["muted"])
    primary = str(p["primary"])
    radius = str(p["radius"])
    is_dark = bool(p["dark"])
    tip_bg = surface
    tip_fg = text

    return f"""
        /* ── Cards & Panels ── */
        MkCard {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: {radius};
        }}
        MkCard QLabel#MkCardTitle {{
            background: transparent;
            color: {text};
            font-size: 14px;
            font-weight: 700;
        }}

        /* ── Tabs & Breadcrumbs ── */
        MkTabs {{
            background: transparent;
            border: none;
        }}
        MkTabButton {{
            background: transparent;
            color: {muted};
            border: none;
            padding: 8px 16px;
            font-weight: 500;
        }}
        MkTabButton:hover {{
            color: {primary};
        }}
        MkTabButton[active="true"] {{
            color: {primary};
            font-weight: 600;
            border-bottom: 2px solid {primary};
        }}
        MkBreadcrumbItem {{
            color: {muted};
            background: transparent;
            border: none;
        }}
        MkBreadcrumbItem:hover {{
            color: {primary};
        }}

        /* ── Tooltips ── */
        QToolTip {{
            background-color: {tip_bg};
            color: {tip_fg};
            border: 1px solid {border};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
        }}
    """


def build_window_and_layout_qss(p: Dict[str, Any]) -> str:
    """Build QSS rules for MkWindow, MkTitleBar, and layout cards."""
    bg = str(p["bg"])
    chrome_surface = str(p["chrome_surface"])
    border = str(p["border"])
    surface = str(p["surface"])
    radius = str(p["radius"])

    return f"""
        /* ── Windows & Layout Containers ── */
        QWidget#MkWindowContainer, QFrame#MkWindowContainer {{
            background-color: {bg};
            border: 1px solid {border};
            border-radius: 8px;
        }}
        QWidget#MkWindowSidebarHost {{
            background-color: {p["sidebar_surface"]};
            border: none;
            border-top-left-radius: 8px;
            border-bottom-left-radius: 8px;
        }}
        QWidget#MkWindowSidebarHost MkMenu,
        QWidget#MkWindowSidebarHost QFrame#SidebarInnerFrame {{
            border-top-left-radius: 8px;
            border-bottom-left-radius: 8px;
        }}
        QWidget#MkWindowDesktopShell {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
        }}
        QWidget#MkWindowContentHost {{
            background-color: transparent;
            border: none;
            border-bottom-right-radius: 8px;
        }}
        MkTitleBar, QWidget#MkTitleBar {{
            background-color: {chrome_surface};
            border-bottom: 1px solid {border};
            border-top-right-radius: 8px;
        }}
        QPushButton#TitleBarCloseButton {{
            background-color: transparent;
            border: none;
            margin: 0px;
            padding: 0px;
        }}
        QPushButton#TitleBarCloseButton:hover {{
            background-color: transparent;
            border: none;
        }}
        QPushButton#TitleBarCloseButton:pressed {{
            background-color: transparent;
            border: none;
        }}
        QWidget#MainRightWidget {{
            border-bottom-right-radius: 8px;
        }}
        QFrame[mkPanel="true"] {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: {radius};
        }}
        QFrame[mkBorderless="true"] {{
            background-color: transparent;
            border: none;
        }}
    """


def build_all_monkeyqt_qss(palette: Optional[Dict[str, Any]] = None) -> str:
    """
    Assemble complete MonkeyQt unified QSS stylesheet.
    One single call builds all component rules for Qt native C++ tree cascade.
    """
    p = palette or _palette()
    return "\n".join([
        build_button_qss(p),
        build_console_qss(p),
        build_menu_and_sidebar_qss(p),
        build_scrollbar_qss(p),
        build_table_qss(p),
        build_form_controls_qss(p),
        build_card_and_feedback_qss(p),
        build_window_and_layout_qss(p)
    ])
