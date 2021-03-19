from typing import Dict, List, Any, Union

from pyvisor.GUI.model.behaviour import Behaviour


class Animal:

    def __init__(self, number: int, name: str):
        self.number = number
        self.name = name
        self.behaviours = dict()  # type: Dict[str, Behaviour]

    def get_button_assignments(
            self,
            selected_device: str
    ) -> Dict[str, Behaviour]:
        button_assignments = {}
        for label in self.behaviours:
            behaviour = self.behaviours[label]
            binding = behaviour.key_bindings[selected_device]
            if binding is None:
                continue
            button_assignments[binding] = behaviour
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
            s += "{}: {}\n".format(key, self.behaviours[key].key_bindings)
        return s

    def __repr__(self):
        return self.__str__()

    def key_is_assigned(self, button_identifier) -> bool:
        for binding in self.behaviours.values():
            if binding.key_bindings == button_identifier:
                return True
        return False

    def to_savable_dict(self) -> Dict[str, Any]:
        d = {
            "animal_number": self.number,
            "animal_name": self.name,
            "behaviours": [self.behaviours[key].to_dict() for key in sorted(self.behaviours.keys())]
        }
        return d

    @staticmethod
    def from_json_dict(json_dict: Dict[str, Any]) -> 'Animal':
        new_animal = Animal(json_dict['animal_number'], json_dict['animal_name'])
        behaviours = [Behaviour.from_dict(d) for d in json_dict['behaviours']]
        for b in behaviours:
            new_animal[b.label] = b
        return new_animal

    def get_unique_name(self) -> str:
        for index in range(100):
            candidate = 'behaviour_{}'.format(index)
            if self._name_is_unique(candidate):
                return candidate
        raise RuntimeError("No unique name found.")

    def _name_is_unique(self, candidate: str) -> bool:
        for label in self.behaviours:
            behav = self.behaviours[label]
            if behav.name == candidate:
                return False
        return True

    def has_behaviour(self, name: str) -> bool:
        for behav in self.behaviours.values():
            if behav.name == name:
                return True
        return False

    def get_behaviour_assigned_to(
            self, selected_device,
            button_identifier
    ) -> Union[Behaviour, None]:
        for behav in self.behaviours.values():
            binding = behav.key_bindings[selected_device]
            if binding is None:
                continue
            if binding == button_identifier:
                return behav

