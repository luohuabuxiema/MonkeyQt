from monkeyqt.themes.engine import ThemeEngine as _MkThemeEngine
from PySide6.QtCore import Qt, Property, QRectF, QTimer, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import draw_liquid_glass, parse_px, qcolor


class MkCard(QFrame):
    """
    MkCard 组件 - 风格化卡片容器，完美自适应 68 种内置主题风格。
    
    特性：
        1. 主题自适应：全自动适配 68 套主题规范（毛玻璃、新拟态、极简风等）；
        2. 原生流光骨架屏（Skeleton Shimmer）：
           调用 card.set_loading(True) 或初始化 MkCard(loading=True)，
           整张卡片将自动呈现科技感极强的流光骨架占位；加载完成后 set_loading(False) 平滑展现真实数据。
    
    用法:
        card = MkCard(title="Settings", parent=self)
        card_layout = card.content_layout  # 在此添加子组件
        card.set_loading(True)             # 开启流光骨架屏
    """

    def __init__(self, title="", show_title=True, loading=False, parent=None):
        from PySide6.QtWidgets import QWidget
        if isinstance(title, QWidget):
            parent = title
            title = ""
            show_title = True
        elif isinstance(show_title, QWidget):
            parent = show_title
            show_title = True
        elif isinstance(loading, QWidget):
            parent = loading
            loading = False

        super().__init__(parent)
        self._title = title
        self._show_title = show_title
        self._hovered = False
        self._time_angle = 0.0
        self._loading = bool(loading)
        self._shimmer_progress = 0.0
        self._shimmer_timer = None
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumSize(200, 120)

        # 内部布局
        self._layout = QVBoxLayout(self)
        if show_title:
            self._layout.setContentsMargins(20, 16, 20, 16)
        else:
            self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8 if show_title else 0)

        # 标题
        self._title_label = QLabel(title)
        self._title_label.setObjectName("MkCardTitle")
        _MkThemeEngine.apply_style_sheet(self._title_label, "background: transparent;")
        font = QFont("Segoe UI", 13, QFont.Weight.DemiBold)
        self._title_label.setFont(font)
        self._layout.addWidget(self._title_label)
        self._title_label.setVisible(bool(title) and show_title)

        # 内容区域（用户可往此添加子组件）
        self._content_widget = QFrame()
        _MkThemeEngine.apply_style_sheet(self._content_widget, "background: transparent; border: none;")
        self.content_layout = QVBoxLayout(self._content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(6)
        self._layout.addWidget(self._content_widget)

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)

        if self._loading:
            self._content_widget.setVisible(False)
            self._title_label.setVisible(False)
            self._shimmer_timer = QTimer(self)
            self._shimmer_timer.setInterval(30)
            self._shimmer_timer.timeout.connect(self._on_shimmer_step)
            self._shimmer_timer.start()

    @property
    def content_widget(self) -> QFrame:
        return self._content_widget

    def _update_style(self):
        t = ThemeEngine

        # 如果是流态玻璃，启动动画定时器以触发重绘
        if t.is_liquid_glass():
            if not hasattr(self, "_liquid_timer"):
                from PySide6.QtCore import QTimer
                self._liquid_timer = QTimer(self)
                self._liquid_timer.timeout.connect(self._on_liquid_timeout)
            if not self._liquid_timer.isActive():
                self._liquid_timer.start(33)  # 30 fps
        else:
            if hasattr(self, "_liquid_timer") and self._liquid_timer.isActive():
                self._liquid_timer.stop()

        fg = t.get("--fg", "#1E293B")

        # 标题颜色
        if t.is_dark():
            _MkThemeEngine.apply_style_sheet(self._title_label, f"background: transparent; color: #FFFFFF;")
        elif t.is_brutal():
            _MkThemeEngine.apply_style_sheet(self._title_label, f"background: transparent; color: #000000; font-weight: 900;")
        else:
            _MkThemeEngine.apply_style_sheet(self._title_label, f"background: transparent; color: {fg};")

        if not self.styleSheet():
            _MkThemeEngine.apply_style_sheet(self, "QFrame { background: transparent; border: none; }")
        self.update()

    def paintEvent(self, event):
        t = ThemeEngine
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        primary = t.get("--primary", "#409EFF")
        bg = t.get("--bg", "#FFFFFF")
        r_str = t.get("--radius", "6px")
        radius = parse_px(r_str, 6, 0, 36)

        if t.is_neumorphic():
            inset = rect.adjusted(6, 6, -6, -6)
            # 凸起效果
            painter.setPen(Qt.PenStyle.NoPen)
            # 暗阴影
            painter.setBrush(QBrush(QColor(0, 0, 0, 25)))
            painter.drawRoundedRect(inset.translated(4, 4), radius, radius)
            # 亮阴影
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.drawRoundedRect(inset.translated(-3, -3), radius, radius)
            # 主体
            bg_color = QColor(bg) if bg.startswith("#") else QColor("#E8E8E8")
            painter.setBrush(QBrush(bg_color))
            painter.drawRoundedRect(inset, radius, radius)

        elif t.is_glass():
            inset = rect.adjusted(3, 3, -3, -3)
            if t.is_liquid_glass():
                angle = getattr(self, "_time_angle", 0.0)
                draw_liquid_glass(
                    painter,
                    inset,
                    max(radius, 18),
                    primary,
                    dark=t.is_dark(),
                    hovered=self._hovered,
                    angle=angle,
                    intensity=1.2,
                )
            else:
                # 毛玻璃
                if t.is_dark():
                    glass = QColor(255, 255, 255, 20)
                else:
                    glass = QColor(255, 255, 255, 50)
                if self._show_title:
                    painter.setPen(QPen(qcolor(t.get("--glass-border", "rgba(255, 255, 255, 100)")), 1))
                else:
                    painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(glass))
                painter.drawRoundedRect(inset, radius, radius)
                # 顶部高光线
                if self._show_title:
                    painter.setPen(QPen(QColor(255, 255, 255, 60), 1))
                    painter.drawLine(inset.left() + radius, inset.top(),
                                   inset.right() - radius, inset.top())

        elif t.is_brutal():
            inset = rect.adjusted(4, 4, -8, -8)
            if self._show_title:
                # 硬偏移阴影
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor("#000000")))
                painter.drawRect(inset.translated(4, 4))
                # 白色主体
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                painter.setPen(QPen(QColor("#000000"), 2))
                painter.drawRect(inset)
            else:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                painter.drawRect(inset)

        elif t.is_glow():
            inset = rect.adjusted(2, 2, -2, -2)
            # 主体
            card_bg = qcolor(t.get("--surface", "#1B2525")) if t.is_dark() else QColor(bg)
            painter.setBrush(QBrush(card_bg))
            if self._show_title:
                border_color = qcolor(t.get("--border", primary))
                painter.setPen(QPen(border_color, 1))
            else:
                painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(inset, radius, radius)

        elif t.is_pixel():
            inset = rect.adjusted(3, 3, -6, -6)
            if self._show_title:
                # 像素阴影
                pixel = 3
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor("#000000")))
                for x in range(inset.left() + pixel, inset.right() + pixel, pixel):
                    painter.drawRect(x, inset.bottom(), pixel, pixel)
                for y in range(inset.top() + pixel, inset.bottom() + pixel, pixel):
                    painter.drawRect(inset.right(), y, pixel, pixel)
                # 主体
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                painter.setPen(QPen(QColor("#000000"), 2))
                painter.drawRect(inset)
            else:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                painter.drawRect(inset)
        else:
            inset = rect.adjusted(1, 1, -1, -1)
            bg = t.get("--bg", "#FFFFFF")
            border = t.get("--border", "#E2E8F0")
            border_w = t.get("--border-width", "1px")
            bw = parse_px(border_w, 1, 0, 8)
            card_bg = t.get("--surface", bg if not t.is_dark() else t._lighten_hex(bg, 0.06))

            painter.setBrush(QBrush(qcolor(card_bg)))
            if self._show_title and bw > 0:
                border_color = qcolor(t.get('--input-hover-border', border) if self._hovered else border)
                painter.setPen(QPen(border_color, bw))
            else:
                painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(inset, radius, radius)

        # 若处于骨架屏加载态，绘制整卡流光骨架（参考图一/图三 Web 质感）
        if self._loading:
            self._draw_skeleton_shimmer(painter, rect, t)

        painter.end()

    def _draw_skeleton_shimmer(self, painter: QPainter, rect, t):
        is_dark = t.is_dark()
        # 柔和底色与高光色
        base_color = QColor(36, 36, 42) if is_dark else QColor(241, 245, 249)
        highlight_color = QColor(54, 54, 64, 200) if is_dark else QColor(255, 255, 255, 230)

        # 内部边距
        pad_x = 20 if self._show_title else 16
        pad_y = 16 if self._show_title else 14
        content_w = max(10.0, float(rect.width() - pad_x * 2))
        content_h = max(10.0, float(rect.height() - pad_y * 2))

        if hasattr(self, "_get_skeleton_blocks") and callable(getattr(self, "_get_skeleton_blocks")):
            blocks = self._get_skeleton_blocks(rect, content_w, content_h, pad_x, pad_y)
        else:
            blocks = []
            if content_h <= 110.0:
                # 类似图一顶部的 3 个 KPI 指标卡 (标题条 + 大数值骨架块)
                blocks.append(QRectF(float(pad_x), float(pad_y + 4), min(100.0, content_w * 0.45), 14.0))
                blocks.append(QRectF(float(pad_x), float(pad_y + 30), min(80.0, content_w * 0.35), 26.0))
            elif content_h <= 200.0:
                # 中等卡片 (如 GPU 状态卡)
                blocks.append(QRectF(float(pad_x), float(pad_y + 4), min(160.0, content_w * 0.4), 16.0))
                blocks.append(QRectF(float(pad_x), float(pad_y + 32), content_w * 0.85, 14.0))
                blocks.append(QRectF(float(pad_x), float(pad_y + 54), content_w * 0.55, 14.0))
            else:
                # 大容器卡片：顶部标题 + 多行雅致流光条纹，杜绝粗笨大色块
                blocks.append(QRectF(float(pad_x), float(pad_y + 4), min(180.0, content_w * 0.35), 16.0))
                blocks.append(QRectF(float(pad_x), float(pad_y + 26), min(130.0, content_w * 0.25), 12.0))
                curr_y = pad_y + 52.0
                max_y = float(rect.height()) - float(pad_y) - 16.0
                while curr_y + 16.0 <= max_y and len(blocks) < 8:
                    ratio = 0.90 if len(blocks) % 3 == 0 else (0.75 if len(blocks) % 3 == 1 else 0.55)
                    blocks.append(QRectF(float(pad_x), float(curr_y), content_w * ratio, 18.0))
                    curr_y += 30.0

        painter.setPen(Qt.PenStyle.NoPen)

        # 流光扫描位移
        sweep_x = float(rect.left()) + float(rect.width() + 200) * self._shimmer_progress - 100.0
        gradient_width = max(120.0, float(rect.width()) * 0.45)

        for block in blocks:
            rad = 6.0 if block.height() > 20.0 else 4.0
            grad = QLinearGradient(sweep_x - gradient_width, 0, sweep_x + gradient_width, 0)
            grad.setColorAt(0.0, base_color)
            grad.setColorAt(0.5, highlight_color)
            grad.setColorAt(1.0, base_color)

            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(block, rad, rad)

    @Property(bool)
    def loading(self) -> bool:
        return self._loading

    @loading.setter
    def loading(self, val: bool):
        self.set_loading(val)

    def set_loading(self, loading: bool = True):
        """设置卡片骨架屏加载态。开启后自动隐藏内容并播放流光扫光，关闭后平滑恢复内容。"""
        if self._loading == loading:
            return
        self._loading = bool(loading)
        if self._loading:
            self._content_widget.setVisible(False)
            self._title_label.setVisible(False)
            if not hasattr(self, "_shimmer_timer") or self._shimmer_timer is None:
                self._shimmer_timer = QTimer(self)
                self._shimmer_timer.setInterval(30)
                self._shimmer_timer.timeout.connect(self._on_shimmer_step)
            if not self._shimmer_timer.isActive() and self.isVisible():
                self._shimmer_timer.start()
        else:
            if hasattr(self, "_shimmer_timer") and self._shimmer_timer and self._shimmer_timer.isActive():
                self._shimmer_timer.stop()
            self._content_widget.setVisible(True)
            self._title_label.setVisible(bool(self._title) and self._show_title)
            self._content_widget.updateGeometry()
            self.updateGeometry()
            if self.parentWidget() and self.parentWidget().layout():
                self.parentWidget().layout().invalidate()
                self.parentWidget().layout().activate()
        self.update()

    def sizeHint(self) -> QSize:
        if hasattr(self, "_content_widget") and self._content_widget:
            cw_hint = self._content_widget.sizeHint()
            if cw_hint.isValid() and cw_hint.height() > 0:
                pad_y = 32 if self._show_title else 0
                title_h = self._title_label.sizeHint().height() + 8 if (bool(self._title) and self._show_title) else 0
                return QSize(max(200, cw_hint.width()), max(120, cw_hint.height() + title_h + pad_y))
        return super().sizeHint()

    def _on_shimmer_step(self):
        if not self.isVisible() or not self._loading:
            return
        self._shimmer_progress += 0.03
        if self._shimmer_progress >= 1.0:
            self._shimmer_progress = 0.0
        self.update()

    def hideEvent(self, event):
        if hasattr(self, "_shimmer_timer") and self._shimmer_timer and self._shimmer_timer.isActive():
            self._shimmer_timer.stop()
        super().hideEvent(event)

    def showEvent(self, event):
        if getattr(self, "_loading", False):
            if hasattr(self, "_shimmer_timer") and self._shimmer_timer and not self._shimmer_timer.isActive():
                self._shimmer_timer.start()
        super().showEvent(event)

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def _on_liquid_timeout(self):
        import math
        self._time_angle += 0.04
        if self._time_angle >= 2 * math.pi:
            self._time_angle -= 2 * math.pi
        self.update()

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        if t.is_liquid_glass():
            if not hasattr(self, "_liquid_timer"):
                from PySide6.QtCore import QTimer
                self._liquid_timer = QTimer(self)
                self._liquid_timer.timeout.connect(self._on_liquid_timeout)
            if not self._liquid_timer.isActive():
                self._liquid_timer.start(33)
        else:
            if hasattr(self, "_liquid_timer") and self._liquid_timer.isActive():
                self._liquid_timer.stop()
        self.update()

    @Property(str)
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self._title_label.setText(value)
        self._title_label.setVisible(bool(value) and self._show_title)

    @Property(bool)
    def show_title(self):
        return self._show_title

    @show_title.setter
    def show_title(self, value):
        self._show_title = bool(value)
        self._title_label.setVisible(bool(self._title) and self._show_title)
        if self._show_title:
            self._layout.setContentsMargins(20, 16, 20, 16)
            self._layout.setSpacing(8)
        else:
            self._layout.setContentsMargins(0, 0, 0, 0)
            self._layout.setSpacing(0)
        self._update_style()
        self.update()
