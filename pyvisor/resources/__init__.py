"""Utilities for accessing packaged resource files."""
from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Iterable, Iterator, List


def _traversable(*relative_parts: str):
    traversable = resources.files(__name__)
    for part in relative_parts:
        traversable = traversable.joinpath(part)
    return traversable


def resource_path(*relative_parts: str) -> Path:
    """Return the filesystem path for a bundled resource."""
    traversable = _traversable(*relative_parts)
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
