#!/usr/bin/env python3
"""Run the validation reliability analysis from a clip manifest.

Reads a manifest CSV describing paired annotation passes, computes the
full agreement battery (κ, F1, ICC, Bland–Altman, Courtship Index) and
writes tidy result tables plus figures.

Manifest columns (one row per clip):
    clip_id              unique clip name
    fps                  frame rate
    n_frames             clip length in frames
    courtship_behaviours behaviour labels counted as courting,
                         ';'-separated (e.g. "orienting;tapping;wing")
    pass_a_path          annotation file for observer/tool A
    pass_a_tool          'gamethogram' or 'boris'
    pass_b_path          annotation file for observer/tool B
    pass_b_tool          'gamethogram' or 'boris'

Usage:
    python validation/run_reliability.py manifest.csv --out results/validation
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from pyvisor.analysis.reliability.annotation_io import (
    RasterAnnotation,
    load_boris_tabular,
    load_gamethogram,
)
from pyvisor.analysis.reliability.report import (
    ClipComparison,
    StudySummary,
    summarise_study,
    write_tables,
)


def _load_pass(path: Path, tool: str, fps: float, n_frames: int) -> RasterAnnotation:
    tool = tool.lower().strip()
    if tool == "gamethogram":
        return load_gamethogram(path, fps=fps)
    if tool == "boris":
        return load_boris_tabular(path, fps=fps, n_frames=n_frames)
    raise ValueError(f"unknown tool {tool!r} (expected 'gamethogram' or 'boris')")


def build_comparisons(manifest: pd.DataFrame, root: Path) -> list[ClipComparison]:
    comparisons = []
    for _, row in tqdm(list(manifest.iterrows()), desc="Loading annotation passes"):
        fps = float(row["fps"])
        n_frames = int(row["n_frames"])
        behaviours = [b.strip() for b in str(row["courtship_behaviours"]).split(";") if b.strip()]
        pass_a = _load_pass(root / row["pass_a_path"], row["pass_a_tool"], fps, n_frames)
        pass_b = _load_pass(root / row["pass_b_path"], row["pass_b_tool"], fps, n_frames)
        comparisons.append(
            ClipComparison(
                clip_id=str(row["clip_id"]),
                pass_a=pass_a,
                pass_b=pass_b,
                courtship_behaviours=behaviours,
            )
        )
    return comparisons


def render_figures(summary: StudySummary, output_dir: Path) -> None:
    """Optional figure step — skipped cleanly if matplotlib is unavailable."""
    try:
        from pyvisor.analysis.reliability.figures import plot_bland_altman, plot_kappa_raincloud
    except ImportError as exc:  # pragma: no cover
        print(f"Skipping figures (matplotlib unavailable): {exc}")
        return
    plot_kappa_raincloud(summary.per_behaviour, output_dir)
    plot_bland_altman(summary.courtship_index, summary.bland_altman_courtship_index, output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Manifest CSV of paired annotation passes")
    parser.add_argument("--out", type=Path, default=Path("results/validation"), help="Output directory")
    parser.add_argument("--no-figures", action="store_true", help="Write tables only")
    args = parser.parse_args()

    manifest = pd.read_csv(args.manifest)
    root = args.manifest.resolve().parent
    comparisons = build_comparisons(manifest, root)

    summary = summarise_study(comparisons)
    write_tables(summary, args.out)
    if not args.no_figures:
        render_figures(summary, args.out)

    ba = summary.bland_altman_courtship_index
    print(f"\nClips analysed       : {len(comparisons)}")
    print(f"ICC(2,1) Courtship Idx: {summary.icc_courtship_index:.3f}")
    print(f"Bland–Altman bias     : {ba.bias:+.3f}  (95% LoA {ba.loa_lower:+.3f} … {ba.loa_upper:+.3f})")
    print(f"Tables + figures      : {args.out}")


if __name__ == "__main__":
    main()
