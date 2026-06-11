# GameThogram validation protocol

*« one scoring session, the whole evidence base »*

This protocol specifies the single data-collection session that yields,
in one pass, the methodological evidence a behavioural-methods journal
(Methods in Ecology & Evolution, Behavior Research Methods, eNeuro)
expects of an annotation tool:

| Claim | Evidence produced | Statistic |
|---|---|---|
| Scores are reproducible between observers | inter-observer reliability | Cohen's κ (frame-wise, per behaviour); ICC(2,1) on the Courtship Index |
| Scores are reproducible within an observer | intra-observer (test–retest) reliability | ICC(2,1) on re-scored subset |
| GameThogram yields the same science as the standard tool | concurrent validity vs BORIS | ICC(2,1) + Bland–Altman on the Courtship Index; frame-wise κ |
| GameThogram is faster | scoring efficiency | seconds per video-minute, paired across tools |
| The gamepad workflow is usable | usability | System Usability Scale (SUS) |

All analysis is implemented in `pyvisor.analysis.reliability` and run
through `validation/run_reliability.py`; the timing and SUS analyses
are described in §6.

---

## 1  Design

A within-subject, counterbalanced design. Every observer scores every
clip in **both** tools; a subset is re-scored for test–retest.

- **Observers:** 3 trained scorers (minimum 2). Report training level.
- **Clips:** 20 *Drosophila* courtship clips, ~6 min each, sampled to
  span the full range of courtship intensity (low → high Courtship
  Index) so agreement is not estimated only where the behaviour is rare
  or saturated. Draw them from the existing single-pass corpus.
- **Behaviours:** the established courtship ethogram — orienting,
  tapping, wing extension (song), licking, attempted copulation,
  copulation. Use the *same* behaviour set and definitions in both
  tools (write a one-page ethogram definition sheet; cite it).
- **Tools:** GameThogram (gamepad) and BORIS (keyboard/mouse), the de
  facto standard.
- **Re-scoring:** each observer re-scores 8 of the 20 clips in
  GameThogram after ≥ 1 week (washout), for intra-observer reliability.

### Counterbalancing

Randomise, per observer, both clip order and which tool is used first,
so learning and fatigue do not load onto one tool. A Latin-square over
(observer × tool-first × clip-block) is sufficient at n = 3.

### Power / sample size

20 clips × 3 observers gives 60 scored clips per tool. For ICC, n = 20
targets with k = 3 raters detects ICC ≥ 0.7 against a null of 0.4 at
~80 % power; state this in the manuscript. For frame-wise κ the
effective sample is thousands of frames per clip, so κ precision is not
the limiting factor — clip count is.

---

## 2  Pre-registration of definitions (do this first)

Lock these before scoring, because they cannot be changed afterwards
without biasing the comparison:

1. The ethogram (behaviour names + operational definitions + onset/offset
   rules).
2. Which behaviours count toward the **Courtship Index** (the primary
   scalar readout).
3. The frame rate (all clips at a single fps; re-encode if mixed).
4. Mutually-exclusive vs co-occurring behaviours (must match between
   GameThogram's compatibility settings and the BORIS configuration).

---

## 3  Procedure

For each observer:

1. Calibrate the gamepad and the BORIS keymap to the same ethogram.
2. For each clip, in the counterbalanced tool order:
   - Start a stopwatch / log the wall-clock start.
   - Score the clip start-to-finish without pausing the *task* (pausing
     the video is allowed; the point is to measure realistic scoring
     effort).
   - Log wall-clock end. Record **active scoring time** = end − start −
     interruptions.
3. After the second tool for that clip, the observer records nothing
   else until the next clip (avoid cross-talk).
4. At the end of the session, each observer completes the **SUS**
   (10 items) for GameThogram, and optionally NASA-TLX.

Export, per clip per observer per tool:

- **GameThogram:** *Export Data* → text (`.txt`) — the frame×behaviour
  matrix the analysis reads natively.
- **BORIS:** *Observations → Export events → Tabular events* (`.tsv`).

---

## 4  What to log

A single timing sheet (`timing.csv`) with one row per
(clip × observer × tool):

```
clip_id, observer, tool, video_seconds, active_scoring_seconds
```

and the annotation files laid out so the manifest can find them
(see `validation/manifest.template.csv`).

---

## 5  File layout

```
validation/
├── protocol.md                 ← this file
├── manifest.template.csv       ← copy to manifest.csv and fill in
├── run_reliability.py          ← computes κ / ICC / Bland–Altman / CI
├── ethogram_definitions.md     ← the locked ethogram (you write this)
├── timing.csv                  ← scoring-time log (§6)
└── scores/
    ├── clip01_obsA.txt         ← GameThogram exports
    ├── clip01_obsB.txt
    ├── clip02_gamethogram.txt
    └── clip02_boris.tsv        ← BORIS tabular exports
```

Run the reliability analysis:

```bash
python validation/run_reliability.py validation/manifest.csv --out results/validation
```

Outputs (all CSV-backed for reviewers): `agreement_per_behaviour.csv`,
`courtship_index_per_clip.csv`, `study_summary.csv`, plus
`kappa_raincloud.{svg,png,csv}` and `bland_altman_ci.{svg,png,csv}`.

---

## 6  Efficiency and usability analyses

These two use the logged sheets rather than the annotation files.

- **Scoring time:** paired comparison of `active_scoring_seconds /
  video_seconds` between tools, within observer. Report median ratio and
  a paired resampling test (`FisherResamplingTest` from `reRandomStats`,
  `meanDiff`) plus a per-observer breakdown. A raincloud of seconds per
  video-minute, GameThogram vs BORIS, is the headline efficiency figure.
- **SUS:** standard 0–100 SUS score per observer; report mean ± SD and
  the adjective rating. Keep the raw 10-item responses as a CSV
  companion.

---

## 7  Reporting checklist (maps to the journal bar)

- [ ] κ per behaviour (table + raincloud), with prevalence noted — κ is
      deflated when a behaviour is rare, so report prevalence alongside.
- [ ] ICC(2,1) on the Courtship Index, inter- and intra-observer.
- [ ] Bland–Altman (bias + 95 % LoA) for GameThogram vs BORIS.
- [ ] Frame-wise κ GameThogram vs BORIS.
- [ ] Scoring-time ratio with paired test + figure.
- [ ] SUS (and TLX if collected).
- [ ] Ethogram definition sheet, manifest, and analysis code archived
      with the Zenodo release for reproducibility.
