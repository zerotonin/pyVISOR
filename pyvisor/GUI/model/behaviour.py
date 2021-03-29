from typing import Dict, Any, List

import numpy as np

from pyvisor.GUI.model.key_bindings import KeyBindings
from .scorer_action import ScorerAction
from ...icon import Icon

BehaviourName = str


class Behaviour(ScorerAction):

    ANIMAL_MOVIE = -1

    def __init__(self, animal_number: int = None, color: str = '#C0C0C0',
                 icon_path: str = None, name: str = None,
                 compatible_with: List[str] = None):

        super().__init__(name, icon_path)
        self.animal_number = animal_number
        self.color = color
        if compatible_with is None:
            compatible_with = []
        self.compatible_with = compatible_with

    def set_key_binding(self, device: str, binding: str):
        if device == "X-Box":
            self.key_bindings.xbox = binding
        elif device == "Playstation":
            self.key_bindings.playstation = binding
        elif device == "Keyboard":
            self.key_bindings.keyboard = binding
        elif device == "Free":
            self.key_bindings.free = binding
        else:
            msg = ("Device '{}' unknown. Options are "
                   "X-Box, Playstation, Keyboard, Free.")
            raise KeyError(msg.format(device))

    @property
    def icon(self):
        icon = Icon(color=self.color)
        icon.readImage(self.icon_path)
        icon.decall2icon()
        return icon.icon2pygame()

    @property
    def label(self) -> str:
        if self.animal_number == self.ANIMAL_MOVIE:
            return "movie_{}".format(self.name)
        return "A{}_{}".format(self.animal_number, self.name)

    @property
    def is_movie(self) -> bool:
        return self.animal_number == self.ANIMAL_MOVIE

    def __str__(self):
        s = 'BehavBinding:\n'
        for lbl, attr in zip(
                ['animal', 'Icon', 'behaviour'],
                [self.animal_number, self.icon_path, self.name]
        ):
            s += f'  {lbl}: {attr}\n'
        return s

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> Dict[str, Any]:
        d = {
            'key_bindings': self.key_bindings.to_dict(),
            'animal': self.animal_number,
            'name': self.name,
            'icon_path': self.icon_path,
            'color': self.color,
            'compatible_with': self.compatible_with
        }
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Behaviour":
        behav = Behaviour(
            d['animal'],
            d['color'],
            d['icon_path'],
            d['name'],
            d['compatible_with']
        )
        behav.key_bindings = KeyBindings.from_dict(d['key_bindings'])
        return behav

    @staticmethod
    def from_object_dict_to_savable_dict(bindings: Dict[str, "Behaviour"]) -> Dict[str, Any]:
        d = {}
        for key in bindings:
            if key in d:
                raise ValueError(f"Button '{key}' is already in dict. Make sure buttons are uniquely assigned!")
            d[key] = bindings[key].to_dict()
        return d

    @staticmethod
    def from_savable_dict_to_dict_of_objects(plain_dict: Dict[str, Dict[str, Any]]) -> Dict[str, 'Behaviour']:
        d = {}
        for key in plain_dict:
            if key in d:
                raise ValueError(f"Button '{key}' is already in dict. Make sure buttons are uniquely assigned!")
            binding = Behaviour.from_dict(plain_dict[key])
            d[binding.label] = binding
        return d


