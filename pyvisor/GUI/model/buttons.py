from dataclasses import dataclass
from typing import Dict, List

from pyvisor.GUI.behavBinding import BehavBinding


class BehaviourAssignments:

    def __init__(self):
        self.assignments = dict()

    def get_button_assignments(self) -> Dict[str, BehavBinding]:
        button_assignments = {}
        for label in self.assignments:
            binding = self.assignments[label]
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
    def from_key_assignment_dictionary(key_assignments: Dict[str, BehavBinding]) -> 'BehaviourAssignments':
        new_behav_assignments = BehaviourAssignments()
        for key in key_assignments:
            binding = key_assignments[key]
            new_behav_assignments[binding.label] = binding
        return new_behav_assignments

    def keys(self):
        return self.assignments.keys()

    def items(self):
        return self.assignments.items()

    def __contains__(self, item: str):
        for key in self.assignments.keys():
            if key == item:
                return True
        return False

    def __setitem__(self, key: str, value: BehavBinding):
        if key != value.label:
            raise ValueError("label {} does not match binding label {}".format(key, value.label))
        self.assignments[key] = value

    def __getitem__(self, item: str) -> BehavBinding:
        return self.assignments[item]

    def __delitem__(self, key):
        del self.assignments[key]

    def __str__(self):
        s = ""
        for key in self.assignments:
            s += "{}: {}\n".format(key, self.assignments[key].keyBinding)
        return s

    def __repr__(self):
        return self.__str__()

    def key_is_assigned(self, button_identifier) -> bool:
        for binding in self.assignments.values():
            if binding.keyBinding == button_identifier:
                return True
        return False
