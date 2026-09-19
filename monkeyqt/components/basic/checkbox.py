import os
from PySide6.QtWidgets import QCheckBox, QWidget
from PySide6.QtCore import Property, Qt
from monkeyqt.common.enums import MkSize

from monkeyqt.themes.engine import ThemeEngine
from monkeyqt.themes.style_utils import readable_text

_cur_dir = os.path.dirname(os.path.abspath(__file__))
_check_light_svg_path = os.path.join(_cur_dir, "check.svg")
_check_dark_svg_path = os.path.join(_cur_dir, "check_dark.svg")

if not os.path.exists(_check_light_svg_path):
    try:
        with open(_check_light_svg_path, "w", encoding="utf-8") as _f:
            _f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="none"/><polyline points="216 72 104 184 48 128" fill="none" stroke="white" stroke-linecap="round" stroke-linejoin="round" stroke-width="28"/></svg>')
    except Exception:
        pass

if not os.path.exists(_check_dark_svg_path):
    try:
        with open(_check_dark_svg_path, "w", encoding="utf-8") as _f:
            _f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="none"/><polyline points="216 72 104 184 48 128" fill="none" stroke="#0F172A" stroke-linecap="round" stroke-linejoin="round" stroke-width="28"/></svg>')
    except Exception:
        pass

CHECK_LIGHT_SVG_URL = _check_light_svg_path.replace("\\", "/")
CHECK_DARK_SVG_URL = _check_dark_svg_path.replace("\\", "/")
CHECK_SVG_URL = CHECK_LIGHT_SVG_URL


class MkCheckBox(QCheckBox):
    """
    MkCheckBox 组件
    自适应 68 种主题风格的高清矢量复选框，完美融入现代暗色/亮色界面。
    """
    
    def __init__(self, text="", parent=None, size=MkSize.DEFAULT.value):
        # 兼容 Qt Designer
        if isinstance(text, QWidget):
            parent = text
            text = ""
            
        super().__init__(text, parent)
        
        self._mk_size = size
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        ThemeEngine.instance().themeChanged.connect(self._apply_style)
        self._apply_style()
 
    def _apply_style(self, theme_name: str = None):
        """注入主题自适应 QSS 样式"""
        t = ThemeEngine
        is_dark = t.is_dark()
        fg = t.get("--fg", "#1E293B")
        surface = t.get("--surface", "#FFFFFF")
        muted = t.get("--text-muted", "#94A3B8")
        primary = t.get("--primary", "#409EFF")

        if is_dark:
            # 暗黑主题下，复选框未选中边框增强对比度（避免在深黑/OLED背景下发虚看不清）
            border = "rgba(255, 255, 255, 0.52)" if not t.is_brutal() else "#FFFFFF"
            hover_border = "rgba(255, 255, 255, 0.88)" if not t.is_brutal() else primary
            indicator_bg = "transparent" if surface in ("#000000", "#09090B", "#121212") else surface
        else:
            border = t.get("--border", "#CBD5E1")
            hover_border = primary
            indicator_bg = surface

        checked_bg = primary
        checked_border = primary
        hover_text = primary
        svg_url = CHECK_LIGHT_SVG_URL if readable_text(primary) == "#FFFFFF" else CHECK_DARK_SVG_URL

        disabled_bg = t.get("--surface-muted", "#EDF2FC")

        self.setStyleSheet(f"""
            /* 基础样式与文本颜色 */
            MkCheckBox {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
                color: {fg};
                spacing: 8px; /* 框与文字的间距 */
                outline: none;
            }}
            MkCheckBox:hover {{
                color: {hover_text};
            }}
            MkCheckBox:disabled {{
                color: {muted};
            }}
 
            /* 自定义勾选框 (Indicator) */
            MkCheckBox::indicator {{
                width: 16px;
                height: 16px;
                background-color: {indicator_bg};
                border: 1px solid {border};
                border-radius: 4px;
            }}
 
            /* 悬浮时的框边框 */
            MkCheckBox::indicator:hover {{
                border-color: {hover_border};
            }}
 
            /* 选中状态 */
            MkCheckBox::indicator:checked {{
                background-color: {checked_bg};
                border-color: {checked_border};
                image: url({svg_url});
            }}
            
            /* 禁用状态 */
            MkCheckBox::indicator:disabled {{
                background-color: {disabled_bg};
                border-color: {border};
            }}

            /* --- 尺寸控制 --- */
            MkCheckBox[mk_size="large"] {{
                font-size: 15px;
                height: 40px;
            }}
            MkCheckBox[mk_size="large"]::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }}
            
            MkCheckBox[mk_size="default"] {{
                font-size: 13px;
                height: 32px;
            }}
            MkCheckBox[mk_size="default"]::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 4px;
            }}
            
            MkCheckBox[mk_size="small"] {{
                font-size: 12px;
                height: 24px;
            }}
            MkCheckBox[mk_size="small"]::indicator {{
                width: 14px;
                height: 14px;
                border-radius: 3px;
            }}
        """)

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
