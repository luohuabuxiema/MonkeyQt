from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

from monkeyqt.themes.engine import ThemeEngine

class MkBreadcrumbItem(QPushButton):
    """面包屑节点，自适应当前主题"""
    def __init__(self, text, is_current=False, parent=None):
        super().__init__(text, parent)
        self.is_current = is_current
        self.setCursor(Qt.CursorShape.PointingHandCursor if not is_current else Qt.CursorShape.ArrowCursor)
        ThemeEngine.instance().themeChanged.connect(self._apply_style)
        self._apply_style()

    def _apply_style(self, theme_name: str = None):
        t = ThemeEngine
        is_dark = t.is_dark()
        fg = t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        hover_color = "#FFFFFF" if is_dark else "#0F172A"
        if t.is_glow() or t.is_brutal() or t.is_pixel():
            hover_color = t.get("--primary", "#409EFF")

        if self.is_current:
            self.setStyleSheet(f"""
                MkBreadcrumbItem {{
                    border: none;
                    background: transparent;
                    color: {fg};
                    font-size: 14px;
                    font-weight: 600;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                MkBreadcrumbItem {{
                    border: none;
                    background: transparent;
                    color: {muted};
                    font-size: 14px;
                    font-weight: 500;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
                }}
                MkBreadcrumbItem:hover {{
                    color: {hover_color};
                }}
            """)

from ..layout.widget import MkQWidget

class MkBreadcrumb(MkQWidget):
    """
    MkBreadcrumb 面包屑组件
    显示当前页面的路径，快速返回之前的任意页面。
    """
    itemClicked = Signal(str)

    def __init__(self, separator="/", parent=None):
        super().__init__(parent, layout="h", margins=0, spacing=8)
        self.separator_text = separator
        self.layout = self.inner_layout
        self.layout.addStretch() # 靠左对齐

        self._items_data = []

    def set_items(self, items: list):
        """
        批量设置面包屑项
        items 格式: [{"id": "home", "text": "首页"}, {"id": "user", "text": "用户管理"}]
        最后一个项会自动变为当前项。
        """
        # 清空之前的
        while self.layout.count() > 1: # 留下 stretch
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self._items_data = items
        total = len(items)

        for i, data in enumerate(items):
            is_current = (i == total - 1)
            
            # 添加节点按钮
            btn = MkBreadcrumbItem(data["text"], is_current=is_current)
            if not is_current:
                btn.clicked.connect(lambda checked=False, d=data: self.itemClicked.emit(d["id"]))
            self.layout.insertWidget(self.layout.count() - 1, btn)

            # 添加分隔符 (除了最后一个)
            if not is_current:
                sep_label = QLabel(self.separator_text)
                muted = ThemeEngine.get("--text-muted", "#64748B")
                sep_label.setStyleSheet(f"""
                    QLabel {{
                        color: {muted};
                        font-weight: 600;
                        font-size: 14px;
                        background: transparent;
                        border: none;
                    }}
                """)
                self.layout.insertWidget(self.layout.count() - 1, sep_label)
