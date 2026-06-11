# ╔══════════════════════════════════════════════════════════════════╗
# ║  GameThogram — reliability.annotation_io                         ║
# ║  « one loader for GameThogram and BORIS exports »                ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Parses GameThogram frame×behaviour matrices (txt / mat /        ║
# ║  xlsx / npy) and BORIS tabular-events exports into a shared      ║
# ║  frame-raster representation so any two passes can be aligned    ║
# ║  and compared frame for frame.                                   ║
# ╚══════════════════════════════════════════════════════════════════╝
"""Load heterogeneous annotation exports into a common frame raster.

The shared representation is :class:`RasterAnnotation` — a frames ×
behaviours boolean DataFrame plus the frame rate.  Everything in
:mod:`agreement` and :mod:`measures` consumes that representation, so
GameThogram and BORIS passes become directly comparable.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio

_COL_HEADER = re.compile(r"COL\d+:\s*(.+?)\s*$")


@dataclass(frozen=True)
class RasterAnnotation:
    """Frames × behaviours boolean table with a frame rate and source tag."""

    table: pd.DataFrame  # index = frame number, columns = behaviour labels
    fps: float
    source: str

    @property
    def n_frames(self) -> int:
        return len(self.table)

    @property
    def behaviours(self) -> list[str]:
        return list(self.table.columns)

    def column(self, behaviour: str) -> np.ndarray:
        return self.table[behaviour].to_numpy(dtype=bool)

    def matrix(self) -> np.ndarray:
        return self.table.to_numpy(dtype=int)


# ┌────────────────────────────────────────────────────────────┐
# │ GameThogram loaders  « txt · mat · xlsx · npy »            │
# └────────────────────────────────────────────────────────────┘


def load_gamethogram(path: Path, fps: float, labels: list[str] | None = None) -> RasterAnnotation:
    """Load a GameThogram export, dispatching on file suffix."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return _load_gamethogram_txt(path, fps)
    if suffix == ".mat":
        return _load_gamethogram_mat(path, fps)
    if suffix in {".xlsx", ".xls"}:
        return _load_gamethogram_xlsx(path, fps)
    if suffix == ".npy":
        return _load_gamethogram_npy(path, fps, labels)
    raise ValueError(f"unsupported GameThogram export suffix: {suffix!r}")


def _labels_from_header(lines: list[str], n_cols: int) -> list[str]:
    labels = [m.group(1) for line in lines if (m := _COL_HEADER.search(line))]
    if len(labels) == n_cols:
        return labels
    return [f"COL{i + 1}" for i in range(n_cols)]


def _load_gamethogram_txt(path: Path, fps: float) -> RasterAnnotation:
    header_lines = [
        line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("#")
    ]
    data = np.loadtxt(path, dtype=int, ndmin=2)
    labels = _labels_from_header(header_lines, data.shape[1])
    table = pd.DataFrame(data.astype(bool), columns=labels)
    return RasterAnnotation(table=table, fps=fps, source=f"gamethogram:{path.name}")


def _load_gamethogram_mat(path: Path, fps: float) -> RasterAnnotation:
    payload = sio.loadmat(path)
    data = np.asarray(payload["data"], dtype=int)
    info = payload.get("info", "")
    if isinstance(info, np.ndarray):
        info = info.item() if info.size else ""
    labels = _labels_from_header(str(info).splitlines(), data.shape[1])
    table = pd.DataFrame(data.astype(bool), columns=labels)
    return RasterAnnotation(table=table, fps=fps, source=f"gamethogram:{path.name}")


def _load_gamethogram_xlsx(path: Path, fps: float) -> RasterAnnotation:
    frame = pd.read_excel(path, header=0)
    table = frame.astype(bool)
    return RasterAnnotation(table=table, fps=fps, source=f"gamethogram:{path.name}")


def _load_gamethogram_npy(path: Path, fps: float, labels: list[str] | None) -> RasterAnnotation:
    data = np.load(path).astype(int)
    if data.ndim != 2:
        raise ValueError("npy raster must be 2-D (frames × behaviours)")
    cols = labels if labels is not None else [f"COL{i + 1}" for i in range(data.shape[1])]
    if len(cols) != data.shape[1]:
        raise ValueError(f"{len(cols)} labels for {data.shape[1]} columns")
    table = pd.DataFrame(data.astype(bool), columns=cols)
    return RasterAnnotation(table=table, fps=fps, source=f"gamethogram:{path.name}")


