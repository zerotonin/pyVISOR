from typing import List, Tuple, Set

import pandas as pd
import numpy as np

from .GUI.model.animal import Animal
from .GUI.model.behaviour import BehaviourName


class AnimalEthogram2:

    def __init__(self, animal: Animal, n_frames: int):
        self._animal = animal
        self._table = pd.DataFrame(
            np.zeros((n_frames, len(animal.behaviours)), dtype=bool),
            index=range(n_frames),
            columns=sorted([b.name for b in animal.behaviours.values()])
        )
        self._icons = {
            behav.name: behav.icon for behav in self._animal.behaviours.values()
        }

    def assign_behaviours(self, frame: int, behav_labels: List[str]):
        if not self._behaviours_are_compatible(behav_labels):
            raise RuntimeError("Behaviours are not compatible: {}".format(behav_labels))
        self._table.loc[frame, behav_labels] = [True] * len(behav_labels)
        if self._table.loc[frame].sum() == len(behav_labels):
            return
        for label in self._table.columns.names:
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
