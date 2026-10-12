"""Theme-aware vector skeletons driven by one clock for visible widgets."""
import time
import weakref
from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, QPoint, QRectF, QSize, QSizeF, QTimer, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QWidget,
)
from shiboken6 import isValid

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import qcolor


class _SkeletonClock(QObject):
    def __init__(self, app):
        super().__init__(app)
        self.widgets = weakref.WeakSet()
        self.started = time.monotonic()
        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self._tick)

    def add(self, widget):
        self.widgets.add(widget)
        if not self.timer.isActive():
            self.timer.start()

    def remove(self, widget):
        self.widgets.discard(widget)
        if not self.widgets:
            self.timer.stop()

    def _tick(self):
        for widget in list(self.widgets):
            if not isValid(widget) or not widget.isVisible():
                self.widgets.discard(widget)
            elif not widget.visibleRegion().isEmpty():
                widget._on_skeleton_frame(time.monotonic() - self.started)
        if not self.widgets:
            self.timer.stop()


def _skeleton_clock():
    app = QApplication.instance()
    clock = getattr(app, "_mk_skeleton_clock", None)
    if clock is None:
        app._mk_skeleton_clock = clock = _SkeletonClock(app)
    return clock


@dataclass(frozen=True)
class MkSkeletonBlock:
    """Integers are logical pixels; floats in [0, 1] are relative dimensions."""
    x: float = 0
    y: float = 0
    width: float = 1.0
    height: float = 20
    radius: float = 6
    shape: str = "rect"


