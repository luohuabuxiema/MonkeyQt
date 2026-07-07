import os
from PySide6.QtWidgets import QCheckBox, QWidget
from PySide6.QtCore import Property, Qt
from monkeyqt.common.enums import MkSize

_cur_dir = os.path.dirname(os.path.abspath(__file__))
_check_svg_path = os.path.join(_cur_dir, "check.svg")
if not os.path.exists(_check_svg_path):
    try:
        with open(_check_svg_path, "w", encoding="utf-8") as _f:
            _f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="none"/><polyline points="216 72 104 184 48 128" fill="none" stroke="white" stroke-linecap="round" stroke-linejoin="round" stroke-width="28"/></svg>')
    except Exception:
        pass
CHECK_SVG_URL = _check_svg_path.replace("\\", "/")


class MkCheckBox(QCheckBox):
    """
    MkCheckBox 组件
    对标 Element Plus 的 Checkbox，支持自定义尺寸和现代化的选中动画（通过 QSS）。
    """
    
    def __init__(self, text="", parent=None, size=MkSize.DEFAULT.value):
        # 兼容 Qt Designer
        if isinstance(text, QWidget):
            parent = text
            text = ""
            
        super().__init__(text, parent)
        
        self._mk_size = size
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._apply_style()
 
    def _apply_style(self):
        """注入 Element Plus 风格 of QSS 样式"""
        self.setStyleSheet("""
            /* 基础样式与文本颜色 */
            MkCheckBox {
                font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
                color: #606266;
                spacing: 8px; /* 框与文字的间距 */
                outline: none;
            }
            MkCheckBox:hover {
                color: #409eff;
            }
            MkCheckBox:disabled {
                color: #c0c4cc;
            }
 
            /* 自定义勾选框 (Indicator) */
            MkCheckBox::indicator {
                width: 14px;
                height: 14px;
                background-color: #ffffff;
                border: 1px solid #dcdfe6;
                border-radius: 2px;
                transition: border-color .25s cubic-bezier(.71,-.46,.29,1.46),background-color .25s cubic-bezier(.71,-.46,.29,1.46);
            }
 
            /* 悬浮时的框边框变蓝 */
            MkCheckBox::indicator:hover {
                border-color: #409eff;
            }
 
            /* 选中状态 */
            MkCheckBox::indicator:checked {
                background-color: #409eff;
                border-color: #409eff;
                image: url(__CHECK_SVG__);
            }
            
            /* 禁用状态 */
            MkCheckBox::indicator:disabled {
                background-color: #edf2fc;
                border-color: #dcdfe6;
            }
            MkCheckBox::indicator:checked:disabled {
                background-color: #a0cfff;
                border-color: #a0cfff;
            }

            /* --- 尺寸控制 --- */
            MkCheckBox[mk_size="large"] {
                font-size: 14px;
                height: 40px;
            }
            MkCheckBox[mk_size="large"]::indicator {
                width: 16px;
                height: 16px;
            }
            
            MkCheckBox[mk_size="default"] {
                font-size: 14px;
                height: 32px;
            }
            
            MkCheckBox[mk_size="small"] {
                font-size: 12px;
                height: 24px;
            }
            MkCheckBox[mk_size="small"]::indicator {
                width: 12px;
                height: 12px;
            }
        """.replace("__CHECK_SVG__", CHECK_SVG_URL))

    # --- 暴露属性 ---
    @Property(str)
    def mk_size(self):
        return self._mk_size

    @mk_size.setter
    def mk_size(self, value):
        if self._mk_size == value:
            return
        self._mk_size = value
        self.setProperty("mk_size", value)
        self.style().unpolish(self)
        self.style().polish(self)
