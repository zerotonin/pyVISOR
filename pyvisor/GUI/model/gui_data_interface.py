from typing import Dict, List, Any, Callable, Union, Tuple

from pyvisor.GUI.model.animal import Animal
from pyvisor.GUI.model.behaviour import Behaviour
from .movie_bindings import MovieBindings
from .scorer_action import ScorerAction
from ...ManualEthologyScorer import ManualEthologyScorer


class GUIDataInterface:

    def __init__(self):
        self.movie_bindings = MovieBindings()
        self.animals = {}  # type: Dict[int, Animal]
        self._UI_callbacks_animal_added = []
        self._UI_callbacks_name_changed = []
        self._UI_callbacks_key_binding_changed = []
        self._UI_callbacks_update_icon = []
        self.selected_device = None  # type: Union[str, None]
        self.manual_scorer = ManualEthologyScorer()

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

    def get_savable_dict(self) -> Dict[str, Any]:
        d = {
            "animals": self.get_savable_list(),
            "selected_device": self.selected_device,
            "movie_bindings": self.movie_bindings.to_dict()
        }
        return d

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
        for callback in self._UI_callbacks_key_binding_changed:
            callback(action, is_behaviour)

    def register_callback_key_binding_changed(
            self,
            callback: Callable[[ScorerAction, bool], None]
    ):
        self._UI_callbacks_key_binding_changed.append(callback)
