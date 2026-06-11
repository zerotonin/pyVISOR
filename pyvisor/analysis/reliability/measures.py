# ╔══════════════════════════════════════════════════════════════════╗
# ║  GameThogram — reliability.measures                              ║
# ║  « derived behavioural measures per clip »                       ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Courtship Index, bout counts and durations, and latency to      ║
# ║  first occurrence — the scalar readouts fed to ICC and           ║
# ║  Bland–Altman across clips.                                      ║
# ╚══════════════════════════════════════════════════════════════════╝
"""Per-clip behavioural measures derived from a frame raster."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BoutStatistics:
    n_bouts: int
    total_frames: int
    mean_duration_s: float
    sd_duration_s: float


def proportion_active(raster: np.ndarray) -> float:
    """Fraction of frames in which the behaviour is active.

    With a 1-D behaviour vector this is that behaviour's index; pass a
    2-D (frames × behaviours) slice and the row-wise ``any`` to obtain
    a Courtship Index over a *set* of courtship behaviours.
    """
    a = np.asarray(raster).astype(bool)
    if a.ndim == 2:
        a = a.any(axis=1)
    if a.size == 0:
        raise ValueError("empty raster")
    return float(np.mean(a))


def courtship_index(raster: np.ndarray, behaviour_columns: np.ndarray) -> float:
    """Courtship Index: proportion of frames courting.

    Args:
        raster:            (frames × behaviours) 0-1 matrix.
        behaviour_columns: Indices of the columns that count as
                           courtship (e.g. orienting, tapping, wing
                           extension, licking, attempted copulation).
    """
    matrix = np.asarray(raster).astype(bool)
    if matrix.ndim != 2:
        raise ValueError("raster must be 2-D (frames × behaviours)")
    courting = matrix[:, list(behaviour_columns)].any(axis=1)
    return float(np.mean(courting))


def _runs_of_true(vector: np.ndarray) -> list[tuple[int, int]]:
    """Return (start, stop_exclusive) frame indices of each True run."""
    a = np.asarray(vector).astype(bool)
    padded = np.concatenate([[False], a, [False]])
    edges = np.diff(padded.astype(int))
    starts = np.where(edges == 1)[0]
    stops = np.where(edges == -1)[0]
    return list(zip(starts.tolist(), stops.tolist()))


def bout_statistics(behaviour_vector: np.ndarray, fps: float) -> BoutStatistics:
    """Count and time the contiguous bouts of one behaviour."""
    if fps <= 0:
        raise ValueError("fps must be positive")
    runs = _runs_of_true(behaviour_vector)
    durations_frames = np.array([stop - start for start, stop in runs], dtype=float)
    durations_s = durations_frames / fps
    n = len(runs)
    return BoutStatistics(
        n_bouts=n,
        total_frames=int(durations_frames.sum()),
        mean_duration_s=float(durations_s.mean()) if n else 0.0,
        sd_duration_s=float(durations_s.std(ddof=1)) if n > 1 else 0.0,
    )


def latency_to_first(behaviour_vector: np.ndarray, fps: float) -> float:
    """Seconds until the behaviour first becomes active.

    Returns ``nan`` if the behaviour never occurs.
    """
    if fps <= 0:
        raise ValueError("fps must be positive")
    a = np.asarray(behaviour_vector).astype(bool)
    hits = np.where(a)[0]
    if hits.size == 0:
        return float("nan")
    return float(hits[0] / fps)


def onset_frames(behaviour_vector: np.ndarray) -> np.ndarray:
    """Frame indices at which the behaviour switches from off to on."""
    a = np.asarray(behaviour_vector).astype(bool)
    padded = np.concatenate([[False], a])
    return np.where(np.diff(padded.astype(int)) == 1)[0]
