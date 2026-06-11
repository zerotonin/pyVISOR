# ╔══════════════════════════════════════════════════════════════════╗
# ║  GameThogram — reliability.viz_constants                         ║
# ║  « Wong palette and the triple-output saver »                    ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Wong (2011) colourblind-safe palette and save_figure (SVG +     ║
# ║  PNG + CSV) for every validation figure.                         ║
# ╚══════════════════════════════════════════════════════════════════╝
"""Shared figure conventions for the validation analysis."""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import pandas as pd
from matplotlib.figure import Figure

# ┌────────────────────────────────────────────────────────────┐
# │ Wong (2011) palette  « colourblind-safe base colours »     │
# └────────────────────────────────────────────────────────────┘
WONG: dict[str, str] = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermilion": "#D55E00",
    "reddish_purple": "#CC79A7",
}

FIGURE_DPI: int = 200

# Keep SVG text editable in Inkscape rather than baked into paths.
mpl.rcParams["svg.fonttype"] = "none"


def save_figure(
    fig: Figure,
    stem: str,
    output_dir: Path,
    data: pd.DataFrame | None = None,
) -> None:
    """Export a figure as SVG + PNG, plus an optional CSV data companion.

    Args:
        fig:        Matplotlib figure to save.
        stem:       Filename stem (no extension).
        output_dir: Target directory (created if needed).
        data:       Tidy table behind the figure, written as ``stem.csv``.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{stem}.svg")
    fig.savefig(output_dir / f"{stem}.png", dpi=FIGURE_DPI)
    if data is not None:
        data.to_csv(output_dir / f"{stem}.csv", index=False, encoding="utf-8")
