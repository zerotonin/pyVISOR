"""Utility helpers for locating user-specific data directories.

This module centralizes the logic for determining where pyVISOR should
store user data such as cached icons, serialized GUI state, and autosave
artifacts.  It relies on :mod:`appdirs` so that the chosen locations
respect platform conventions (``~/Library`` on macOS, ``%APPDATA%`` on
Windows, etc.).
"""
from pathlib import Path

from appdirs import user_data_dir

_APP_NAME = "pyVISOR"
_APP_AUTHOR = "pyVISOR"


def _user_data_dir() -> Path:
    """Return the base directory for storing user-specific data."""
    return Path(user_data_dir(_APP_NAME, _APP_AUTHOR))


def ensure_user_data_dir() -> Path:
    """Ensure the user data directory exists and return it."""
    path = _user_data_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_tmp_icon_dir() -> Path:
    """Ensure and return the directory for cached, recoloured icons."""
    tmp_dir = ensure_user_data_dir() / "tmp_icons"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir


def ensure_autosave_dir() -> Path:
    """Ensure and return the directory for autosave data."""
    autosave_dir = ensure_user_data_dir() / "autosaves"
    autosave_dir.mkdir(parents=True, exist_ok=True)
    return autosave_dir


def settings_path(filename: str) -> Path:
    """Return the path for a settings file stored in the user data dir."""
    ensure_user_data_dir()
    return _user_data_dir() / filename


__all__ = [
    "ensure_autosave_dir",
    "ensure_tmp_icon_dir",
    "ensure_user_data_dir",
    "settings_path",
]