class MkSkeleton(QWidget):
    """Composable rounded rectangles/circles; no bitmap scaling or child timers.

    ``blocks`` accepts MkSkeletonBlock objects or dictionaries.
    ``source_widget`` binds a real QWidget layout tree, auto-extracting blocks and
    tracking live resizes to eliminate layout shifts when switching states.
    """
    def __init__(self, blocks=None, parent=None, *, animated=True,
                 duration_ms=1200, base_color=None, highlight_color=None,
                 source_widget=None):
        super().__init__(parent)
        self._blocks = []
        self._animated = bool(animated)
        self._loading = True
        self._duration_ms = max(100, int(duration_ms))
        self._base_color = base_color
        self._highlight_color = highlight_color
        self._phase = 0.0
        self._source_widget = None
        self._source_filter_installed = False
        self.setProperty("mk_auto_loading", False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(40, 40)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        if source_widget is not None:
            self.bind_source(source_widget)
        elif blocks is not None:
            self.set_blocks(blocks)
        else:
            self.set_blocks(self._default_fallback_blocks())

        ThemeEngine.instance().themeChanged.connect(self._theme_changed)

    @staticmethod
    def _default_fallback_blocks():
        return [
            MkSkeletonBlock(16, 20, 0.4, 26),
            MkSkeletonBlock(16, 60, 0.7, 14),
            MkSkeletonBlock(16, 100, 0.9, 160, 12),
        ]

    @classmethod
    def from_widget(cls, widget: QWidget, parent=None, **kwargs) -> "MkSkeleton":
        """Factory method to create an auto-adapting skeleton from an existing QWidget."""
        return cls(blocks=None, parent=parent, source_widget=widget, **kwargs)

    @classmethod
    def preset_card_grid(cls, rows: int = 2, cols: int = 2, card_radius: float = 12,
                         has_title: bool = True, parent=None, **kwargs) -> "MkSkeleton":
        """Generates a responsive 2D card grid skeleton (matching dashboards and metrics)."""
        blocks = []
        top_offset = 0.0
        if has_title:
            blocks.append(MkSkeletonBlock(x=16, y=16, width=0.35, height=24, radius=6))
            top_offset = 0.12

        avail_h = 1.0 - top_offset - 0.04
        row_h = max(0.1, avail_h / max(1, rows))
        col_w = 0.96 / max(1, cols)

        for r in range(rows):
            for c in range(cols):
                bx = 0.02 + c * col_w + 0.01
                by = top_offset + r * row_h + 0.01
                bw = col_w - 0.02
                bh = row_h - 0.02
                blocks.append(MkSkeletonBlock(x=bx, y=by, width=bw, height=bh, radius=card_radius))
        return cls(blocks=blocks, parent=parent, **kwargs)

    @classmethod
    def preset_list(cls, rows: int = 5, item_height: float = 54, has_avatar: bool = True,
                    parent=None, **kwargs) -> "MkSkeleton":
        """Generates a list/table skeleton with optional avatar/circle icons."""
        blocks = [MkSkeletonBlock(x=16, y=16, width=0.4, height=22, radius=4)]
        y_start = 54.0
        for i in range(rows):
            curr_y = y_start + i * (item_height + 12.0)
            if has_avatar:
                blocks.append(MkSkeletonBlock(x=16, y=curr_y + (item_height - 36) / 2, width=36, height=36, shape="circle"))
                blocks.append(MkSkeletonBlock(x=64, y=curr_y + 8, width=0.4, height=16, radius=4))
                blocks.append(MkSkeletonBlock(x=64, y=curr_y + 30, width=0.7, height=12, radius=4))
            else:
                blocks.append(MkSkeletonBlock(x=16, y=curr_y, width=0.96, height=item_height, radius=8))
        return cls(blocks=blocks, parent=parent, **kwargs)

    @classmethod
    def preset_form(cls, fields: int = 4, parent=None, **kwargs) -> "MkSkeleton":
        """Generates a form/settings layout skeleton."""
        blocks = [MkSkeletonBlock(x=20, y=20, width=0.3, height=26, radius=4)]
        y = 66.0
        for _ in range(fields):
            blocks.append(MkSkeletonBlock(x=20, y=y, width=0.25, height=16, radius=4))
            blocks.append(MkSkeletonBlock(x=20, y=y + 24, width=0.94, height=36, radius=6))
            y += 74.0
        blocks.append(MkSkeletonBlock(x=20, y=y + 8, width=120, height=36, radius=6))
        return cls(blocks=blocks, parent=parent, **kwargs)

    def bind_source(self, widget: QWidget) -> None:
        """Bind a source widget to automatically infer skeleton blocks and track its layout."""
        if self._source_widget is not None and self._source_filter_installed:
            try:
                self._source_widget.removeEventFilter(self)
            except Exception:
                pass
            self._source_filter_installed = False

        self._source_widget = widget
        if widget is not None and isValid(widget):
            widget.installEventFilter(self)
            self._source_filter_installed = True
            self.sync_from_source()

    def unbind_source(self) -> None:
        """Unbind the currently tracked source widget."""
        if self._source_widget is not None and self._source_filter_installed:
            try:
                self._source_widget.removeEventFilter(self)
            except Exception:
                pass
            self._source_filter_installed = False
        self._source_widget = None

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._source_widget:
            if event.type() in (QEvent.Type.Resize, QEvent.Type.LayoutRequest):
                self.sync_from_source()
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._source_widget is not None:
            self.sync_from_source(event.size())

    def sync_from_source(self, target_size: QSize | None = None) -> list[MkSkeletonBlock]:
        """Inspects source_widget hierarchy, forces virtual layout pass if needed,
        and regenerates skeleton blocks to 100% match the real page geometry."""
        if self._source_widget is None or not isValid(self._source_widget):
            return self._blocks

        src = self._source_widget
        ref_size = target_size or self.size()

        if ref_size.width() > 10 and ref_size.height() > 10:
            if src.size() != ref_size:
                src.setGeometry(0, 0, ref_size.width(), ref_size.height())

        self._cascade_layout(src)
        blocks = self._extract_blocks_from_widget(src)
        if blocks:
            self.set_blocks(blocks)
        elif not self._blocks:
            self.set_blocks(self._default_fallback_blocks())
        return self._blocks

    @staticmethod
    def _cascade_layout(widget: QWidget) -> None:
        """Forces all descendant layouts in the widget tree to polish and compute geometries."""
        if not isValid(widget):
            return
        widget.ensurePolished()
        lay = widget.layout()
        if lay is not None:
            lay.setGeometry(widget.rect())
            lay.activate()

        for child in widget.findChildren(QWidget):
            if isValid(child):
                child.ensurePolished()
                c_lay = child.layout()
                if c_lay is not None:
                    c_lay.setGeometry(child.rect())
                    c_lay.activate()

    @staticmethod
    def _extract_blocks_from_widget(root: QWidget) -> list[MkSkeletonBlock]:
        """Extracts rounded rectangles and circles mirroring the real child widgets."""
        blocks = []
        if not isValid(root):
            return blocks

        for child in root.findChildren(QWidget):
            if not isValid(child):
                continue
            if child.property("mk_skeleton_ignore") is True:
                continue
            if child.isHidden() and not child.property("mk_skeleton_force_visible"):
                continue

            # Check if child is a container or leaf
            has_child_widgets = False
            for sub in child.findChildren(QWidget):
                if isValid(sub) and not sub.property("mk_skeleton_ignore") and not sub.isHidden():
                    has_child_widgets = True
                    break

            is_atomic_block = child.property("mk_skeleton_block") is True
            is_card_container = (
                child.property("mk_skeleton_card") is True or 
                child.__class__.__name__ in ("MkCard", "ThesisChartCard", "ThesisChartCanvas")
            )

            if has_child_widgets and not is_atomic_block:
                if is_card_container:
                    pos = child.mapTo(root, QPoint(0, 0))
                    w_w, w_h = child.width(), child.height()
                    if w_w > 4 and w_h > 4:
                        blocks.append(MkSkeletonBlock(
                            x=pos.x(), y=pos.y(), width=w_w, height=w_h,
                            radius=child.property("mk_skeleton_radius") or 10,
                            shape="rect"
                        ))
                continue

            pos = child.mapTo(root, QPoint(0, 0))
            w_w = child.width()
            w_h = child.height()

            if w_w <= 4 or w_h <= 4:
                continue

            shape = child.property("mk_skeleton_shape")
            if not shape:
                if child.__class__.__name__ in ("MkAvatar", "QRadioButton") or child.property("mk_avatar") is True:
                    shape = "circle"
                else:
                    shape = "rect"

            radius = child.property("mk_skeleton_radius")

            if isinstance(child, QLabel):
                fm = child.fontMetrics()
                font_h = fm.height()
                if w_h <= font_h * 2.5:
                    text_h = min(w_h, max(12.0, font_h + 2.0))
                    y_offset = (w_h - text_h) / 2.0
                    blocks.append(MkSkeletonBlock(
                        x=pos.x(), y=pos.y() + y_offset, width=w_w, height=text_h,
                        radius=radius or 4, shape="rect"
                    ))
                else:
                    blocks.append(MkSkeletonBlock(
                        x=pos.x(), y=pos.y(), width=w_w, height=w_h,
                        radius=radius or 6, shape="rect"
                    ))
            elif isinstance(child, (QPushButton, QLineEdit)):
                blocks.append(MkSkeletonBlock(
                    x=pos.x(), y=pos.y(), width=w_w, height=w_h,
                    radius=radius or 6, shape="rect"
                ))
            elif isinstance(child, (QTextEdit, QPlainTextEdit)):
                blocks.append(MkSkeletonBlock(
                    x=pos.x(), y=pos.y(), width=w_w, height=w_h,
                    radius=radius or 6, shape="rect"
                ))
            elif isinstance(child, QProgressBar):
                blocks.append(MkSkeletonBlock(
                    x=pos.x(), y=pos.y(), width=w_w, height=w_h,
                    radius=radius or (w_h / 2.0), shape="rect"
                ))
            else:
                blocks.append(MkSkeletonBlock(
                    x=pos.x(), y=pos.y(), width=w_w, height=w_h,
                    radius=radius or 8, shape=shape
                ))

        return blocks

    def set_blocks(self, blocks):
        parsed = [b if isinstance(b, MkSkeletonBlock) else MkSkeletonBlock(**b) for b in blocks]
        if any(b.shape not in ("rect", "circle") for b in parsed):
            raise ValueError("Skeleton shape must be 'rect' or 'circle'")
        self._blocks = parsed
        self.update()

    def add_block(self, **kwargs):
        block = MkSkeletonBlock(**kwargs)
        self.set_blocks(self._blocks + [block])
        return block

    def set_animated(self, animated):
        self._animated = bool(animated)
        self._sync_clock()
        self.update()

    def set_loading(self, loading=True):
        self._loading = bool(loading)
        self.setVisible(self._loading)
        self._sync_clock()

    def _sync_clock(self):
        clock = _skeleton_clock()
        if self._animated and self._loading and self.isVisible():
            clock.add(self)
        else:
            clock.remove(self)

    def _on_skeleton_frame(self, elapsed):
        self._phase = (elapsed * 1000 / self._duration_ms) % 1.0
        self.update()

    def _theme_changed(self, _name=None):
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        self._sync_clock()

    def hideEvent(self, event):
        _skeleton_clock().remove(self)
        super().hideEvent(event)

    def sizeHint(self):
        return QSize(480, 300)

    @staticmethod
    def _dimension(value, total):
        return value * total if isinstance(value, float) and 0 <= value <= 1 else value

    def paintEvent(self, event):
        surface = qcolor(ThemeEngine.get("--surface", "#FFFFFF"))
        fg = qcolor(ThemeEngine.get("--fg", "#1E293B"))
        base = qcolor(self._base_color) if self._base_color else QColor.fromRgbF(
            *(surface.getRgbF()[i] * .92 + fg.getRgbF()[i] * .08 for i in range(3)))
        highlight = qcolor(self._highlight_color) if self._highlight_color else QColor.fromRgbF(
            *(surface.getRgbF()[i] * .98 + fg.getRgbF()[i] * .02 for i in range(3)))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        for block in self._blocks:
            rect = QRectF(self._dimension(block.x, self.width()),
                          self._dimension(block.y, self.height()),
                          self._dimension(block.width, self.width()),
                          self._dimension(block.height, self.height()))
            if block.shape == "circle":
                side = min(rect.width(), rect.height())
                rect.setSize(QSizeF(side, side))
                path.addEllipse(rect)
            else:
                path.addRoundedRect(rect, block.radius, block.radius)
        painter.fillPath(path, base)
        if self._animated and self._loading:
            band = max(80.0, self.width() * .35)
            position = self._phase * (self.width() + band * 2) - band
            gradient = QLinearGradient(position - band, 0, position + band, 0)
            transparent = QColor(highlight)
            transparent.setAlpha(0)
            gradient.setColorAt(0, transparent)
            gradient.setColorAt(.5, highlight)
            gradient.setColorAt(1, transparent)
            painter.fillPath(path, gradient)
        painter.end()
