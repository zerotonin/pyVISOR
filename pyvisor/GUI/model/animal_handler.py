from typing import Dict, List, Any, Callable

from pyvisor.GUI.model.animal import Animal


class AnimalHandler:

    def __init__(self):
        self.animals = {}  # type: Dict[int, Animal]
        self._UI_callbacks_animal_added = []
        self._UI_callbacks_name_changed = []

    def add_animal(self, name: str, number: int) -> Animal:
        new_animal = Animal(number, name)
        self.animals[number] = new_animal
        self._update_UIs_add_animal(new_animal)
        return new_animal

    def change_animal_name(self, animal: Animal, new_name: str):
        raise NotImplementedError
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
