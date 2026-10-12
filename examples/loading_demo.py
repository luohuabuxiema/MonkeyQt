"""Run: python examples/loading_demo.py. The delay simulates I/O only."""
import argparse
import math
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QPointF, QTimer, Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QApplication, QGridLayout, QHBoxLayout, QLabel, QStackedWidget, QVBoxLayout, QWidget
from monkeyqt import (MkButton, MkCard, MkMenu, MkPageLoader, MkQWidget,
                      MkSelectCard, MkSkeleton, ThemeEngine)


class CurvePreview(QWidget):
    """Small vector chart for the demo; no plotting backend is required."""
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.values = []
        self.setMinimumSize(100, 130)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = self.rect().adjusted(10, 12, -10, -20)
        painter.setPen(QPen(QColor(ThemeEngine.get("--border", "#E2E8F0")), 1))
        for step in range(5):
            y = area.top() + step * area.height() / 4
            painter.drawLine(QPointF(area.left(), y), QPointF(area.right(), y))
        path = QPainterPath()
        for i, value in enumerate(self.values):
            point = QPointF(area.left() + i * area.width() / max(1, len(self.values) - 1),
                            area.bottom() - value * area.height())
            if i:
                path.lineTo(point)
            else:
                path.moveTo(point)
        painter.setPen(QPen(QColor(self.color), 2))
        painter.drawPath(path)
        painter.end()


def fetch_project(name, mode, delay, *, cancel_event):
    # Real applications replace this with I/O using thread-safe connections.
    # Do not add an artificial delay to production data loading.
    cancel_event.wait(delay)
    if mode == "error":
        raise OSError("演示：数据服务暂时不可用，可点击重试或刷新")
    if mode == "empty":
        return []
    return [dict(id=i, title=f"{name} · Model {i + 1}", subtitle=f"{40 + i * 7}.1%  ·  {5 + i} MB",
                 dot_color=["#3478F6", "#17A398", "#9868E8"][i % 3], checked=i == 0)
            for i in range(4)]


