from typing import Dict, List, Any, Callable, Union, Tuple

from pyvisor.GUI.model.animal import Animal
from pyvisor.GUI.model.behaviour import Behaviour
from .callback_handler import CallbackHandler
from .movie_bindings import MovieBindings
from .scorer_action import ScorerAction
from ...ManualEthologyScorer import ManualEthologyScorer


class GUIDataInterface:

    def __init__(self):
        self.movie_bindings = MovieBindings()
        self.animals = {}  # type: Dict[int, Animal]
        self.callbacks_animal_added = CallbackHandler()
        self.callbacks_animal_name_changed = CallbackHandler()
        self.callbacks_behaviour_added = CallbackHandler()
        self.callbacks_behaviour_name_changed = CallbackHandler()
        self.callbacks_behaviour_color_changed = CallbackHandler()
        self.callbacks_behaviour_removed = CallbackHandler()
        self.callbacks_key_binding_changed = CallbackHandler()
        self.callbacks_update_icon = CallbackHandler()
        self.callbacks_compatibility_changed = CallbackHandler()
        self.selected_device = None  # type: Union[str, None]
        self.manual_scorer = ManualEthologyScorer()

    def add_animal(self, name: str, number: int) -> Animal:
        new_animal = Animal(number, name)
        self.animals[number] = new_animal
        self._update_UIs_add_animal(new_animal)
        return new_animal

    def change_animal_name(self, animal: Animal, new_name: str):
        animal.name = new_name
        for callback in self.callbacks_animal_name_changed:
            callback(animal)

    def get_savable_list(self) -> List[Dict[str, Any]]:
        savable_list = [
            self.animals[number].to_savable_dict() for
            number in self.animals
        ]
        return savable_list

    def get_savable_dict(self) -> Dict[str, Any]:
        d = {
            "animals": self.get_savable_list(),
            "selected_device": self.selected_device,
            "movie_bindings": self.movie_bindings.to_dict()
        }
        return d

    def _update_UIs_add_animal(self, new_animal):
        for callback in self.callbacks_animal_added:
            callback(new_animal)

    def register_callback_animal_added(
            self,
            callback: Callable[[Animal], None]
    ) -> int:
        id_ = self.callbacks_animal_added.register(callback)
        return id_

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
        for callback in self.callbacks_update_icon:
            callback(behaviour)

    def set_icon_color(self, behaviour: Behaviour, color: str):
        behaviour.color = color
        for callback in self.callbacks_behaviour_color_changed:
            callback(behaviour)

    def get_action_assigned_to(
            self, button_identifier
    ) -> Union[Tuple[Behaviour, bool], Tuple[None, bool]]:
        assigned = None
        is_behaviour = False
        for an in self.animals:
            animal = self.animals[an]
            assigned_an = animal.get_behaviour_assigned_to(
                self.selected_device, button_identifier
            )
            if assigned_an is None:
                continue
            if assigned is not None:
                raise RuntimeError(
                    "Key {} is assigned to multiple behaviours.".format(
                        button_identifier
                    )
                )
            assigned = assigned_an
            is_behaviour = True
        assigned_movie_action = self.movie_bindings.get_action_assigned_to(
            self.selected_device, button_identifier)
        if assigned_movie_action is not None:
            if assigned is not None:
                raise RuntimeError(
                    "Key {} is assigned to multiple behaviours/movie actions.".format(
                        button_identifier
                    )
                )
        return assigned, is_behaviour

    def change_button_binding(
            self,
            action: ScorerAction,
            button_identifier: Union[str, None],
            is_behaviour: bool
    ):
        action.key_bindings[self.selected_device] = button_identifier
        self._update_UIs_key_binding(action, is_behaviour)

    def _update_UIs_key_binding(self, action: ScorerAction, is_behaviour: bool):
        for callback in self.callbacks_key_binding_changed:
            callback(action, is_behaviour)

    def register_callback_key_binding_changed(
            self,
            callback: Callable[[ScorerAction, bool], None]
    ) -> int:
        id_ = self.callbacks_key_binding_changed.register(callback)
        return id_

    def reset_all_bindings(self):
        for a in self.animals.keys():
            animal = self.animals[a]
            for behav in animal.behaviours.values():
                self.change_button_binding(behav, None,
                                           is_behaviour=True)
        for action in self.movie_bindings.scorer_actions.values():
            self.change_button_binding(action, None,
                                       is_behaviour=False)

    def register_callback_compatibility_changed(
            self,
            callback: Callable[[Behaviour, Behaviour], None]):
        id_ = self.callbacks_compatibility_changed.register(callback)
        return id_

    def set_compatibility(self, behav1: Behaviour, behav2: Behaviour, state: bool):
        print('{} <-> {}: {}'.format(behav1.name, behav2.name, state))
        print(behav1.compatible_with)
        if state:
            behav1.compatible_with.append(behav2.name)
            behav2.compatible_with.append(behav1.name)
        else:
            idx1 = behav1.compatible_with.index(behav2.name)
            behav1.compatible_with.pop(idx1)
            idx2 = behav2.compatible_with.index(behav1.name)
            behav2.compatible_with.pop(idx2)
        for cb in self.callbacks_compatibility_changed:
            cb(behav1, behav2)

    def add_behaviour(self, animal: Animal, behav: Behaviour):
        animal[behav.label] = behav
        for cb in self.callbacks_behaviour_added:
            cb(animal, behav)

    def register_callback_behaviour_added(self, callback: Callable[[Animal, Behaviour], None]):
        self.callbacks_behaviour_added.register(callback)

    def change_behaviour_name(self, behaviour: Behaviour, name: str):
        if name == behaviour.name:
            raise NameIdenticalException
        animal = self.animals[behaviour.animal_number]
        if animal.behaviour_with_name_exists(name):
            raise NameExistsException
        animal.rename_behaviour(behaviour, name)
        for callback in self.callbacks_behaviour_name_changed:
            callback(behaviour)

    def remove_behaviour(self, behaviour: Behaviour):
        animal = self.animals[behaviour.animal_number]
        print(animal.behaviours.keys())
        animal.remove_behaviour(behaviour)
        callbacks = self.callbacks_behaviour_removed.callback_functions.copy()
        for callback in callbacks.values():
            callback(behaviour)


class NameExistsException(RuntimeError):
    pass


class NameIdenticalException(RuntimeError):
    pass
