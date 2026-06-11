# ╔══════════════════════════════════════════════════════════════════╗
# ║  GameThogram — reliability.report                                ║
# ║  « two annotation sets in, tidy tables + figures out »           ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Orchestrates the validation analysis: per-clip per-behaviour    ║
# ║  agreement, study-level ICC and Bland–Altman on the Courtship    ║
# ║  Index, and the matching figures.  Decision logic stays out — it ║
# ║  computes every statistic and leaves interpretation to the paper. ║
# ╚══════════════════════════════════════════════════════════════════╝
"""Study-level orchestration of the agreement statistics.

Every statistic is computed unconditionally for every clip; thresholds
and verdicts belong in the manuscript, not here.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from pyvisor.analysis.reliability import agreement as ag
from pyvisor.analysis.reliability import measures as me
from pyvisor.analysis.reliability.annotation_io import RasterAnnotation, align


@dataclass(frozen=True)
class ClipComparison:
    """One clip scored by two passes (observers, or GameThogram vs BORIS)."""

    clip_id: str
    pass_a: RasterAnnotation
    pass_b: RasterAnnotation
    courtship_behaviours: list[str]


# ┌────────────────────────────────────────────────────────────┐
# │ Per-clip, per-behaviour agreement                          │
# └────────────────────────────────────────────────────────────┘


def behaviour_agreement(comparison: ClipComparison) -> pd.DataFrame:
    """Per-behaviour κ, %-agreement and F1 for a single clip."""
    a, b = align(comparison.pass_a, comparison.pass_b)
    rows = []
    for behav in a.behaviours:
        va, vb = a.column(behav), b.column(behav)
        pr = ag.precision_recall_f1(va, vb)
        rows.append(
            {
                "clip_id": comparison.clip_id,
                "behaviour": behav,
                "kappa": ag.cohen_kappa_binary(va, vb),
                "percent_agreement": ag.percent_agreement(va, vb),
                "precision": pr.precision,
                "recall": pr.recall,
                "f1": pr.f1,
                "prevalence_a": float(np.mean(va)),
                "prevalence_b": float(np.mean(vb)),
            }
        )
    return pd.DataFrame(rows)


def courtship_index_pair(comparison: ClipComparison) -> dict[str, float]:
    """Courtship Index from each pass for one clip."""
    a, b = align(comparison.pass_a, comparison.pass_b)
    cols_a = [a.behaviours.index(c) for c in comparison.courtship_behaviours if c in a.behaviours]
    return {
        "clip_id": comparison.clip_id,
        "ci_a": me.courtship_index(a.matrix(), cols_a),
        "ci_b": me.courtship_index(b.matrix(), cols_a),
    }


# ┌────────────────────────────────────────────────────────────┐
# │ Study-level summary                                         │
# └────────────────────────────────────────────────────────────┘


@dataclass(frozen=True)
class StudySummary:
    per_behaviour: pd.DataFrame  # one row per clip × behaviour
    courtship_index: pd.DataFrame  # one row per clip (ci_a, ci_b)
    icc_courtship_index: float
    bland_altman_courtship_index: ag.BlandAltman


def summarise_study(comparisons: list[ClipComparison]) -> StudySummary:
    """Run the full battery over every clip and pool the scalar readouts."""
    if not comparisons:
        raise ValueError("no clip comparisons supplied")

    per_behaviour = pd.concat(
        [behaviour_agreement(c) for c in comparisons], ignore_index=True
    )
    ci = pd.DataFrame([courtship_index_pair(c) for c in comparisons])

    ci_matrix = ci[["ci_a", "ci_b"]].to_numpy()
    return StudySummary(
        per_behaviour=per_behaviour,
        courtship_index=ci,
        icc_courtship_index=ag.icc_2_1(ci_matrix),
        bland_altman_courtship_index=ag.bland_altman(ci["ci_a"].to_numpy(), ci["ci_b"].to_numpy()),
    )


def write_tables(summary: StudySummary, output_dir: Path) -> None:
    """Write the tidy result tables as CSVs (reviewer-checkable numbers)."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary.per_behaviour.to_csv(
        output_dir / "agreement_per_behaviour.csv", index=False, encoding="utf-8"
    )
    summary.courtship_index.to_csv(
        output_dir / "courtship_index_per_clip.csv", index=False, encoding="utf-8"
    )
    ba = summary.bland_altman_courtship_index
    pd.DataFrame(
        [
            {
                "icc_2_1_courtship_index": summary.icc_courtship_index,
                "ba_bias": ba.bias,
                "ba_sd_diff": ba.sd_diff,
                "ba_loa_lower": ba.loa_lower,
                "ba_loa_upper": ba.loa_upper,
                "n_clips": ba.n,
            }
        ]
    ).to_csv(output_dir / "study_summary.csv", index=False, encoding="utf-8")
