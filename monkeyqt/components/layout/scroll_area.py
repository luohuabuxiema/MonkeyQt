# -*- coding: utf-8 -*-
"""
@File : scroll_area.py
@Desc : Modern minimalist web-style auto-scrolling area and adaptive stacked container for MonkeyQt.
"""
from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QFrame, QWidget, QStackedWidget
from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import modern_scrollbar_qss


class MkStackedWidget(QStackedWidget):
    """
    Adaptive stacked widget whose sizeHint and minimumSizeHint
    dynamically track the current active page, enabling seamless
    auto-scrolling when placed inside an MkScrollArea.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("MkStackedWidget")
        self.currentChanged.connect(self._on_current_changed)

    def _on_current_changed(self, index: int):
        self.updateGeometry()

    def sizeHint(self):
        curr = self.currentWidget()
        if curr is not None:
            return curr.sizeHint()
        return super().sizeHint()

    def minimumSizeHint(self):
        curr = self.currentWidget()
        if curr is not None:
            return curr.minimumSizeHint()
        return super().minimumSizeHint()


class MkScrollArea(QScrollArea):
    """
    Modern minimalist web-style auto-scrolling container (similar to modern web apps).

    Features:
    - Zero borders, transparent background by default
    - Automatic horizontal fitting (widgetResizable=True)
    - Vertical scrolling appears automatically when content height exceeds viewport
    - Sleek 7px capsule scrollbar without native arrows, adaptive to all 68 themes
    - Smooth scrolling and convenience APIs (scroll_to_top, scroll_to_bottom, scroll_to_widget)
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        horizontal: bool = False,
        scrollbar_width: int = 7,
    ):
        super().__init__(parent)
        self.setObjectName("MkScrollArea")
        self._horizontal = horizontal
        self._scrollbar_width = scrollbar_width

        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFrameShadow(QFrame.Shadow.Plain)

        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded if horizontal else Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        if self.viewport():
            self.viewport().setObjectName("MkScrollAreaViewport")
            self.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.viewport().setAutoFillBackground(False)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        ThemeEngine.instance().themeChanged.connect(self.update_theme_style)
        self.update_theme_style()

    def setWidget(self, widget: QWidget):
        if widget is not None:
            widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            self._connect_stacked_widgets(widget)
        super().setWidget(widget)

    def _connect_stacked_widgets(self, root: QWidget):
        stacks = [root] if isinstance(root, QStackedWidget) else root.findChildren(QStackedWidget)
        for stack in stacks:
            try:
                stack.currentChanged.connect(self._on_stack_page_changed)
            except Exception:
                pass

    def _on_stack_page_changed(self, index: int):
        self.verticalScrollBar().setValue(0)
        self.updateGeometry()

    def update_theme_style(self, theme_name: str = ""):
        t = ThemeEngine
        is_dark = t.is_dark()
        qss = modern_scrollbar_qss(
            is_dark=is_dark,
            width=self._scrollbar_width,
            radius=self._scrollbar_width // 2,
        )
        self.setStyleSheet(f"""
            QScrollArea#MkScrollArea {{
                background: transparent;
                border: none;
            }}
            QWidget#MkScrollAreaViewport {{
                background: transparent;
                border: none;
            }}
            {qss}
        """)

    def scroll_to_top(self):
        """Scroll smoothly to the top of the content."""
        self.verticalScrollBar().setValue(0)

    def scroll_to_bottom(self):
        """Scroll to the bottom of the content."""
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def scroll_to_widget(self, target: QWidget, x_margin: int = 0, y_margin: int = 0):
        """Ensure the specified target widget is visible within the viewport."""
        self.ensureWidgetVisible(target, x_margin, y_margin)
