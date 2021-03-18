from typing import Dict, List, Any, Callable

from pyvisor.GUI.model.animal import Animal
from pyvisor.GUI.model.behaviour import Behaviour


class AnimalHandler:

    def __init__(self):
        self._UI_callbacks_update_icon = []
        self.animals = {}  # type: Dict[int, Animal]
        self._UI_callbacks_animal_added = []
        self._UI_callbacks_name_changed = []

    def add_animal(self, name: str, number: int) -> Animal:
        new_animal = Animal(number, name)
        self.animals[number] = new_animal
        self._update_UIs_add_animal(new_animal)
        return new_animal

    def change_animal_name(self, animal: Animal, new_name: str):
        animal.name = new_name
        self._update_UIs_name_changed(animal)

    def get_savable_list(self) -> List[Dict[str, Any]]:
        savable_list = [
            self.animals[number].to_savable_dict() for
            number in self.animals
        ]
        return savable_list

    def _update_UIs_add_animal(self, new_animal):
        for callback in self._UI_callbacks_animal_added:
            callback(new_animal)

    def register_callback_animal_added(self,
                                       callback: Callable[[Animal], None]):
        self._UI_callbacks_animal_added.append(callback)

    def get_button_assignments(
            self,
            selected_device: str
    ) -> Dict[str, Behaviour]:
        assignments = {}
        for a_number in self.animals:
            a = self.animals[a_number]
            assignments.update(
                a.get_button_assignments(selected_device)
            )
        return assignments

    def set_icon(self, behaviour: Behaviour, icon_path):
        behaviour.icon_path = icon_path
        self._update_UIs_icon(behaviour)

    def _update_UIs_icon(self, behaviour: Behaviour):
        for callback in self._UI_callbacks_update_icon:
            callback(behaviour)

    def _update_UIs_name_changed(self, animal):
        for callback in self._UI_callbacks_name_changed:
            callback(animal)

    def set_icon_color(self, behaviour: Behaviour, color: str):
        behaviour.color = color
        self._update_UIs_icon(behaviour)


