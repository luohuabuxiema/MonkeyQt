# -*- coding: utf-8 -*-
"""ThemedUpload — themed drag/drop upload area."""

import os

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ..engine import ThemeEngine


class ThemedUpload(QWidget):
    """A themed upload drop area with a compact selected-file list."""

    filesSelected = Signal(list)
    fileRemoved = Signal(str)

    def __init__(self, parent=None, multiple=False, accept_filters=None, max_size_mb=50.0, tip_text=""):
        super().__init__(parent)
        self._multiple = multiple
        self._accept_filters = accept_filters or ["*.*"]
        self._max_size_mb = float(max_size_mb)
        self._tip_text = tip_text or f"支持任意文件，单文件不超过 {max_size_mb}MB"
        self._selected_files = []
        self._drag_active = False

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        self.drop_area = QFrame()
        self.drop_area.setObjectName("themedUploadDropArea")
        self.drop_area.setAcceptDrops(True)
        self.drop_area.installEventFilter(self)
        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setContentsMargins(18, 28, 18, 28)
        drop_layout.setSpacing(8)
        drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel("↑")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Segoe UI", 26, QFont.Weight.Bold)
        self.icon_label.setFont(font)
        self.main_label = QLabel("将文件拖拽到此处，或 点击上传")
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tip_label = QLabel(self._tip_text)
        self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(self.icon_label)
        drop_layout.addWidget(self.main_label)
        drop_layout.addWidget(self.tip_label)
        self.layout.addWidget(self.drop_area)

        self.file_list = QWidget()
        self.file_list_layout = QVBoxLayout(self.file_list)
        self.file_list_layout.setContentsMargins(0, 0, 0, 0)
        self.file_list_layout.setSpacing(6)
        self.file_list.setVisible(False)
        self.layout.addWidget(self.file_list)

        ThemeEngine.instance().themeChanged.connect(self.set_theme_style)
        self.set_theme_style()

    def eventFilter(self, obj, event):
        if obj == self.drop_area:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.trigger_file_dialog()
                return True
            if event.type() == QEvent.Type.DragEnter and event.mimeData().hasUrls():
                event.acceptProposedAction()
                self._drag_active = True
                self.set_theme_style()
                return True
            if event.type() == QEvent.Type.DragLeave:
                self._drag_active = False
                self.set_theme_style()
                return True
            if event.type() == QEvent.Type.Drop:
                self._drag_active = False
                files = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
                self.handle_files_selected(files)
                self.set_theme_style()
                event.acceptProposedAction()
                return True
        return super().eventFilter(obj, event)

    def trigger_file_dialog(self):
        filter_str = "Selected Files (" + " ".join(self._accept_filters) + ");;All Files (*.*)"
        if self._multiple:
            files, _ = QFileDialog.getOpenFileNames(self, "选择文件", "", filter_str)
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", filter_str)
            files = [file_path] if file_path else []
        if files:
            self.handle_files_selected(files)

    def handle_files_selected(self, files):
        valid = [path for path in files if path and os.path.exists(path)]
        if not valid:
            return
        self._selected_files = list(dict.fromkeys((self._selected_files if self._multiple else []) + valid))
        if not self._multiple:
            self._selected_files = self._selected_files[:1]
        self._rebuild_file_list()
        self.filesSelected.emit(list(self._selected_files))

    def _rebuild_file_list(self):
        while self.file_list_layout.count():
            item = self.file_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.file_list.setVisible(bool(self._selected_files))
        for path in self._selected_files:
            row = QFrame()
            row.setObjectName("themedUploadFileRow")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 7, 8, 7)
            row_layout.setSpacing(8)
            name = QLabel(os.path.basename(path))
            name.setObjectName("themedUploadFileName")
            remove = QPushButton("×")
            remove.setObjectName("themedUploadRemove")
            remove.setFixedSize(24, 24)
            remove.clicked.connect(lambda checked=False, file_path=path: self._remove_file(file_path))
            row_layout.addWidget(QLabel("□"))
            row_layout.addWidget(name, 1)
            row_layout.addWidget(remove)
            self.file_list_layout.addWidget(row)
        self.set_theme_style()

    def _remove_file(self, path):
        if path in self._selected_files:
            self._selected_files.remove(path)
            self._rebuild_file_list()
            self.fileRemoved.emit(path)

    def set_theme_style(self, style_name: str = None):
        t = ThemeEngine
        primary = t.get("--primary", "#409EFF")
        fg = t.get("--glass-text", t.get("--fg", "#1E293B")) if t.is_glass() else t.get("--fg", "#1E293B")
        muted = t.get("--text-muted", "#64748B")
        border = primary if self._drag_active else (t.get("--glass-border", t.get("--border", "#E2E8F0")) if t.is_glass() else t.get("--border", "#E2E8F0"))
        surface = t.get("--glass-surface", t.get("--surface-muted", "#F8FAFC")) if t.is_glass() else t.get("--surface-muted", "#F8FAFC")
        radius = "0px" if t.is_brutal() or t.is_pixel() else t.get("--radius", "8px")
        border_rule = "2px dashed #000000" if t.is_brutal() or t.is_pixel() else f"2px dashed {border}"
        row_border = "2px solid #000000" if t.is_brutal() or t.is_pixel() else f"1px solid {border}"
        self.setStyleSheet(f"""
            QFrame#themedUploadDropArea {{
                background: {surface};
                border: {border_rule};
                border-radius: {radius};
            }}
            QLabel {{
                background: transparent;
                color: {fg};
            }}
            QLabel#themedUploadFileName, QFrame#themedUploadFileRow QLabel {{
                color: {fg};
                font-size: 13px;
            }}
            QFrame#themedUploadFileRow {{
                background: {surface};
                border: {row_border};
                border-radius: {radius};
            }}
            QPushButton#themedUploadRemove {{
                background: transparent;
                border: none;
                color: {muted};
                font-size: 18px;
                font-weight: 800;
            }}
            QPushButton#themedUploadRemove:hover {{
                color: #EF4444;
            }}
        """)
        self.icon_label.setStyleSheet(f"color: {primary};")
        self.tip_label.setStyleSheet(f"color: {muted}; font-size: 12px;")
