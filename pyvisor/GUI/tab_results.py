"""Results Overview tab — live analysis plots with export.

Displays behaviour percentages, bout durations and a transition‐probability
heatmap computed from the current scoring session.  Each plot can be exported
individually as CSV, PNG or SVG.
"""
from __future__ import annotations

import os
from typing import Optional

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox, QScrollArea, QSizePolicy, QGroupBox,
)

from .model.gui_data_interface import GUIDataInterface
from ..paths import ensure_extension as _ensure_extension
from ..analysis.ethogram_analysis import (
    analyse_ethogram,
    stats_to_dataframe,
    transition_matrix_to_dataframe,
    AnalysisResult,
)

HERE = os.path.dirname(os.path.abspath(__file__))

# Matplotlib style defaults — keep text as text in SVG
matplotlib.rcParams["svg.fonttype"] = "none"

# Colour palette (colour‐blind friendly, based on Tol's muted scheme)
_PALETTE = [
    "#332288", "#88CCEE", "#44AA99", "#117733",
    "#999933", "#DDCC77", "#CC6677", "#882255",
    "#AA4499", "#661100", "#6699CC", "#AA4466",
]


def _pick_colours(n: int):
    return [_PALETTE[i % len(_PALETTE)] for i in range(n)]


class TabResults(QWidget):
    """Results tab — analysis plots with export.

    Displays behaviour percentages, bout durations, and transition
    matrices computed from the current scoring session or a
    previously saved sidecar file. Each plot can be exported as
    CSV, PNG, or SVG.
    """
    """Fourth tab of the pyVISOR main GUI — analysis & export."""

    def __init__(self, parent: QWidget, gui_data_interface: GUIDataInterface):
        super().__init__()
        self.parent = parent
        self.gui_data_interface = gui_data_interface
        self._result: Optional[AnalysisResult] = None
        self._cbar = None
        self._init_UI()

    # ──────────────────────────────────────────────────────────────
    #  UI construction
    # ──────────────────────────────────────────────────────────────
    def _init_UI(self):
        # main layout
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        # refresh button row
        btn_row = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh analysis from scorer")
        self.btn_refresh.setStyleSheet(
            "color: #fff; background: #336699; font-weight: bold; padding: 6px 16px;")
        self.btn_refresh.setToolTip("Compute analysis from the current scoring session\n"
                                 "or from the saved resume file.")
        self.btn_refresh.clicked.connect(self._on_refresh)
        btn_row.addWidget(self.btn_refresh)
        btn_row.addStretch()
        outer.addLayout(btn_row)

        # scrollable area for plot groups
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent;")
        scroll_content = QWidget()
        self._plots_layout = QVBoxLayout(scroll_content)
        self._plots_layout.setSpacing(16)

        # ethogram raster (dynamic height — created on refresh)
        self._raster_grp = None
        self._raster_fig = None
        self._raster_canvas = None

        # percentage plot
        self._fig_pct, self._ax_pct, self._canvas_pct, grp_pct = \
            self._make_plot_group("Behaviour Percentages", height=280)
        self._plots_layout.addWidget(grp_pct)

        # bout duration plot
        self._fig_bout, self._ax_bout, self._canvas_bout, grp_bout = \
            self._make_plot_group("Mean Bout Duration", height=280)
        self._plots_layout.addWidget(grp_bout)

        # transition matrix (global)
        self._fig_trans, self._ax_trans, self._canvas_trans, grp_trans = \
            self._make_plot_group("Transition Matrix (all animals)", height=360)
        self._plots_layout.addWidget(grp_trans)

        # per-animal transition matrices (created dynamically)
        self._per_animal_groups = []

        self._plots_layout.addStretch()
        scroll.setWidget(scroll_content)
        outer.addWidget(scroll, stretch=1)

        # placeholder label
        self._placeholder = QLabel(
            "Press  \"Refresh analysis from scorer\"  after scoring a video "
            "to see results here.")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet(
            "color: #fff; background: rgba(0,0,0,120); padding: 24px; "
            "font-size: 14px;")
        self._plots_layout.insertWidget(0, self._placeholder)

    def _make_plot_group(self, title: str, height: int = 300):
        """Create a titled group box containing a matplotlib canvas + export buttons."""
        grp = QGroupBox(title)
        grp.setStyleSheet(
            "QGroupBox { color: #fff; font-weight: bold; font-size: 13px; "
            "border: 1px solid rgba(255,255,255,80); border-radius: 4px; "
            "margin-top: 8px; padding-top: 16px; background: rgba(0,0,0,100); }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; }")
        vbox = QVBoxLayout(grp)

        fig = Figure(figsize=(7, 3), dpi=100, facecolor="none")
        fig.patch.set_alpha(0.0)
        ax = fig.add_subplot(111)
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(height)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        canvas.setStyleSheet("background: transparent;")
        vbox.addWidget(canvas)

        # export buttons
        btn_row = QHBoxLayout()
        for fmt in ("CSV", "PNG", "SVG"):
            btn = QPushButton(f"Export {fmt}")
            btn.setStyleSheet(
                "color: #fff; background: #555; padding: 4px 10px;")
            btn.clicked.connect(
                lambda checked, t=title, f=fmt: self._export(t, f))
            btn_row.addWidget(btn)
        btn_row.addStretch()
        vbox.addLayout(btn_row)

        grp.setVisible(False)  # hidden until analysis runs
        return fig, ax, canvas, grp

    # ──────────────────────────────────────────────────────────────
    #  Analysis trigger
    # ──────────────────────────────────────────────────────────────
    def _on_refresh(self):
        scorer = self.gui_data_interface.manual_scorer
        data = None
        labels = []
        fps = 25.0

        # Try 1: get live data from scorer
        if scorer is not None:
            data = scorer.get_data()
            labels = scorer.get_labels()
            if hasattr(scorer, 'movie') and scorer.movie is not None:
                fps = float(getattr(scorer.movie, '_movie_fps',
                                    getattr(scorer.movie, 'fps', 25)))

        # Try 2: fall back to sidecar file
        if (data is False or data is None) and scorer is not None:
            data, labels, fps = self._load_from_sidecar(scorer)

        if data is False or data is None or (hasattr(data, 'size') and data.size == 0):
            QMessageBox.warning(
                self, "No data available",
                "No annotation data found. Either:\n"
                "• Run the scorer and annotate some video, or\n"
                "• Load a video that has a .pyvisor.pkl sidecar file.",
                QMessageBox.Ok)
            return

        self._result = analyse_ethogram(data, labels, fps)
        self._draw_all()

    @staticmethod
    def _load_from_sidecar(scorer):
        """Try to load data from the sidecar pickle."""
        import pickle as _pickle
        path = scorer._sidecar_path() if hasattr(scorer, '_sidecar_path') else ""
        if not path:
            return None, [], 25.0
        try:
            with open(path, 'rb') as fh:
                session = _pickle.load(fh)
            data = session.get('data')
            labels = session.get('labels', [])
            fps = session.get('fps', 25.0)
            if data is not None:
                print("Results loaded from sidecar: {}".format(path))
            return data, labels, fps
        except FileNotFoundError:
            return None, [], 25.0
        except Exception as exc:
            print("Could not load sidecar for results: {}".format(exc))
            return None, [], 25.0

    # ──────────────────────────────────────────────────────────────
    #  Drawing
    # ──────────────────────────────────────────────────────────────
    def _draw_all(self):
        if self._result is None:
            return
        self._placeholder.setVisible(False)
        self._draw_ethogram_raster()
        self._draw_percentages()
        self._draw_bout_durations()
        self._draw_transition_matrix()
        self._draw_per_animal_transitions()

    def _draw_ethogram_raster(self):
        """Draw a raster/timeline plot: one subplot per animal, coloured bars per behaviour."""
        from collections import OrderedDict
        from matplotlib.ticker import FuncFormatter

        r = self._result
        if r is None:
            return

        # ── Group behaviours by animal ──────────────────────────
        animals = OrderedDict()  # animal_name -> list of BehaviourStats
        for s in r.behaviour_stats:
            animal, behav = _split_label(s.label)
            animals.setdefault(animal, []).append(s)

        n_animals = len(animals)
        if n_animals == 0:
            return

        total_dur_s = r.n_frames / r.fps

        # ── Remove old raster widget if present ─────────────────
        if self._raster_grp is not None:
            self._raster_grp.setVisible(False)
            self._plots_layout.removeWidget(self._raster_grp)
            self._raster_grp.deleteLater()
            self._raster_grp = None

        # ── Compute dynamic height ──────────────────────────────
        max_behavs = max(len(stats) for stats in animals.values())
        row_h = 22  # pixels per behaviour row
        subplot_h = max(100, max_behavs * row_h + 60)
        total_h = subplot_h * n_animals + 40

        # ── Create plot group ───────────────────────────────────
        fig, _, canvas, grp = self._make_plot_group(
            "Ethogram Timeline", height=total_h)
        fig.clear()
        axes = fig.subplots(n_animals, 1, sharex=True, squeeze=False)
        axes = [ax[0] for ax in axes]

        colours = self._get_behaviour_colours(r.labels)
        colour_map = {s.label: colours[i] for i, s in enumerate(r.behaviour_stats)}

        for ax_idx, (animal_name, stats_list) in enumerate(animals.items()):
            ax = axes[ax_idx]
            n_behavs = len(stats_list)
            behav_names = []

            for row, s in enumerate(stats_list):
                _, bname = _split_label(s.label)
                behav_names.append(bname)
                c = colour_map.get(s.label, '#888888')

                if s.bout_intervals_s:
                    ax.broken_barh(
                        s.bout_intervals_s,
                        (row - 0.4, 0.8),
                        facecolors=c,
                        edgecolors='none',
                        linewidth=0,
                    )

            ax.set_yticks(range(n_behavs))
            ax.set_yticklabels(behav_names, fontsize=8, color='white')
            ax.set_ylim(-0.5, n_behavs - 0.5)
            ax.invert_yaxis()
            ax.set_xlim(0, total_dur_s)
            ax.set_title(animal_name, fontsize=11, color='white', pad=4)
            ax.tick_params(colors='white', labelsize=8)
            ax.set_facecolor('#484b4d')
            for spine in ax.spines.values():
                spine.set_color('white')
                spine.set_alpha(0.3)

            # light grid on x axis
            ax.grid(axis='x', color='white', alpha=0.15, linewidth=0.5)

        # ── Format x-axis as HH:MM:SS on the bottom subplot ────
        def _fmt_time(x, _):
            h = int(x // 3600)
            m = int((x % 3600) // 60)
            s = int(x % 60)
            return f"{h:02d}:{m:02d}:{s:02d}"

        axes[-1].xaxis.set_major_formatter(FuncFormatter(_fmt_time))
        axes[-1].set_xlabel("Time (HH:MM:SS)", fontsize=10, color='white')

        fig.set_facecolor('#3c3f41')
        fig.tight_layout()
        canvas.draw()
        grp.setVisible(True)

        # Insert at position 0 (before percentages)
        self._plots_layout.insertWidget(0, grp)
        self._raster_grp = grp
        self._raster_fig = fig
        self._raster_canvas = canvas

    def _draw_percentages(self):
        r = self._result
        ax = self._ax_pct
        ax.clear()

        stats = r.behaviour_stats
        labels = [s.label for s in stats]
        values = [s.percentage for s in stats]
        colours = self._get_behaviour_colours(labels)
        short = [_short(lab) for lab in labels]

        y_pos = np.arange(len(stats))
        ax.barh(y_pos, values, color=colours, edgecolor="white", linewidth=0.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(short, fontsize=9, color="white")
        ax.set_xlabel("% of total frames", fontsize=10, color="white")
        ax.set_xlim(0, max(max(values) * 1.15, 1) if values else 1)
        ax.invert_yaxis()
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("white")
            spine.set_alpha(0.4)
        ax.set_facecolor("#484b4d")

        for i, v in enumerate(values):
            ax.text(v + 0.3, i, f"{v:.1f}%", va="center",
                    fontsize=8, color="white")

        self._fig_pct.set_facecolor("#3c3f41")
        self._fig_pct.tight_layout()
        self._canvas_pct.draw()
        self._canvas_pct.parentWidget().setVisible(True)

    def _draw_bout_durations(self):
        r = self._result
        ax = self._ax_bout
        ax.clear()

        stats = r.behaviour_stats
        labels = [_short(s.label) for s in stats]
        means = [s.bout_mean_s for s in stats]
        stds = [s.bout_std_s for s in stats]
        colours = self._get_behaviour_colours([s.label for s in stats])

        x_pos = np.arange(len(stats))
        ax.bar(x_pos, means, yerr=stds, color=colours,
               edgecolor="white", linewidth=0.5, capsize=3,
               error_kw={"ecolor": "white", "elinewidth": 1})
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, fontsize=9, color="white", rotation=30,
                           ha="right")
        ax.set_ylabel("Duration (s)", fontsize=10, color="white")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("white")
            spine.set_alpha(0.4)
        ax.set_facecolor("#484b4d")

        self._fig_bout.set_facecolor("#3c3f41")
        self._fig_bout.tight_layout()
        self._canvas_bout.draw()
        self._canvas_bout.parentWidget().setVisible(True)

    def _draw_transition_matrix(self):
        r = self._result
        self._draw_single_transition(
            self._fig_trans, self._ax_trans, self._canvas_trans,
            r.transition_matrix, r.transition_labels,
            "Transition Matrix (all animals)")

    def _draw_per_animal_transitions(self):
        """Draw one transition matrix per animal, creating plot groups dynamically."""
        # Remove old per-animal groups
        for fig, ax, canvas, grp in self._per_animal_groups:
            grp.setVisible(False)
            self._plots_layout.removeWidget(grp)
            grp.deleteLater()
        self._per_animal_groups = []

        r = self._result
        for tr in r.per_animal_transitions:
            title = "Transitions — {}".format(tr.title)
            fig, ax, canvas, grp = self._make_plot_group(title, height=320)
            # Insert before the stretch at the end
            idx = self._plots_layout.count() - 1
            self._plots_layout.insertWidget(idx, grp)
            self._draw_single_transition(fig, ax, canvas, tr.matrix, tr.labels, title)
            self._per_animal_groups.append((fig, ax, canvas, grp))

    def _draw_single_transition(self, fig, ax, canvas, mat, labels, title):
        """Draw a transition matrix heatmap with pseudo-log colour scale."""
        from matplotlib.colors import SymLogNorm
        # Clear entire figure (removes old colorbars)
        fig.clear()
        ax = fig.add_subplot(111)

        n = mat.shape[0]
        vmax = max(mat.max(), 0.01)
        norm = SymLogNorm(linthresh=0.01, linscale=0.5, vmin=0, vmax=vmax)

        im = ax.imshow(mat, cmap="YlOrRd", aspect="auto", norm=norm)

        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(n))
        ax.set_xticklabels(labels, fontsize=8, color="white", rotation=45, ha="right")
        ax.set_yticklabels(labels, fontsize=8, color="white")
        ax.set_xlabel("To", fontsize=10, color="white")
        ax.set_ylabel("From", fontsize=10, color="white")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("white")
            spine.set_alpha(0.4)
        ax.set_facecolor("#484b4d")

        # annotate cells
        thresh = mat.max() / 2.0
        for i in range(n):
            for j in range(n):
                val = mat[i, j]
                color = "white" if val < thresh else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=7, color=color)

        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cb.ax.tick_params(colors="white", labelsize=8)
        cb.outline.set_edgecolor("white")
        cb.outline.set_alpha(0.4)

        fig.set_facecolor("#3c3f41")
        fig.tight_layout()
        canvas.draw()
        canvas.parentWidget().setVisible(True)

    def _get_behaviour_colours(self, labels):
        """Look up actual behaviour colours from the GUI data model."""
        colours = []
        for label in labels:
            found = False
            for an in self.gui_data_interface.animals.values():
                for behav in an.behaviours.values():
                    full_label = "{} : {}".format(an.name, behav.name)
                    if full_label == label and behav.color:
                        colours.append(behav.color)
                        found = True
                        break
                if found:
                    break
            if not found:
                colours.append(_PALETTE[len(colours) % len(_PALETTE)])
        return colours

    # ──────────────────────────────────────────────────────────────
    #  Export
    # ──────────────────────────────────────────────────────────────
    def _export(self, plot_title: str, fmt: str):
        if self._result is None:
            QMessageBox.warning(self, "No data",
                                "Run the analysis first.", QMessageBox.Ok)
            return

        # choose file
        ext_map = {"CSV": "*.csv", "PNG": "*.png", "SVG": "*.svg"}
        filt = ext_map.get(fmt, "*.*")
        path, selected_filt = QFileDialog.getSaveFileName(
            self, f"Export {plot_title} as {fmt}", "", filt)
        if not path:
            return
        path = _ensure_extension(path, selected_filt)

        try:
            if fmt == "CSV":
                self._export_csv(plot_title, path)
            elif fmt in ("PNG", "SVG"):
                self._export_figure(plot_title, path, fmt.lower())
            QMessageBox.information(
                self, "Export complete",
                f"Saved to:\n{path}", QMessageBox.Ok)
        except Exception as exc:
            QMessageBox.critical(
                self, "Export failed",
                f"Could not export:\n{exc}", QMessageBox.Ok)

    def _export_csv(self, plot_title: str, path: str):
        if "Timeline" in plot_title or "Ethogram" in plot_title:
            # Export raw binary ethogram as CSV
            if self._result is not None and self._result.raw_data is not None:
                import pandas as _pd
                df = _pd.DataFrame(self._result.raw_data,
                                   columns=self._result.labels)
                df.insert(0, 'frame', range(len(df)))
                df.insert(1, 'time_s', df['frame'] / self._result.fps)
                df.to_csv(path, index=False)
        elif "Percentage" in plot_title:
            df = stats_to_dataframe(self._result)
            df.to_csv(path, index=False)
        elif "Bout" in plot_title:
            df = stats_to_dataframe(self._result)
            df.to_csv(path, index=False)
        elif "Transition" in plot_title:
            df = transition_matrix_to_dataframe(self._result)
            df.to_csv(path)
        else:
            df = stats_to_dataframe(self._result)
            df.to_csv(path, index=False)

    def _export_figure(self, plot_title: str, path: str, fmt: str):
        fig = self._get_fig_for_title(plot_title)
        fig.savefig(path, format=fmt, dpi=200, transparent=False,
                    facecolor="#3c3f41", edgecolor="none",
                    bbox_inches="tight")

    def _get_fig_for_title(self, title: str) -> Figure:
        if "Timeline" in title or "Ethogram" in title:
            if self._raster_fig is not None:
                return self._raster_fig
            return self._fig_pct
        elif "Percentage" in title:
            return self._fig_pct
        elif "Bout" in title:
            return self._fig_bout
        elif "Transition" in title or "Transitions" in title:
            # Check per-animal groups first
            for fig, ax, canvas, grp in self._per_animal_groups:
                if grp.title() and grp.title() in title:
                    return fig
            return self._fig_trans
        return self._fig_pct

    # ──────────────────────────────────────────────────────────────
    #  Qt overrides
    # ──────────────────────────────────────────────────────────────
    def resizeEvent(self, event):
        pass


def _short(label: str) -> str:
    """'animal_0 : aggression' → 'A0: aggression'"""
    if " : " in label:
        parts = label.split(" : ", 1)
        animal = parts[0].strip()
        behav = parts[1].strip()
        # try to abbreviate 'animal_0' → 'A0'
        for prefix in ("animal_", "Animal_", "animal ", "Animal "):
            if animal.startswith(prefix):
                animal = "A" + animal[len(prefix):]
                break
        return f"{animal}: {behav}"
    return label


def _split_label(label: str):
    """Split 'animal_0 : aggression' → ('animal_0', 'aggression')."""
    if " : " in label:
        parts = label.split(" : ", 1)
        return parts[0].strip(), parts[1].strip()
    return "unknown", label.strip()
