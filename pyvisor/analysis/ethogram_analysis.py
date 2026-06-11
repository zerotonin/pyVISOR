"""High-level ethogram analysis utilities.

Provides percentage, bout-duration, and transition-matrix computations
that can be driven from either the live GUI (TabResults) or offline
scripts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class BehaviourStats:
    """Analysis results for a single behaviour column."""
    label: str
    percentage: float  # 0–100
    bout_durations_s: np.ndarray  # array of individual bout durations in seconds
    bout_mean_s: float
    bout_std_s: float
    frequency_hz: float  # bouts per second of total recording
    bout_intervals_s: List[Tuple[float, float]] = field(default_factory=list)  # (start_s, duration_s)


@dataclass
class TransitionResult:
    """Transition matrix with labels."""
    matrix: np.ndarray
    labels: List[str]
    title: str = ""


@dataclass
class AnalysisResult:
    """Container for all analysis outputs."""
    labels: List[str]
    fps: float
    n_frames: int
    behaviour_stats: List[BehaviourStats]
    transition_matrix: np.ndarray  # (n_behaviours, n_behaviours)
    transition_labels: List[str]  # row/column labels for the matrix
    per_animal_transitions: List[TransitionResult] = field(default_factory=list)
    raw_data: Optional[np.ndarray] = None  # original binary matrix for raster plot


def analyse_ethogram(data: np.ndarray, labels: List[str], fps: float) -> AnalysisResult:
    """Run full analysis on an ethogram matrix.

    Parameters
    ----------
    data : ndarray, shape (n_frames, n_behaviours)
        Binary matrix where 1 indicates behaviour active at that frame.
    labels : list of str
        Human-readable label for each column.
    fps : float
        Frames per second of the source video.

    Returns
    -------
    AnalysisResult
    """
    n_frames, n_cols = data.shape

    # Filter out 'delete' columns — delete is an editing action, not a behaviour
    keep = [i for i in range(n_cols)
            if i < len(labels) and 'delete' not in labels[i].lower()]
    if keep:
        data = data[:, keep]
        labels = [labels[i] for i in keep]
    n_frames, n_cols = data.shape
    total_dur_s = n_frames / fps

    stats = []
    for col_idx in range(n_cols):
        col = data[:, col_idx]
        label = labels[col_idx] if col_idx < len(labels) else f"col_{col_idx}"

        # percentage
        percentage = (col.sum() / n_frames) * 100.0 if n_frames > 0 else 0.0

        # bout detection
        bout_durs = _bout_durations(col, fps)
        bout_ivs = _bout_intervals(col, fps)

        bout_mean = float(np.nanmean(bout_durs)) if len(bout_durs) > 0 else 0.0
        bout_std = float(np.nanstd(bout_durs)) if len(bout_durs) > 0 else 0.0

        # frequency
        freq = len(bout_durs) / total_dur_s if total_dur_s > 0 else 0.0

        stats.append(BehaviourStats(
            label=label,
            percentage=percentage,
            bout_durations_s=bout_durs,
            bout_mean_s=bout_mean,
            bout_std_s=bout_std,
            frequency_hz=freq,
            bout_intervals_s=bout_ivs,
        ))

    # transition matrix (global)
    trans_mat, trans_labels = _transition_matrix(data, labels)

    # per-animal transition matrices
    per_animal = _per_animal_transitions(data, labels)

    return AnalysisResult(
        labels=labels,
        fps=fps,
        n_frames=n_frames,
        behaviour_stats=stats,
        transition_matrix=trans_mat,
        transition_labels=trans_labels,
        per_animal_transitions=per_animal,
        raw_data=data,
    )


def _bout_durations(col: np.ndarray, fps: float) -> np.ndarray:
    """Return array of bout durations (seconds) for a single binary column."""
    if col.sum() == 0:
        return np.array([], dtype=float)

    diff = np.diff(col.astype(int))
    starts = np.where(diff == 1)[0] + 1
    stops = np.where(diff == -1)[0] + 1

    # handle edge cases: behaviour active at first or last frame
    if col[0] == 1:
        starts = np.insert(starts, 0, 0)
    if col[-1] == 1:
        stops = np.append(stops, len(col))

    # ensure paired
    n = min(len(starts), len(stops))
    starts = starts[:n]
    stops = stops[:n]

    durations_frames = stops - starts
    return durations_frames.astype(float) / fps


def _bout_intervals(col: np.ndarray, fps: float) -> List[Tuple[float, float]]:
    """Return list of (start_seconds, duration_seconds) for each bout.

    Suitable for matplotlib's ``broken_barh``.
    """
    if col.sum() == 0:
        return []

    diff = np.diff(col.astype(int))
    starts = np.where(diff == 1)[0] + 1
    stops = np.where(diff == -1)[0] + 1

    if col[0] == 1:
        starts = np.insert(starts, 0, 0)
    if col[-1] == 1:
        stops = np.append(stops, len(col))

    n = min(len(starts), len(stops))
    intervals = []
    for i in range(n):
        t_start = starts[i] / fps
        t_dur = (stops[i] - starts[i]) / fps
        intervals.append((t_start, t_dur))
    return intervals


def _transition_matrix(data: np.ndarray, labels: List[str]) -> Tuple[np.ndarray, List[str]]:
    """Compute a behaviour transition probability matrix.

    For each frame we determine the *dominant* active behaviour (the one
    with the lowest column index if multiple are active, or 'none' if no
    behaviour is active).  We then build a (n+1) x (n+1) matrix where
    row = 'from' and col = 'to', with 'none' as the last entry.
    Values are transition probabilities (rows sum to 1).
    """
    n_frames, n_cols = data.shape
    if n_frames < 2 or n_cols == 0:
        return np.zeros((1, 1)), ["none"]

    # For each frame find the dominant behaviour index (or n_cols for 'none')
    dominant = np.full(n_frames, n_cols, dtype=int)  # default = 'none'
    for frame in range(n_frames):
        active = np.where(data[frame] == 1)[0]
        if len(active) > 0:
            dominant[frame] = active[0]  # first active behaviour

    n_states = n_cols + 1  # behaviours + 'none'
    trans_labels = [_short_label(lbl) for lbl in labels] + ["none"]
    counts = np.zeros((n_states, n_states), dtype=float)

    for i in range(n_frames - 1):
        s_from = dominant[i]
        s_to = dominant[i + 1]
        counts[s_from, s_to] += 1

    # normalise rows to probabilities
    row_sums = counts.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # avoid division by zero
    prob_matrix = counts / row_sums

    return prob_matrix, trans_labels


def _short_label(label: str) -> str:
    """Extract a short name from 'animal_0 : aggression' style labels."""
    if " : " in label:
        parts = label.split(" : ", 1)
        return parts[1].strip()
    return label.strip()


def _extract_animal_name(label: str) -> str:
    """'animal_0 : aggression' → 'animal_0'"""
    if " : " in label:
        return label.split(" : ", 1)[0].strip()
    return "unknown"


def _per_animal_transitions(data: np.ndarray, labels: List[str]) -> List[TransitionResult]:
    """Compute a separate transition matrix for each animal."""
    from collections import OrderedDict

    # Group column indices by animal name
    animal_cols: OrderedDict[str, List[int]] = OrderedDict()
    for i, lbl in enumerate(labels):
        animal = _extract_animal_name(lbl)
        animal_cols.setdefault(animal, []).append(i)

    results = []
    for animal_name, col_indices in animal_cols.items():
        sub_data = data[:, col_indices]
        sub_labels = [labels[i] for i in col_indices]
        mat, tlabels = _transition_matrix(sub_data, sub_labels)
        results.append(TransitionResult(
            matrix=mat,
            labels=tlabels,
            title=animal_name,
        ))
    return results


# ── CSV export helpers ──────────────────────────────────────────────

def stats_to_dataframe(result: AnalysisResult) -> pd.DataFrame:
    """Return a summary DataFrame suitable for CSV export."""
    rows = []
    for s in result.behaviour_stats:
        rows.append({
            "behaviour": s.label,
            "percentage": round(s.percentage, 2),
            "mean_bout_duration_s": round(s.bout_mean_s, 4),
            "std_bout_duration_s": round(s.bout_std_s, 4),
            "frequency_hz": round(s.frequency_hz, 4),
            "n_bouts": len(s.bout_durations_s),
        })
    return pd.DataFrame(rows)


def transition_matrix_to_dataframe(result: AnalysisResult) -> pd.DataFrame:
    """Return the transition matrix as a labelled DataFrame."""
    return pd.DataFrame(
        np.round(result.transition_matrix, 4),
        index=result.transition_labels,
        columns=result.transition_labels,
    )
