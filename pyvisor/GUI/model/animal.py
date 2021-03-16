from typing import Dict, List

from pyvisor.GUI.model.behaviours import Behaviour


class Animal:
    ANIMAL_MOVIE = -1

    def __init__(self, number: int):
        self.number = number
        self.behaviours = dict()

    def get_button_assignments(self) -> Dict[str, Behaviour]:
        button_assignments = {}
        for label in self.behaviours:
            binding = self.behaviours[label]
            button = binding.keyBinding
            if button is None:
                continue
            button_assignments[button] = binding
        return button_assignments

    def all_actions_have_buttons_assigned(self, animal_behaviours: List[str], movie_commands: List[str]) -> bool:
        for ab in animal_behaviours:
            if ab not in self:
                return False
        for mc in movie_commands:
            if mc not in self:
                return False
        return True

    @staticmethod
    def from_key_assignment_dictionary(key_assignments: Dict[str, Behaviour]) -> 'Animal':
        b0 = list(key_assignments.values())[0]
        new_animal = Animal(b0.animal)
        for key in key_assignments:
            binding = key_assignments[key]
            new_animal[binding.label] = binding
        return new_animal

    def keys(self):
        return self.behaviours.keys()

    def items(self):
        return self.behaviours.items()

    def __contains__(self, item: str):
        for key in self.behaviours.keys():
            if key == item:
                return True
        return False

    def __setitem__(self, key: str, value: Behaviour):
        if key != value.label:
            raise ValueError("label {} does not match binding label {}".format(key, value.label))
        self.behaviours[key] = value

    def __getitem__(self, item: str) -> Behaviour:
        return self.behaviours[item]

    def __delitem__(self, key):
        del self.behaviours[key]

    def __str__(self):
        s = ""
        for key in self.behaviours:
            s += "{}: {}\n".format(key, self.behaviours[key].keyBinding)
        return s

    def __repr__(self):
        return self.__str__()

    def key_is_assigned(self, button_identifier) -> bool:
        for binding in self.behaviours.values():
            if binding.keyBinding == button_identifier:
                return True
        return False

    @staticmethod
    def from_json(a):
        raise NotImplementedError