# ┌────────────────────────────────────────────────────────────┐
# │ BORIS loader  « tabular events → frame raster »           │
# └────────────────────────────────────────────────────────────┘


def _find_column(columns: list[str], *candidates: str) -> str | None:
    lowered = {c.lower().strip(): c for c in columns}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    return None


def load_boris_tabular(
    path: Path,
    fps: float,
    n_frames: int,
    behaviours: list[str] | None = None,
) -> RasterAnnotation:
    """Rasterise a BORIS "Export events → Tabular events" file.

    Handles state behaviours (START/STOP pairs) and point events.
    Expected columns (case-insensitive): a behaviour column
    (``Behavior``), a status column (``Status`` / ``Behavior type``
    with START/STOP/POINT), and a time column (``Time`` in seconds, or
    ``Image index`` / ``Frame`` in frames).

    Args:
        path:       BORIS tabular export (``.tsv`` or ``.csv``).
        fps:        Frames per second, to convert event times to frames.
        n_frames:   Length of the raster (match the GameThogram pass).
        behaviours: Restrict/order the output columns; defaults to all
                    behaviours seen in the file, sorted.
    """
    path = Path(path)
    sep = "\t" if path.suffix.lower() in {".tsv", ".txt"} else ","
    frame = pd.read_csv(path, sep=sep)
    cols = list(frame.columns)

    behav_col = _find_column(cols, "behavior", "behaviour")
    status_col = _find_column(cols, "status", "behavior type", "behaviour type")
    time_col = _find_column(cols, "time", "start (s)", "time (s)")
    frame_col = _find_column(cols, "image index", "frame", "frame index")
    if behav_col is None:
        raise ValueError(f"no behaviour column found in {cols}")
    if time_col is None and frame_col is None:
        raise ValueError(f"no time or frame column found in {cols}")

    def to_frame(row) -> int:
        if frame_col is not None and not pd.isna(row[frame_col]):
            return int(round(float(row[frame_col])))
        return int(round(float(row[time_col]) * fps))

    seen = sorted(frame[behav_col].dropna().unique().tolist())
    labels = behaviours if behaviours is not None else seen
    raster = pd.DataFrame(
        np.zeros((n_frames, len(labels)), dtype=bool),
        columns=labels,
    )

    open_start: dict[str, int] = {}
    for _, row in frame.iterrows():
        behav = row[behav_col]
        if behav not in raster.columns:
            continue
        status = str(row[status_col]).upper().strip() if status_col else "POINT"
        idx = to_frame(row)
        if status == "START":
            open_start[behav] = idx
        elif status == "STOP":
            start = open_start.pop(behav, None)
            if start is not None:
                lo, hi = sorted((start, idx))
                raster.loc[lo : max(lo, hi - 1), behav] = True
        else:  # POINT or unknown — mark the single frame
            if 0 <= idx < n_frames:
                raster.loc[idx, behav] = True

    return RasterAnnotation(table=raster, fps=fps, source=f"boris:{path.name}")


# ┌────────────────────────────────────────────────────────────┐
# │ Alignment  « shared behaviours over a shared frame span »  │
# └────────────────────────────────────────────────────────────┘


def align(a: RasterAnnotation, b: RasterAnnotation) -> tuple[RasterAnnotation, RasterAnnotation]:
    """Restrict two annotations to common behaviours and frame length.

    Raises if the frame rates differ or the behaviour sets do not
    overlap — both are signs the two passes are not comparable.
    """
    if not np.isclose(a.fps, b.fps):
        raise ValueError(f"frame-rate mismatch: {a.fps} vs {b.fps}")

    shared = [c for c in a.behaviours if c in set(b.behaviours)]
    if not shared:
        raise ValueError("no shared behaviours between the two annotations")

    n = min(a.n_frames, b.n_frames)
    a_aligned = RasterAnnotation(a.table.loc[: n - 1, shared].reset_index(drop=True), a.fps, a.source)
    b_aligned = RasterAnnotation(b.table.loc[: n - 1, shared].reset_index(drop=True), b.fps, b.source)
    return a_aligned, b_aligned
