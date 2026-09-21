# -*- coding: utf-8 -*-
"""
@File : page.py
@Desc : Modern web-style responsive, auto-scrollable full-page container for MonkeyQt.
"""
from typing import Optional, Union, Sequence
from PySide6.QtWidgets import QWidget, QLayout
from monkeyqt.components.layout.widget import MkQWidget


class MkPage(MkQWidget):
    """
    MkPage - 现代 Web 风格自适应全屏长页面脚手架容器。

    主要特性：
    1. 【开箱即用整页自然滚动】：
       内置极简现代胶囊滚动条（7px 细条，无原生箭头，支持暗黑/亮色主题自适应），
       默认滚动条贴紧窗口最右侧边缘，无多余内缩留白；
    2. 【智能子组件感知】：
       向页面添加 MkProTable / MkDataTable 等数据表格时，自动激活表格的 auto_height
       自适应展开模式，使表格 100% 融入整页文档流，彻底告别局部小视口截断与嵌套滚动条；
    3. 【平滑滚动与便民接口】：
       提供 scroll_to_top()、scroll_to_bottom()、scroll_to_widget() 等接口，
       在多 Tab 切换时自动平滑置顶；
    4. 【与 MkWindow 智能防重协同】：
       嵌入 MkWindow 时自动通知外层主窗口跳过二次滚动包装，保证全局永远只有唯一一根最右侧大滚动条。
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        layout: Optional[Union[str, QLayout]] = "v",
        margins: Optional[Union[int, Sequence[int]]] = (24, 20, 24, 20),
        spacing: Optional[int] = 16,
        role: str = "transparent",
        scroll_direction: str = "v",
        **kwargs
    ):
        super().__init__(
            parent=parent,
            layout=layout,
            margins=margins,
            spacing=spacing,
            role=role,
            scrollable=True,
            scroll_direction=scroll_direction,
            **kwargs
        )
        self.setObjectName("MkPage")
