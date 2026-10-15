"""Theme-aware action menus with configurable triggers and high-DPI icons."""
from __future__ import annotations

import time

from PySide6.QtCore import QPoint, QRect, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QAction, QColor, QFontMetrics, QIcon, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QApplication, QMenu, QProxyStyle, QPushButton, QStyle
from monkeyqt_icons import Ph

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import parse_px, qcolor, readable_text


def _has_icon(icon):
    return icon is not None and (not isinstance(icon, QIcon) or not icon.isNull()) and icon != ""


def _icon_spec(icon):
    # QVariant copies QIcon values; keep Ph metadata before that copy happens.
    spec = getattr(icon, "_ph_spec", None)
    return dict(spec) if spec else icon


def _paint_icon(painter, rect, icon, color, widget, weight="regular"):
    """Render Phosphor SVGs at the destination window's actual device ratio."""
    if not _has_icon(icon):
        return
    spec = getattr(icon, "_ph_spec", None)
    if isinstance(icon, (str, dict)) or spec or hasattr(icon, "name"):
        spec = dict(spec or (icon if isinstance(icon, dict) else {"name": getattr(icon, "name", icon)}))
        spec["size"] = rect.width()
        spec.setdefault("weight", weight)
        if spec.get("color") in (None, "auto", "default", "fg", "foreground", "currentColor", "currentcolor"):
            spec["color"] = color
        spec["dpr"] = widget.devicePixelRatioF()
        painter.drawPixmap(rect.topLeft(), Ph.pixmap(**spec))
    elif isinstance(icon, QIcon):
        icon.paint(painter, rect, Qt.AlignmentFlag.AlignCenter,
                   QIcon.Mode.Normal if widget.isEnabled() else QIcon.Mode.Disabled)
    else:
        raise TypeError("icon must be a Phosphor name, icon class, options dict or QIcon")


class _MenuStyle(QProxyStyle):
    def styleHint(self, hint, option=None, widget=None, return_data=None):
        if hint == QStyle.StyleHint.SH_Menu_Scrollable:
            return 1
        return super().styleHint(hint, option, widget, return_data)

    def pixelMetric(self, metric, option=None, widget=None):
        result = super().pixelMetric(metric, option, widget)
        if metric == QStyle.PixelMetric.PM_MenuScrollerHeight and hasattr(widget, "owner"):
            result += getattr(widget.owner, "_shadow_margin", 0)
        return result


