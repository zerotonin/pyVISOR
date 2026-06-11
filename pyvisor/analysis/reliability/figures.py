# ╔══════════════════════════════════════════════════════════════════╗
# ║  GameThogram — reliability.figures                               ║
# ║  « rainclouds and Bland–Altman, the lab way »                    ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Validation figures in the house style: Wong palette, raincloud  ║
# ║  over bar chart, SVG + PNG + CSV via save_figure.                ║
# ╚══════════════════════════════════════════════════════════════════╝
"""Validation figures.  Import matplotlib lazily so the stats core
stays importable on headless machines without a display backend.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from pyvisor.analysis.reliability.agreement import BlandAltman
from pyvisor.analysis.reliability.viz_constants import WONG, save_figure


def plot_kappa_raincloud(per_behaviour: pd.DataFrame, output_dir: Path, stem: str = "kappa_raincloud") -> None:
    """Raincloud of per-clip κ for each behaviour (half-violin + strip + box)."""
    import matplotlib.pyplot as plt

    behaviours = sorted(per_behaviour["behaviour"].unique())
    fig, ax = plt.subplots(figsize=(7, 0.7 * len(behaviours) + 1.5))
    rng = np.random.default_rng(0)

    for i, behav in enumerate(behaviours):
        values = per_behaviour.loc[per_behaviour["behaviour"] == behav, "kappa"].dropna().to_numpy()
        if values.size == 0:
            continue
        if values.size > 1 and np.ptp(values) > 0:
            kde = _gaussian_kde(values)
            grid = np.linspace(values.min(), values.max(), 100)
            density = kde(grid)
            density = 0.4 * density / density.max()
            ax.fill_between(grid, i + 0.05, i + 0.05 + density, color=WONG["sky_blue"], alpha=0.6, lw=0)
        jitter = i - 0.18 + rng.uniform(-0.06, 0.06, size=values.size)
        ax.scatter(values, jitter, s=14, color=WONG["blue"], alpha=0.7, zorder=3)
        ax.boxplot(
            values, positions=[i - 0.32], vert=False, widths=0.12,
            patch_artist=True, manage_ticks=False,
            boxprops=dict(facecolor="white", color=WONG["black"]),
            medianprops=dict(color=WONG["vermilion"]),
            flierprops=dict(marker="", markersize=0),
        )

    ax.axvline(0.8, color=WONG["bluish_green"], ls="--", lw=1, label="κ = 0.8 (almost perfect)")
    ax.set_yticks(range(len(behaviours)))
    ax.set_yticklabels(behaviours)
    ax.set_xlabel("Cohen's κ (per clip)")
    ax.set_xlim(-0.1, 1.0)
    ax.legend(loc="lower left", fontsize=8, frameon=False)
    fig.tight_layout()
    save_figure(fig, stem, output_dir, data=per_behaviour)
    plt.close(fig)


def plot_bland_altman(
    ci_table: pd.DataFrame, stats: BlandAltman, output_dir: Path, stem: str = "bland_altman_ci"
) -> None:
    """Bland–Altman plot of the Courtship Index (pass A vs pass B)."""
    import matplotlib.pyplot as plt

    mean = (ci_table["ci_a"] + ci_table["ci_b"]) / 2
    diff = ci_table["ci_a"] - ci_table["ci_b"]

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(mean, diff, s=28, color=WONG["blue"], alpha=0.8, zorder=3)
    ax.axhline(stats.bias, color=WONG["vermilion"], lw=1.5, label=f"bias = {stats.bias:.3f}")
    ax.axhline(stats.loa_upper, color=WONG["black"], ls="--", lw=1, label="95 % limits of agreement")
    ax.axhline(stats.loa_lower, color=WONG["black"], ls="--", lw=1)
    ax.set_xlabel("Mean Courtship Index of the two passes")
    ax.set_ylabel("Difference (A − B)")
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    fig.tight_layout()
    out = ci_table.assign(mean_ci=mean, diff_ci=diff)
    save_figure(fig, stem, output_dir, data=out)
    plt.close(fig)


def _gaussian_kde(values: np.ndarray):
    """Thin wrapper so the import cost lands only when a KDE is needed."""
    from scipy.stats import gaussian_kde

    return gaussian_kde(values)
