"""
Qt Binding Compatibility Layer for monkeyqt-icons.
Supports PySide6, PyQt6, PySide2, and PyQt5 seamlessly.
"""

import sys

QT_LIB = None
QtCore = None
QtGui = None
QtWidgets = None
QtSvg = None
QtSvgWidgets = None

try:
    from PySide6 import QtCore, QtGui, QtWidgets, QtSvg
    try:
        from PySide6 import QtSvgWidgets
    except ImportError:
        QtSvgWidgets = None
    QT_LIB = "PySide6"
except ImportError:
    try:
        from PyQt6 import QtCore, QtGui, QtWidgets, QtSvg
        try:
            from PyQt6 import QtSvgWidgets
        except ImportError:
            QtSvgWidgets = None
        QT_LIB = "PyQt6"
    except ImportError:
        try:
            from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
            QtSvgWidgets = None
            QT_LIB = "PySide2"
        except ImportError:
            try:
                from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
                QtSvgWidgets = None
                QT_LIB = "PyQt5"
            except ImportError:
                raise ImportError(
                    "monkeyqt-icons requires PySide6, PyQt6, PySide2, or PyQt5. "
                    "Please install one of these Qt bindings."
                )

__all__ = [
    "QT_LIB",
    "QtCore",
    "QtGui",
    "QtWidgets",
    "QtSvg",
    "QtSvgWidgets"
]
