"""
MonkeyQt Icons Integration Subpackage.
Re-exports monkeyqt-icons for seamless access via `from monkeyqt.icons import Ph, PhHouse`.
"""

import sys
import pathlib

# Ensure local monkeyqt-icons folder is on sys.path if not installed via pip
ICONS_PKG_PATH = pathlib.Path(__file__).parent.parent / "monkeyqt-icons"
if ICONS_PKG_PATH.exists() and str(ICONS_PKG_PATH) not in sys.path:
    sys.path.insert(0, str(ICONS_PKG_PATH))

try:
    from monkeyqt_icons import *
except ImportError:
    raise ImportError("monkeyqt-icons package could not be found.")