class LoadingDemo(MkQWidget):
    def __init__(self, delay=.9):
        super().__init__(layout="h", margins=0, spacing=0, role="bg")
        self.delay = delay
        self.setWindowTitle("MonkeyQt · 页面加载与快速导航")
        self.resize(1140, 740)
        self.sidebar = MkMenu()
        self.sidebar.setFixedWidth(190)
        self.sidebar.add_item("A", "Example Project")
        self.sidebar.add_item("B", "Vigorous Whale")
        self.layout().addWidget(self.sidebar)
        main = MkQWidget(layout="v", margins=24, spacing=16)
        self.layout().addWidget(main, 1)
        heading = QLabel("项目概览")
        heading.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        main.layout().addWidget(heading)
        toolbar = QHBoxLayout()
        self.refresh_button = MkButton("刷新", btn_type="primary")
        self.empty_button = MkButton("空数据")
        self.fail_button = MkButton("模拟失败")
        self.fast_button = MkButton("即时数据")
        self.theme_button = MkButton("切换明暗")
        for button in (self.refresh_button, self.empty_button, self.fail_button, self.fast_button, self.theme_button):
            toolbar.addWidget(button)
        toolbar.addStretch()
        main.layout().addLayout(toolbar)
        self.info = QLabel("可在加载过程中切换项目；再次进入会保留已有页面。")
        self.info.setWordWrap(True)
        main.layout().addWidget(self.info)
        self.stack = QStackedWidget()
        main.layout().addWidget(self.stack, 1)
        self.pages, self.rows, self.plots = {}, {}, {}
        for name in ("A", "B"):
            content = MkQWidget(layout="v", margins=0, spacing=14)
            title = QLabel("Example Project" if name == "A" else "Vigorous Whale")
            title.setFont(QFont("Segoe UI", 15, QFont.Weight.DemiBold))
            content.layout().addWidget(title)
            body = QHBoxLayout()
            body.setSpacing(16)
            rows = MkSelectCard(title="Models", badge_pattern="{count} 已选")
            rows.setFixedWidth(210)
            body.addWidget(rows)
            grid = QGridLayout()
            grid.setSpacing(14)
            plots = []
            for i, metric in enumerate(("precision(B)", "recall(B)", "mAP50-95(B)", "Training Loss")):
                card = MkCard(metric)
                plot = CurvePreview("#3478F6" if name == "A" else "#17A398")
                card.content_layout.addWidget(plot)
                grid.addWidget(card, i // 2, i % 2)
                plots.append(plot)
            body.addLayout(grid, 1)
            content.layout().addLayout(body, 1)
            # Match the title, model list and 2x2 charts of this page.
            blocks = [dict(x=0, y=4, width=.38, height=25)]
            blocks.extend(dict(x=0, y=62 + i * 66, width=210, height=54, radius=10) for i in range(5))
            for row in range(2):
                for column in range(2):
                    blocks.append(dict(x=.28 + column * .36, y=.12 + row * .43,
                                       width=.34, height=.40, radius=12))
            skeleton = MkSkeleton(blocks)
            page = MkPageLoader(content, skeleton, loading_delay_ms=120)
            self.pages[name], self.rows[name], self.plots[name] = page, rows, plots
            self.stack.addWidget(page)
        self.current = "A"
        self.sidebar.itemClicked.connect(self.navigate)
        self.refresh_button.clicked.connect(lambda: self.reload("ready"))
        self.empty_button.clicked.connect(lambda: self.reload("empty"))
        self.fail_button.clicked.connect(lambda: self.reload("error"))
        self.fast_button.clicked.connect(lambda: self.reload("ready", delay=0))
        self.theme_button.clicked.connect(self.toggle_theme)
        self.sidebar.set_active("A", emit=False)
        self._beats = 0
        self.heartbeat = QTimer(self)
        self.heartbeat.setInterval(100)
        self.heartbeat.timeout.connect(self._heartbeat)
        self.heartbeat.start()
        QTimer.singleShot(0, lambda: self.navigate("A"))

    def navigate(self, name):
        self.current = name
        page = self.pages[name]
        self.stack.setCurrentWidget(page)  # Show the target shell first.
        self.sidebar.set_active(name, emit=False)
        if page.state == "idle":
            self.reload("ready")

    def reload(self, mode, delay=None):
        name = self.current
        started = time.perf_counter()

        def apply(rows):
            self.rows[name].set_items(rows)
            for index, plot in enumerate(self.plots[name]):
                plot.values = [.15 + .60 * (1 - math.exp(-i / (8 + index * 4)))
                               + .015 * math.sin(i * .7 + index) for i in range(80)] if rows else []
                plot.update()
            if name == self.current:
                self.info.setText(f"项目 {name} 已更新 · {round((time.perf_counter() - started) * 1000)} ms（含模拟 I/O）")

        task = self.pages[name].load(fetch_project, name, mode,
                                     self.delay if delay is None else delay,
                                     on_success=apply, pass_cancel_event=True)
        if mode == "ready":
            self.refresh_button.bind_task(task, "刷新中…")
        return task

    def toggle_theme(self):
        ThemeEngine.set_theme("Elegant Light" if ThemeEngine.is_dark() else "Dark Mode (OLED)")

    def _heartbeat(self):
        self._beats += 1
        self.setWindowTitle(f"MonkeyQt · 页面加载与快速导航 · UI heartbeat {self._beats}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="Automatically navigate, refresh and exit")
    parser.add_argument("--capture-dir", type=Path, help="Save light/dark loading and content previews")
    args = parser.parse_args()
    app = QApplication.instance() or QApplication([])
    # The offscreen plugin may not discover Windows system fonts automatically.
    for name in ("segoeui.ttf", "msyh.ttc"):
        font = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / name
        if font.is_file():
            QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont("Segoe UI", 10))
    ThemeEngine.enable_palette_theme()
    ThemeEngine.set_theme("Elegant Light")
    demo = LoadingDemo(delay=.35 if args.smoke else .9)
    demo.show()
    if args.capture_dir:
        args.capture_dir.mkdir(parents=True, exist_ok=True)

        def capture(name):
            demo.grab().save(str(args.capture_dir / name))

        QTimer.singleShot(220, lambda: capture("loading-light.png"))
        QTimer.singleShot(600 if args.smoke else 1200, lambda: capture("content-light.png"))
        QTimer.singleShot(700 if args.smoke else 1400, demo.toggle_theme)
        QTimer.singleShot(800 if args.smoke else 1550, lambda: demo.navigate("B"))
        QTimer.singleShot(1000 if args.smoke else 1800, lambda: capture("loading-dark.png"))
        QTimer.singleShot(1300 if args.smoke else 2600, lambda: capture("content-dark.png"))
    if args.smoke:
        QTimer.singleShot(1450, lambda: demo.reload("empty", delay=0))
        QTimer.singleShot(1550, lambda: demo.reload("error", delay=0))
        QTimer.singleShot(1650, lambda: demo.reload("ready", delay=0))
        QTimer.singleShot(1800, lambda: print("demo", demo.pages[demo.current].state,
                                           "heartbeat", demo._beats, flush=True))
        QTimer.singleShot(1900, demo.close)
    app.exec()


if __name__ == "__main__":
    main()
