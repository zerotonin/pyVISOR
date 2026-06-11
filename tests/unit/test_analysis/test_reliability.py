"""Unit tests for the reliability toolkit — expected values by hand."""
from __future__ import annotations

import numpy as np
import pytest

from pyvisor.analysis.reliability import agreement as ag
from pyvisor.analysis.reliability import annotation_io as aio
from pyvisor.analysis.reliability import measures as me


# ─────────────────────────────────────────────────────────────────
#  Cohen's κ
# ─────────────────────────────────────────────────────────────────
def test_cohen_kappa_binary_hand_value():
    a = np.array([1, 1, 0, 0, 1, 0, 1, 0])
    b = np.array([1, 0, 0, 0, 1, 0, 1, 1])
    # p_obs = 0.75, p_exp = 0.50  ->  κ = 0.5
    assert ag.cohen_kappa_binary(a, b) == pytest.approx(0.5)


def test_cohen_kappa_binary_perfect():
    a = np.array([1, 0, 1, 1, 0])
    assert ag.cohen_kappa_binary(a, a) == pytest.approx(1.0)


def test_cohen_kappa_binary_constant_is_nan():
    a = np.zeros(10, dtype=int)
    assert np.isnan(ag.cohen_kappa_binary(a, a))


def test_cohen_kappa_multiclass_hand_value():
    a = np.array([0, 1, 2, 0, 1])
    b = np.array([0, 2, 2, 0, 1])
    # p_obs = 0.8, p_exp = 0.32  ->  κ = 0.48/0.68
    assert ag.cohen_kappa_multiclass(a, b) == pytest.approx(0.48 / 0.68)


# ─────────────────────────────────────────────────────────────────
#  Precision / recall / F1
# ─────────────────────────────────────────────────────────────────
def test_precision_recall_f1_hand_value():
    ref = np.array([1, 1, 0, 0, 1])
    test = np.array([1, 0, 0, 1, 1])
    pr = ag.precision_recall_f1(ref, test)
    assert pr.precision == pytest.approx(2 / 3)
    assert pr.recall == pytest.approx(2 / 3)
    assert pr.f1 == pytest.approx(2 / 3)


def test_precision_recall_absent_behaviour_is_nan():
    ref = np.zeros(5, dtype=int)
    test = np.array([1, 0, 0, 0, 0])
    pr = ag.precision_recall_f1(ref, test)
    assert np.isnan(pr.recall)  # no positives in reference


# ─────────────────────────────────────────────────────────────────
#  ICC(2,1) — Shrout & Fleiss (1979) classic dataset
# ─────────────────────────────────────────────────────────────────
def test_icc_2_1_shrout_fleiss():
    x = np.array(
        [
            [9, 2, 5, 8],
            [6, 1, 3, 2],
            [8, 4, 6, 8],
            [7, 1, 2, 6],
            [10, 5, 6, 9],
            [6, 2, 4, 7],
        ],
        dtype=float,
    )
    assert ag.icc_2_1(x) == pytest.approx(0.290, abs=0.01)


def test_icc_2_1_perfect_agreement():
    col = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    x = np.column_stack([col, col])
    assert ag.icc_2_1(x) == pytest.approx(1.0)


# ─────────────────────────────────────────────────────────────────
#  Bland–Altman
# ─────────────────────────────────────────────────────────────────
def test_bland_altman_hand_value():
    a = np.array([1.0, 2.0, 3.0, 4.0])
    b = np.array([1.0, 1.0, 2.0, 2.0])
    ba = ag.bland_altman(a, b)
    assert ba.bias == pytest.approx(1.0)
    assert ba.sd_diff == pytest.approx(0.81649658, abs=1e-6)
    assert ba.loa_upper == pytest.approx(1.0 + 1.96 * ba.sd_diff)


# ─────────────────────────────────────────────────────────────────
#  Event-onset matching
# ─────────────────────────────────────────────────────────────────
def test_match_event_onsets_within_tolerance():
    ref = np.array([10, 20, 30])
    test = np.array([11, 25, 30])
    pr = ag.match_event_onsets(ref, test, tolerance_frames=2)
    assert pr.precision == pytest.approx(2 / 3)
    assert pr.recall == pytest.approx(2 / 3)


# ─────────────────────────────────────────────────────────────────
#  Derived measures
# ─────────────────────────────────────────────────────────────────
def test_bout_statistics_hand_value():
    vec = np.array([0, 1, 1, 0, 1, 0, 1, 1, 1])
    stats = me.bout_statistics(vec, fps=10.0)
    assert stats.n_bouts == 3
    assert stats.total_frames == 6
    assert stats.mean_duration_s == pytest.approx(0.2)
    assert stats.sd_duration_s == pytest.approx(0.1)


def test_latency_to_first():
    assert me.latency_to_first(np.array([0, 0, 1, 0]), fps=10.0) == pytest.approx(0.2)
    assert np.isnan(me.latency_to_first(np.zeros(4, dtype=int), fps=10.0))


def test_courtship_index():
    raster = np.array(
        [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0], [1, 0, 0]]
    )
    assert me.courtship_index(raster, behaviour_columns=[0, 1]) == pytest.approx(0.6)


def test_onset_frames():
    vec = np.array([0, 1, 1, 0, 1])
    assert list(me.onset_frames(vec)) == [1, 4]


# ─────────────────────────────────────────────────────────────────
#  Annotation I/O round-trip (GameThogram txt) + alignment
# ─────────────────────────────────────────────────────────────────
def test_gamethogram_txt_roundtrip(tmp_path):
    data = np.array([[1, 0], [0, 1], [1, 1], [0, 0]], dtype=int)
    labels = ["fly1 : courting", "fly1 : copulation"]
    header = "".join(f"COL{i + 1}: {lab}\n" for i, lab in enumerate(labels))
    fpos = tmp_path / "scores.txt"
    np.savetxt(fpos, data, fmt="%2i", header=header)

    raster = aio.load_gamethogram(fpos, fps=25.0)
    assert raster.behaviours == labels
    assert np.array_equal(raster.matrix(), data)
    assert raster.fps == 25.0


def test_align_intersects_behaviours_and_frames():
    a = aio.RasterAnnotation(
        table=_frame({"x": [1, 0, 1], "y": [0, 1, 0]}), fps=25.0, source="a"
    )
    b = aio.RasterAnnotation(
        table=_frame({"x": [1, 1, 0, 0], "z": [0, 0, 1, 1]}), fps=25.0, source="b"
    )
    a2, b2 = aio.align(a, b)
    assert a2.behaviours == ["x"]
    assert b2.behaviours == ["x"]
    assert a2.n_frames == 3 and b2.n_frames == 3


def test_align_rejects_fps_mismatch():
    a = aio.RasterAnnotation(table=_frame({"x": [1, 0]}), fps=25.0, source="a")
    b = aio.RasterAnnotation(table=_frame({"x": [1, 0]}), fps=30.0, source="b")
    with pytest.raises(ValueError):
        aio.align(a, b)


def _frame(cols):
    import pandas as pd

    return pd.DataFrame({k: np.array(v, dtype=bool) for k, v in cols.items()})
