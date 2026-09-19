"""
monkeyqt-icons: High-Performance Phosphor Icons for PySide6 / PyQt5 / PyQt6.
1-to-1 port of @phosphor-icons/core v2.1.1.
"""

from .qt_compat import QT_LIB
from .core import PhosphorEngine, PhosphorIconBase, PhFactory, Ph
from .widget import PhIconWidget
from .icons import *

__version__ = "2.1.2"

__all__ = [
    "QT_LIB",
    "PhosphorEngine",
    "PhosphorIconBase",
    "PhFactory",
    "Ph",
    "PhIconWidget",
    *icons.__all__
]
