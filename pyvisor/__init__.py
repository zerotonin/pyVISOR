"""pyVISOR — Desktop toolkit for manual ethology scoring.

This package provides a PyQt5-based GUI for annotating animal
behaviours in video recordings using gamepads or keyboards,
with built-in analysis and export capabilities.
"""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pyvisor")
except PackageNotFoundError:  # package not installed (e.g. running from a source checkout)
    __version__ = "0.1.0"

__all__ = ["__version__"]