class _DropdownMenu(QMenu):
    """Keep QAction semantics and native navigation; customize presentation."""

    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self._menu_style = _MenuStyle(QApplication.style().objectName() or "Fusion")
        self._menu_style.setParent(self)
        self.setStyle(self._menu_style)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setSeparatorsCollapsible(False)
        self.aboutToShow.connect(owner.update_theme_style)

    def actionEvent(self, event):
        super().actionEvent(event)
        if getattr(self.owner, "_colors", None):
            self.setFixedWidth(self.sizeHint().width())
            self.update()

    def sizeHint(self):
        hint = super().sizeHint()
        o = self.owner
        fm = self.fontMetrics()
        prefix = any(_has_icon(a.property("mk_prefix")) or not a.icon().isNull() for a in self.actions())
        width = 0
        for action in self.actions():
            if not action.isVisible() or action.isSeparator():
                continue
            label, _, shortcut = action.text().partition("\t")
            shortcut = shortcut or action.shortcut().toString()
            content = fm.horizontalAdvance(label.replace("&", ""))
            if not action.property("mk_label"):
                content += (o.icon_size + o.icon_gap) if prefix else 0
                content += (o.icon_size + o.icon_gap) if _has_icon(action.property("mk_suffix")) else 0
                content += (o.icon_size + o.icon_gap) if action.isCheckable() or action.menu() else 0
                content += fm.horizontalAdvance(shortcut) + 24 if shortcut else 0
            width = max(width, content)
        width += 2 * (o.menu_padding + o.item_padding + o._shadow_margin)
        width = o.menu_width or max(o.min_menu_width, width)
        if o.max_menu_width:
            width = min(width, o.max_menu_width)
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            width = min(width, screen.availableGeometry().width())
        return QSize(width, hint.height())

    def _keep_open(self, action):
        if not action or not action.isEnabled() or action.isSeparator() or action.menu():
            return False
        close = action.property("mk_close_on_click")
        return not (bool(close) if close is not None else not action.isCheckable())

    def mouseReleaseEvent(self, event):
        action = self.actionAt(event.position().toPoint())
        if event.button() == Qt.MouseButton.LeftButton and self._keep_open(action):
            action.trigger()
            self.update()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        action = self.activeAction()
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._keep_open(action):
                action.trigger()
                self.update()
                event.accept()
                return
            if event.key() == Qt.Key.Key_Space and action and action.isEnabled() and not action.menu() and not action.isSeparator():
                self.hide()
                action.trigger()
                event.accept()
                return
        super().keyPressEvent(event)

    def paintEvent(self, event):
        o, c = self.owner, self.owner._colors
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        margin = o._shadow_margin
        card = QRectF(self.rect()).adjusted(margin + .5, margin + .5, -margin - .5, -margin - .5)
        if margin:
            for spread in range(margin, 0, -1):
                shadow = QColor(c["shadow"])
                shadow.setAlpha(int((9 if ThemeEngine.is_dark() else 5) * (1 - spread / (margin + 1))))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(shadow)
                painter.drawRoundedRect(card.adjusted(-spread, -spread / 2, spread, spread),
                                        o._radius + spread, o._radius + spread)
        painter.setBrush(c["surface"])
        painter.setPen(QPen(c["border"], o._border_width))
        painter.drawRoundedRect(card, o._radius, o._radius)
        clip = QPainterPath()
        clip.addRoundedRect(card.adjusted(1, 1, -1, -1), o._radius, o._radius)
        painter.setClipPath(clip)
        actions = [a for a in self.actions() if a.isVisible()]
        # Align icons within a group; icon-free metric groups stay flush left.
        prefix_columns = {}
        group = []
        for action in actions + [None]:
            if action is None or action.isSeparator() or action.property("mk_label"):
                has_prefix = any(_has_icon(a.property("mk_prefix")) or not a.icon().isNull() for a in group)
                prefix_columns.update((a, has_prefix) for a in group)
                group = []
            else:
                group.append(action)
        for action in actions:
            row = self.actionGeometry(action)
            if row.isEmpty() or not row.intersects(self.rect()):
                continue
            if action.isSeparator():
                painter.setPen(QPen(c["border"], o.separator_width))
                painter.drawLine(row.left() + o.separator_inset, row.center().y(),
                                 row.right() - o.separator_inset, row.center().y())
                continue
            is_label = bool(action.property("mk_label"))
            active = action == self.activeAction() and action.isEnabled() and not is_label
            if active:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(c["hover"])
                painter.drawRoundedRect(QRectF(row).adjusted(0, 1, 0, -1), max(0, o._radius - 3), max(0, o._radius - 3))
            color = c["muted"] if is_label or not action.isEnabled() else c["danger"] if action.property("mk_danger") else c["fg"]
            font = self.font()
            if is_label:
                font.setPixelSize(max(10, o.font_size - 1))
                font.setBold(True)
            painter.setFont(font)
            painter.setPen(color)
            left, right = row.left() + o.item_padding, row.right() - o.item_padding
            iy = row.center().y() - o.icon_size // 2
            if not is_label:
                prefix = action.property("mk_prefix")
                if not _has_icon(prefix):
                    prefix = action.icon()
                if prefix_columns.get(action, False):
                    _paint_icon(painter, QRect(left, iy, o.icon_size, o.icon_size), prefix, color, self, o.icon_weight)
                    left += o.icon_size + o.icon_gap
                if action.isCheckable() or action.menu():
                    if action.isChecked() or action.menu():
                        icon = o.check_icon if action.isCheckable() else "caret-right"
                        _paint_icon(painter, QRect(right - o.icon_size, iy, o.icon_size, o.icon_size), icon, color, self, o.icon_weight)
                    right -= o.icon_size + o.icon_gap
                suffix = action.property("mk_suffix")
                if _has_icon(suffix):
                    _paint_icon(painter, QRect(right - o.icon_size, iy, o.icon_size, o.icon_size), suffix, color, self, o.icon_weight)
                    right -= o.icon_size + o.icon_gap
            label, _, shortcut = action.text().partition("\t")
            shortcut = shortcut or action.shortcut().toString()
            if shortcut and not is_label:
                sw = self.fontMetrics().horizontalAdvance(shortcut)
                painter.setPen(c["muted"])
                painter.drawText(QRect(right - sw, row.top(), sw, row.height()), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, shortcut)
                right -= sw + 24
            painter.setPen(color)
            label = label.replace("&&", "\0").replace("&", "").replace("\0", "&")
            label = QFontMetrics(font).elidedText(label, Qt.TextElideMode.ElideRight, max(0, right - left))
            painter.drawText(QRect(left, row.top(), max(0, right - left), row.height()), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, label)
        if actions:
            # Native QMenu performs scrolling and hit testing for these bands.
            scroller = self.style().pixelMetric(QStyle.PixelMetric.PM_MenuScrollerHeight, None, self)
            for scroll_up, hidden in ((True, self.actionGeometry(actions[0]).top() < margin),
                                      (False, self.actionGeometry(actions[-1]).bottom() > self.height() - margin)):
                if hidden:
                    band_y = 0 if scroll_up else self.height() - scroller
                    painter.fillRect(QRect(0, band_y, self.width(), scroller), c["surface"])
                    icon_y = (margin + scroller - 12) // 2 if scroll_up else self.height() - (margin + scroller + 12) // 2
                    _paint_icon(painter, QRect((self.width() - 12) // 2, icon_y, 12, 12),
                                "caret-up" if scroll_up else "caret-down", c["fg"], self)


class MkDropdown(QPushButton):
    """Multifunction dropdown retaining the original add_item / QAction API.

    Icons accept monkeyqt-icons names, Ph icon classes, option dictionaries, or
    QIcon objects. Phosphor SVGs render at the current window's device ratio.
    trigger: button, more, more-vertical, icon, text, split.
    variant: default, primary, outline, ghost, text.
    Checkable items stay open; regular actions close, unless configured otherwise.
    Geometry uses logical pixels. None radius follows the active theme tokens.
    """

    itemClicked = Signal(str)
    itemToggled = Signal(str, bool)
    checkedChanged = Signal(list)
    aboutToShow = Signal()
    aboutToHide = Signal()

    def __init__(self, text="Dropdown", parent=None, *, trigger="button", variant="default",
                 icon=None, suffix_icon=None, show_arrow=True, size="default",
                 icon_size=18, icon_weight="regular", icon_gap=8, menu_width=None,
                 min_menu_width=180, max_menu_width=None, placement="bottom-start",
                 offset=6, row_height=36, font_size=13, menu_padding=5,
                 item_padding=12, radius=None, shadow=True, separator_width=1,
                 separator_spacing=9, separator_inset=0, check_icon="check"):
        super().__init__(text, parent)
        if trigger not in ("button", "more", "more-vertical", "icon", "text", "split"):
            raise ValueError("Unknown dropdown trigger: " + trigger)
        if variant not in ("default", "primary", "outline", "ghost", "text"):
            raise ValueError("Unknown dropdown variant: " + variant)
        if size not in ("small", "default", "large"):
            raise ValueError("size must be small, default or large")
        if placement not in ("bottom-start", "bottom-end", "top-start", "top-end"):
            raise ValueError("placement must be bottom-start, bottom-end, top-start or top-end")
        self.trigger, self.variant, self.size_variant = trigger, variant, size
        self.prefix_icon, self.suffix_icon = icon, suffix_icon
        self.show_arrow = bool(show_arrow) or trigger == "split"
        self.icon_size, self.icon_gap = max(8, int(icon_size)), max(0, int(icon_gap))
        self.icon_weight = icon_weight
        self.menu_width = max(40, int(menu_width)) if menu_width is not None else None
        self.min_menu_width = max(40, int(min_menu_width))
        self.max_menu_width = max(40, int(max_menu_width)) if max_menu_width is not None else None
        self.placement, self.offset = placement, max(0, int(offset))
        self.row_height, self.font_size = max(20, int(row_height)), max(10, int(font_size))
        self.menu_padding, self.item_padding = max(0, int(menu_padding)), max(0, int(item_padding))
        self.radius, self.shadow = radius, bool(shadow)
        self.separator_width = max(1, int(separator_width))
        self.separator_spacing = max(self.separator_width, int(separator_spacing))
        self.separator_inset, self.check_icon = max(0, int(separator_inset)), check_icon
        self._colors = {}
        self._last_close_time = 0
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName(text if trigger not in ("more", "more-vertical", "icon") else "更多操作" if text == "Dropdown" else text)
        self.menu = _DropdownMenu(self)
        self.menu.aboutToShow.connect(self.aboutToShow)
        self.menu.aboutToHide.connect(self._on_menu_hidden)
        self.clicked.connect(self._on_clicked)
        ThemeEngine.instance().themeChanged.connect(self.update_theme_style)
        self.update_theme_style()

    def update_theme_style(self, style_name=None):
        t = ThemeEngine
        self._radius = max(0, int(self.radius)) if self.radius is not None else parse_px(t.get("--radius", "8px"), 8, 0, 32)
        self._border_width = parse_px(t.get("--border-width", "1px"), 1, 1, 5)
        self._shadow_margin = 10 if self.shadow and not (t.is_brutal() or t.is_pixel()) else 0
        self._colors = {
            "surface": qcolor(t.get("--surface"), "#FFFFFF"),
            "fg": qcolor(t.get("--fg"), "#1E293B"),
            "muted": qcolor(t.get("--text-muted"), "#64748B"),
            "border": qcolor(t.get("--border"), "#E2E8F0"),
            "hover": qcolor(t.get("--surface-muted"), "#F1F5F9"),
            "primary": qcolor(t.get("--primary"), "#171717"),
            "danger": qcolor(t.get("--danger"), "#F87171" if t.is_dark() else "#DC2626"),
            "shadow": qcolor(t.get("--primary"), "#000000") if t.is_glow() else QColor("#000000"),
        }
        font = self.font()
        font.setPixelSize(self.font_size)
        self.setFont(font)
        self.menu.setFont(font)
        effective_height = max(self.row_height, self.menu.fontMetrics().height() + 8, self.icon_size + 8)
        vertical_padding = max(0, (effective_height - self.menu.fontMetrics().height()) // 2)
        padding = self.menu_padding + self._shadow_margin
        ThemeEngine.apply_style_sheet(self.menu, f"""
            QMenu {{ background: transparent; border: none; padding: {padding}px; }}
            QMenu::item {{ padding: {vertical_padding}px {self.item_padding}px;
                           min-height: {effective_height - 2 * vertical_padding}px; }}
            QMenu::separator {{ height: {self.separator_spacing}px; margin: 0; }}
            QMenu::indicator {{ width: 0; height: 0; }}
        """)
        ThemeEngine.apply_style_sheet(self, "QPushButton { background: transparent; border: none; padding: 0; }")
        self.setMinimumHeight({"small": 28, "default": 36, "large": 44}[self.size_variant])
        self.updateGeometry()
        self.update()
        self.menu.updateGeometry()
        self.menu.setFixedWidth(self.menu.sizeHint().width())
        self.menu.update()

    def _on_clicked(self):
        if self.trigger != "split" and time.monotonic() - self._last_close_time >= .15:
            self.show_menu()

    def _on_menu_hidden(self):
        self._last_close_time = time.monotonic()
        self.update()
        self.aboutToHide.emit()

    def _button_icons(self):
        if self.trigger in ("more", "more-vertical"):
            return self.prefix_icon or ("dots-three" if self.trigger == "more" else "dots-three-vertical"), None, False
        return self.prefix_icon if _has_icon(self.prefix_icon) else self.icon(), self.suffix_icon, self.show_arrow and self.trigger != "icon"

    def sizeHint(self):
        height = max({"small": 28, "default": 36, "large": 44}[self.size_variant], self.fontMetrics().height() + 14, self.icon_size + 12)
        if self.trigger in ("more", "more-vertical", "icon"):
            return QSize(height, height)
        prefix, suffix, arrow = self._button_icons()
        width = self.fontMetrics().horizontalAdvance(self.text().replace("&", "")) + 28
        width += (self.icon_size + self.icon_gap) * (int(_has_icon(prefix)) + int(_has_icon(suffix)) + int(arrow))
        return QSize(width + (8 if self.trigger == "split" else 0), height)

    def minimumSizeHint(self):
        return self.sizeHint()

    def paintEvent(self, event):
        c = self._colors
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(.5, .5, -.5, -.5)
        hover = self.underMouse() or self.menu.isVisible()
        variant = "text" if self.trigger == "text" else "ghost" if self.trigger in ("more", "more-vertical") and self.variant == "default" else self.variant
        bg = c["primary"] if variant == "primary" else c["surface"]
        fg = qcolor(readable_text(bg.name())) if variant == "primary" else c["fg"]
        if variant in ("ghost", "text"):
            bg = c["hover"] if hover else QColor(Qt.GlobalColor.transparent)
        elif hover:
            bg = bg.lighter(115) if variant == "primary" else c["hover"]
        if self.isDown():
            bg = bg.darker(108)
        if not self.isEnabled():
            painter.setOpacity(.45)
        painter.setBrush(bg)
        painter.setPen(QPen(c["border"], self._border_width) if variant in ("default", "outline") else Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, self._radius, self._radius)
        prefix, suffix, arrow = self._button_icons()
        text = "" if self.trigger in ("more", "more-vertical", "icon") else self.text().replace("&", "")
        content_width = self.fontMetrics().horizontalAdvance(text)
        pieces = int(_has_icon(prefix)) + int(_has_icon(suffix)) + int(arrow)
        content_width += pieces * self.icon_size + max(0, pieces + bool(text) - 1) * self.icon_gap
        x = (self.width() - content_width) // 2
        y = (self.height() - self.icon_size) // 2
        if _has_icon(prefix):
            _paint_icon(painter, QRect(x, y, self.icon_size, self.icon_size), prefix, fg, self, self.icon_weight)
            x += self.icon_size + self.icon_gap
        if text:
            tw = self.fontMetrics().horizontalAdvance(text)
            painter.setFont(self.font())
            painter.setPen(fg)
            painter.drawText(QRect(x, 0, tw, self.height()), Qt.AlignmentFlag.AlignCenter, text)
            x += tw + self.icon_gap
        if _has_icon(suffix):
            _paint_icon(painter, QRect(x, y, self.icon_size, self.icon_size), suffix, fg, self, self.icon_weight)
            x += self.icon_size + self.icon_gap
        if arrow:
            _paint_icon(painter, QRect(x, y, self.icon_size, self.icon_size), "caret-up" if self.menu.isVisible() else "caret-down", fg, self, self.icon_weight)
        if self.trigger == "split":
            painter.setPen(QPen(c["border"], 1))
            painter.drawLine(self.width() - self.icon_size - 18, 7, self.width() - self.icon_size - 18, self.height() - 7)
        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(c["primary"], 2, Qt.PenStyle.DotLine))
            painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), max(0, self._radius - 2), max(0, self._radius - 2))

    def mousePressEvent(self, event):
        if self.trigger == "split" and event.button() == Qt.MouseButton.LeftButton and event.position().x() >= self.width() - self.icon_size - 18:
            self.show_menu()
            event.accept()
            return
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Down:
            self.show_menu()
            first = next((a for a in self.menu.actions() if a.isVisible() and a.isEnabled() and not a.isSeparator()), None)
            self.menu.setActiveAction(first)
            event.accept()
            return
        super().keyPressEvent(event)

    def show_menu(self):
        """Open at the configured anchor, flipping and clamping to the screen."""
        if not self.isEnabled() or not any(a.isVisible() for a in self.menu.actions()):
            return
        if self.menu.isVisible():
            self.hide_menu()
            return
        self.update_theme_style()
        screen = self.screen() or QApplication.primaryScreen()
        area = screen.availableGeometry()
        self.menu.ensurePolished()
        hint = self.menu.sizeHint()
        height, width = min(hint.height(), area.height()), hint.width()
        origin = self.mapToGlobal(QPoint(0, 0))
        m = self._shadow_margin
        x = origin.x() - m if self.placement.endswith("start") else origin.x() + self.width() - width + m
        below = origin.y() + self.height() + self.offset - m
        above = origin.y() - height - self.offset + m
        y = above if self.placement.startswith("top") else below
        if y + height > area.bottom() + 1 and above >= area.top():
            y = above
        elif y < area.top() and below + height <= area.bottom() + 1:
            y = below
        x = max(area.left(), min(x, area.right() + 1 - width))
        y = max(area.top(), min(y, area.bottom() + 1 - height))
        self.menu.popup(QPoint(x, y))
        self.update()

    def showMenu(self):
        self.show_menu()

    def hide_menu(self):
        self.menu.hide()

    def add_item(self, text, item_id="", *, icon=None, suffix_icon=None, enabled=True,
                 checkable=False, checked=False, close_on_click=None, callback=None,
                 shortcut=None, danger=False):
        """Append and return a QAction. callback takes no arguments.

        close_on_click=None closes regular items and keeps check items open.
        """
        item_id = str(item_id or text)
        action = QAction(text, self.menu)
        action.setData(item_id)
        action.setEnabled(enabled)
        action.setCheckable(checkable or checked)
        action.setChecked(checked)
        action.setProperty("mk_prefix", _icon_spec(icon))
        action.setProperty("mk_suffix", _icon_spec(suffix_icon))
        action.setProperty("mk_close_on_click", close_on_click)
        action.setProperty("mk_danger", bool(danger))
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(lambda _checked=False, aid=item_id: self.itemClicked.emit(aid))
        action.toggled.connect(lambda state, aid=item_id: self._on_toggled(aid, state))
        if callback is not None:
            action.triggered.connect(lambda _checked=False: callback())
        self.menu.addAction(action)
        return action

    def add_check_item(self, text, item_id="", checked=False, **kwargs):
        return self.add_item(text, item_id, checkable=True, checked=checked, **kwargs)

    def add_label(self, text):
        action = QAction(text, self.menu)
        action.setEnabled(False)
        action.setProperty("mk_label", True)
        self.menu.addAction(action)
        return action

    def add_separator(self):
        """Append a separator anywhere, including consecutive separators."""
        return self.menu.addSeparator()

    def get_item(self, item_id):
        return next((a for a in self.menu.actions() if not a.isSeparator() and not a.property("mk_label") and a.data() == item_id), None)

    def set_item_icons(self, item_id, icon=None, suffix_icon=None):
        action = self.get_item(item_id)
        if action is None:
            raise KeyError(item_id)
        action.setProperty("mk_prefix", _icon_spec(icon))
        action.setProperty("mk_suffix", _icon_spec(suffix_icon))
        self.update_theme_style()

    def set_item_checked(self, item_id, checked):
        action = self.get_item(item_id)
        if action is None:
            raise KeyError(item_id)
        if not action.isCheckable():
            raise ValueError("Item is not checkable: " + str(item_id))
        action.setChecked(bool(checked))

    def is_item_checked(self, item_id):
        action = self.get_item(item_id)
        return bool(action and action.isChecked())

    def checked_ids(self):
        return [a.data() for a in self.menu.actions() if a.isCheckable() and a.isChecked()]

    def set_all_checked(self, checked):
        for action in self.menu.actions():
            if action.isCheckable():
                action.setChecked(bool(checked))

    def clear(self):
        self.menu.clear()
        self.checkedChanged.emit([])

    def _on_toggled(self, item_id, checked):
        self.itemToggled.emit(item_id, checked)
        self.checkedChanged.emit(self.checked_ids())
        self.menu.update()
