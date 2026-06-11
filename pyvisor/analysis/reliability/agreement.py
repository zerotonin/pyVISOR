# ╔══════════════════════════════════════════════════════════════════╗
# ║  GameThogram — reliability.agreement                             ║
# ║  « frame-wise κ, ICC, Bland–Altman, precision/recall/F1 »        ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  Inter- and intra-observer agreement statistics for the          ║
# ║  validation study.  Pure numpy/scipy — no extra dependencies.    ║
# ║                                                                  ║
# ║  Closed-form Cohen's κ and Shrout & Fleiss ICC(2,1); the         ║
# ║  resampling time comparison lives in the run script.             ║
# ╚══════════════════════════════════════════════════════════════════╝
"""Agreement statistics for two (or more) annotation passes.

All functions are pure: they take numpy arrays and return floats or
frozen result dataclasses, so they are trivial to unit-test against
hand-computed values.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# ┌────────────────────────────────────────────────────────────┐
# │ Result containers  « frozen, self-documenting »            │
# └────────────────────────────────────────────────────────────┘


@dataclass(frozen=True)
class ConfusionCounts:
    """Frame-wise 2×2 counts for a single behaviour (B scored against A)."""

    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int

    @property
    def n_frames(self) -> int:
        return (
            self.true_positive
            + self.false_positive
            + self.false_negative
            + self.true_negative
        )


@dataclass(frozen=True)
class PrecisionRecall:
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class BlandAltman:
    """Bias and 95 % limits of agreement for a scalar across clips."""

    bias: float
    sd_diff: float
    loa_lower: float
    loa_upper: float
    n: int


# ┌────────────────────────────────────────────────────────────┐
# │ Cohen's κ  « chance-corrected frame agreement »            │
# └────────────────────────────────────────────────────────────┘


def cohen_kappa_binary(rater_a: np.ndarray, rater_b: np.ndarray) -> float:
    """Cohen's κ for one behaviour scored present/absent per frame.

    Args:
        rater_a: Boolean/0-1 vector, one entry per frame.
        rater_b: Boolean/0-1 vector, aligned to *rater_a*.

    Returns:
        κ, or ``nan`` when chance agreement is 1 (the behaviour is
        constant for both raters, leaving κ undefined).
    """
    a = np.asarray(rater_a).astype(bool)
    b = np.asarray(rater_b).astype(bool)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: {a.shape} vs {b.shape}")
    n = a.size
    if n == 0:
        raise ValueError("empty annotation vectors")

    tp = int(np.sum(a & b))
    tn = int(np.sum(~a & ~b))
    p_observed = (tp + tn) / n

    p_a_pos = a.sum() / n
    p_b_pos = b.sum() / n
    p_expected = p_a_pos * p_b_pos + (1.0 - p_a_pos) * (1.0 - p_b_pos)

    if np.isclose(p_expected, 1.0):
        return float("nan")
    return (p_observed - p_expected) / (1.0 - p_expected)


def cohen_kappa_multiclass(state_a: np.ndarray, state_b: np.ndarray) -> float:
    """Cohen's κ for a single mutually-exclusive state per frame.

    Use this when each frame carries exactly one behavioural state
    (a categorical label); use :func:`cohen_kappa_binary` per column
    for multi-label ethograms where behaviours may co-occur.
    """
    a = np.asarray(state_a)
    b = np.asarray(state_b)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: {a.shape} vs {b.shape}")
    n = a.size
    if n == 0:
        raise ValueError("empty annotation vectors")

    labels = np.unique(np.concatenate([a, b]))
    p_observed = np.mean(a == b)
    p_expected = 0.0
    for label in labels:
        p_expected += (np.mean(a == label)) * (np.mean(b == label))

    if np.isclose(p_expected, 1.0):
        return float("nan")
    return (p_observed - p_expected) / (1.0 - p_expected)


def percent_agreement(rater_a: np.ndarray, rater_b: np.ndarray) -> float:
    """Raw proportion of frames on which the two raters agree."""
    a = np.asarray(rater_a).astype(bool)
    b = np.asarray(rater_b).astype(bool)
    return float(np.mean(a == b))


# ┌────────────────────────────────────────────────────────────┐
# │ Precision / recall / F1  « A as reference, B as test »     │
# └────────────────────────────────────────────────────────────┘


def confusion_counts(reference: np.ndarray, test: np.ndarray) -> ConfusionCounts:
    """Frame-wise 2×2 counts, treating *reference* as ground truth."""
    ref = np.asarray(reference).astype(bool)
    tst = np.asarray(test).astype(bool)
    if ref.shape != tst.shape:
        raise ValueError(f"shape mismatch: {ref.shape} vs {tst.shape}")
    return ConfusionCounts(
        true_positive=int(np.sum(ref & tst)),
        false_positive=int(np.sum(~ref & tst)),
        false_negative=int(np.sum(ref & ~tst)),
        true_negative=int(np.sum(~ref & ~tst)),
    )


def precision_recall_f1(reference: np.ndarray, test: np.ndarray) -> PrecisionRecall:
    """Precision, recall and F1 of *test* against *reference*.

    A component is ``nan`` when its denominator is zero (e.g. recall
    when the behaviour never occurs in the reference).
    """
    c = confusion_counts(reference, test)
    p_denom = c.true_positive + c.false_positive
    r_denom = c.true_positive + c.false_negative
    precision = c.true_positive / p_denom if p_denom else float("nan")
    recall = c.true_positive / r_denom if r_denom else float("nan")
    if np.isnan(precision) or np.isnan(recall) or (precision + recall) == 0:
        f1 = float("nan")
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return PrecisionRecall(precision=precision, recall=recall, f1=f1)


# ┌────────────────────────────────────────────────────────────┐
# │ ICC(2,1)  « two-way random, single rater, abs. agreement » │
# └────────────────────────────────────────────────────────────┘


def icc_2_1(scores: np.ndarray) -> float:
    """Shrout & Fleiss ICC(2,1) for an (n targets × k raters) matrix.

    Two-way random-effects, single-measure, absolute agreement — the
    correct ICC for "do independent observers reproduce the same
    per-clip value (e.g. Courtship Index)".

    Args:
        scores: Array of shape (n_targets, n_raters); rows are clips,
                columns are observers.

    Returns:
        ICC(2,1).  Returns ``nan`` if total variance is zero.
    """
    x = np.asarray(scores, dtype=float)
    if x.ndim != 2:
        raise ValueError("scores must be 2-D (targets × raters)")
    n, k = x.shape
    if n < 2 or k < 2:
        raise ValueError("need at least 2 targets and 2 raters")

    grand = x.mean()
    ss_total = np.sum((x - grand) ** 2)
    if np.isclose(ss_total, 0.0):
        return float("nan")

    row_means = x.mean(axis=1)
    col_means = x.mean(axis=0)
    ss_rows = k * np.sum((row_means - grand) ** 2)
    ss_cols = n * np.sum((col_means - grand) ** 2)
    ss_error = ss_total - ss_rows - ss_cols

    ms_rows = ss_rows / (n - 1)
    ms_cols = ss_cols / (k - 1)
    ms_error = ss_error / ((n - 1) * (k - 1))

    denom = ms_rows + (k - 1) * ms_error + (k / n) * (ms_cols - ms_error)
    if np.isclose(denom, 0.0):
        return float("nan")
    return (ms_rows - ms_error) / denom


# ┌────────────────────────────────────────────────────────────┐
# │ Bland–Altman  « method-comparison for a scalar »          │
# └────────────────────────────────────────────────────────────┘


def bland_altman(method_a: np.ndarray, method_b: np.ndarray) -> BlandAltman:
    """Bias and 95 % limits of agreement between two scalar series.

    One value per clip from each method/observer (e.g. Courtship
    Index from GameThogram vs BORIS).
    """
    a = np.asarray(method_a, dtype=float)
    b = np.asarray(method_b, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: {a.shape} vs {b.shape}")
    if a.size < 2:
        raise ValueError("need at least 2 paired observations")

    diff = a - b
    bias = float(np.mean(diff))
    sd = float(np.std(diff, ddof=1))
    return BlandAltman(
        bias=bias,
        sd_diff=sd,
        loa_lower=bias - 1.96 * sd,
        loa_upper=bias + 1.96 * sd,
        n=int(a.size),
    )


# ┌────────────────────────────────────────────────────────────┐
# │ Event-onset matching  « backs the frame-accuracy claim »  │
# └────────────────────────────────────────────────────────────┘


def match_event_onsets(
    onsets_reference: np.ndarray,
    onsets_test: np.ndarray,
    tolerance_frames: int,
) -> PrecisionRecall:
    """Match behaviour onsets within ±*tolerance_frames* (greedy nearest).

    Each reference onset may match at most one test onset and vice
    versa.  Returns event-level precision/recall/F1 — the statistic
    for "annotations land on the right frame".
    """
    ref = np.sort(np.asarray(onsets_reference, dtype=int))
    tst = np.sort(np.asarray(onsets_test, dtype=int))
    if tolerance_frames < 0:
        raise ValueError("tolerance_frames must be non-negative")

    used_test = np.zeros(tst.size, dtype=bool)
    true_positive = 0
    for r in ref:
        candidates = np.where(~used_test & (np.abs(tst - r) <= tolerance_frames))[0]
        if candidates.size:
            nearest = candidates[np.argmin(np.abs(tst[candidates] - r))]
            used_test[nearest] = True
            true_positive += 1

    false_negative = int(ref.size - true_positive)
    false_positive = int(tst.size - true_positive)

    p_denom = true_positive + false_positive
    r_denom = true_positive + false_negative
    precision = true_positive / p_denom if p_denom else float("nan")
    recall = true_positive / r_denom if r_denom else float("nan")
    if np.isnan(precision) or np.isnan(recall) or (precision + recall) == 0:
        f1 = float("nan")
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return PrecisionRecall(precision=precision, recall=recall, f1=f1)
