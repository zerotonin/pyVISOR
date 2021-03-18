from typing import Dict, Any

from pyvisor.GUI.model.key_bindings import KeyBindings


class Behaviour:

    ANIMAL_MOVIE = -1

    def __init__(self,
                 animal: int = None,
                 color: str = '#C0C0C0',
                 icon_path: str = None,
                 name: str = None):

        self.animal = animal
        self.icon_path = icon_path
        self.name = name
        self.color = color
        self.key_bindings = KeyBindings()

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
    def label(self) -> str:
        if self.animal == self.ANIMAL_MOVIE:
            return "movie_{}".format(self.name)
        return "A{}_{}".format(self.animal, self.name)

    @property
    def is_movie(self) -> bool:
        return self.animal == self.ANIMAL_MOVIE

    def __str__(self):
        s = 'BehavBinding:\n'
        for lbl, attr in zip(
                ['animal', 'icon', 'behaviour'],
                [self.animal, self.icon_path, self.name]
        ):
            s += f'  {lbl}: {attr}\n'
        return s

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> Dict[str, Any]:
        d = {
            'key': self.key_bindings,
            'animal': self.animal,
            'behaviour': self.name,
            'icon_path': self.icon_path,
            'color': self.color,
            'device': self.device,
        }
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Behaviour":
        if len(d) != 6:
            msg = "Can't generate BehavBinding from dict. Dict needs to have exactly 6 keys: 'animal', 'color', "
            msg += "'icon_path', 'behaviour', 'key', 'device'.\n"
            msg += "Your dictionary:\n"
            msg += str(d)
            raise ValueError(msg)
        return Behaviour(
            d['animal'],
            d['color'],
            d['icon_path'],
            d['behaviour'],
            d['key'],
            d['device']
        )

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


