"""Reliability and method-comparison toolkit for the validation study.

Loads GameThogram and BORIS annotation exports into a common frame
raster (:mod:`annotation_io`), derives per-clip behavioural measures
(:mod:`measures`), and computes inter-/intra-observer and tool-vs-tool
agreement statistics (:mod:`agreement`).
"""
from __future__ import annotations

from pyvisor.analysis.reliability.agreement import (
    BlandAltman,
    ConfusionCounts,
    PrecisionRecall,
    bland_altman,
    cohen_kappa_binary,
    cohen_kappa_multiclass,
    confusion_counts,
    icc_2_1,
    match_event_onsets,
    percent_agreement,
    precision_recall_f1,
)
from pyvisor.analysis.reliability.annotation_io import (
    RasterAnnotation,
    align,
    load_boris_tabular,
    load_gamethogram,
)
from pyvisor.analysis.reliability.measures import (
    BoutStatistics,
    bout_statistics,
    courtship_index,
    latency_to_first,
    onset_frames,
    proportion_active,
)

__all__ = [
    "BlandAltman",
    "BoutStatistics",
    "ConfusionCounts",
    "PrecisionRecall",
    "RasterAnnotation",
    "align",
    "bland_altman",
    "bout_statistics",
    "cohen_kappa_binary",
    "cohen_kappa_multiclass",
    "confusion_counts",
    "courtship_index",
    "icc_2_1",
    "latency_to_first",
    "load_boris_tabular",
    "load_gamethogram",
    "match_event_onsets",
    "onset_frames",
    "percent_agreement",
    "precision_recall_f1",
    "proportion_active",
]
