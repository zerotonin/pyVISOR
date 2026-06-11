"""Utilities for accessing packaged resource files."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Iterator, List


def _is_frozen() -> bool:
    """Return True if running inside a PyInstaller bundle."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def resource_path(*relative_parts: str) -> Path:
    """Return the filesystem path for a bundled resource.

    Works both in development (using importlib.resources) and when
    frozen by PyInstaller (using sys._MEIPASS).
    """
    if _is_frozen():
        base = Path(sys._MEIPASS) / "pyvisor" / "resources"
        result = base
        for part in relative_parts:
            result = result / part
        return result
    else:
        from importlib import resources
        traversable = resources.files(__name__)
        for part in relative_parts:
            traversable = traversable.joinpath(part)
        return Path(traversable)


def iter_resource_dirs(*relative_parts: str) -> Iterator[Path]:
    """Yield filesystem paths for sub-directories of a packaged resource."""
    base = resource_path(*relative_parts)
    for child in base.iterdir():
        if child.is_dir():
            yield child


def icon_categories() -> Iterable[Path]:
    """Return all available icon category directories."""
    categories: List[Path] = list(iter_resource_dirs("icons"))
    categories.sort(key=lambda path: path.name)
    return categories


def icons_root() -> Path:
    """Return the root directory for bundled icons."""
    return resource_path("icons")


def portable_icon_path(icon_path: str | None) -> str | None:
    """Convert an absolute bundled icon path to a relative one for portability."""
    if icon_path is None:
        return None
    try:
        return str(Path(icon_path).relative_to(icons_root()))
    except ValueError:
        return icon_path


def resolve_icon_path(icon_path: str | None) -> str | None:
    """Resolve a possibly-relative icon path back to an absolute one."""
    if icon_path is None:
        return None
    p = Path(icon_path)
    if not p.is_absolute():
        return str(icons_root() / p)
    if p.exists():
        return icon_path
    # Absolute path from another machine — look for an 'icons/' segment
    # and resolve the trailing part against the local icons root.
    parts = p.parts
    for i, part in enumerate(parts):
        if part == "icons" and i + 1 < len(parts):
            candidate = icons_root() / Path(*parts[i + 1:])
            if candidate.exists():
                return str(candidate)
    return icon_path
