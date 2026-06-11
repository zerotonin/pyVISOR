from typing import List

import pandas as pd
import numpy as np

from .GUI.model.animal import Animal
from .GUI.model.behaviour import BehaviourName


class AnimalEthogram2:
    """Frame-level ethogram for a single animal.

    Stores a boolean DataFrame where each column is a behaviour
    and each row is a video frame. Provides methods to assign,
    delete, and query behaviour states at individual frames.
    """

    def __init__(self, animal: Animal, n_frames: int):
        self._animal = animal
        self._table = pd.DataFrame(
            np.zeros((n_frames, len(animal.behaviours)), dtype=bool),
            index=range(n_frames),
            columns=sorted([b.label for b in animal.behaviours.values()])
        )
        self._icons = {
            behav.label: behav.icon for behav in self._animal.behaviours.values()
        }

    def assign_behaviours(self, frame: int, behav_labels: List[str]):
        if not self._behaviours_are_compatible(behav_labels):
            # Incompatible — skip silently rather than crashing the scorer
            return
        self._table.loc[frame, behav_labels] = [True] * len(behav_labels)
        if self._table.loc[frame].sum() == len(behav_labels):
            return
        for label in self._table.columns:
            if not self._behaviours_are_compatible(behav_labels + [label]):
                self._table.loc[frame, label] = False

    def get_icons(self, behaviours: List[BehaviourName]):
        return [self._icons[name] for name in behaviours]


    def _behaviours_are_compatible(self, behav_labels: List[str]) -> bool:
        for this_label in behav_labels:
            this_behav = self._animal.behaviours[this_label]
            for other_label in behav_labels:
                if this_label == other_label:
                    continue
                other_behav = self._animal.behaviours[other_label]
                if this_behav.name not in other_behav.compatible_with:
                    return False
                if other_behav.name not in this_behav.compatible_with:
                    return False
        return True

    def delete_behaviours(self, frame_number: int):
        self._table.loc[frame_number] = [False] * len(self._table.columns)

    def get_active_labels_at_frame(self, frame: int) -> List[str]:
        """Return list of behaviour labels that are True at *frame*."""
        if frame < 0 or frame >= len(self._table):
            return []
        row = self._table.iloc[frame]
        return [col for col in self._table.columns if row[col]]

    def to_numpy(self) -> np.ndarray:
        return self._table.to_numpy(dtype=int, copy=True)

    def get_formatted_behaviour_labels(self) -> List[str]:
        labels: List[str] = []
        for label in self._table.columns:
            behav = self._animal.behaviours[label]
            labels.append(f"{self._animal.name} : {behav.name}")
        return labels
