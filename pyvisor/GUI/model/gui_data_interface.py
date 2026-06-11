import json
from typing import Dict, List, Any, Callable, Union, Tuple

from pyvisor.GUI.model.animal import Animal
from pyvisor.GUI.model.behaviour import Behaviour
from .callback_handler import CallbackHandler
from .movie_bindings import MovieBindings
from .scorer_action import ScorerAction
from ...paths import ensure_autosave_dir, settings_path


class GUIDataInterface:
    """Central data model shared across all GUI tabs.

    Holds the animal/behaviour definitions, device selection,
    movie bindings, autosave settings, and the active scorer
    instance. Provides callback hooks so UI widgets can react
    to model changes.
    """

    def __init__(self):
        self.movie_bindings = MovieBindings()
        self.animals = {}  # type: Dict[int, Animal]
        self.callbacks_animal_added = CallbackHandler()
        self.callbacks_animal_name_changed = CallbackHandler()
        self.callbacks_animal_removed = CallbackHandler()
        self.callbacks_behaviour_added = CallbackHandler()
        self.callbacks_behaviour_name_changed = CallbackHandler()
        self.callbacks_behaviour_color_changed = CallbackHandler()
        self.callbacks_behaviour_removed = CallbackHandler()
        self.callbacks_key_binding_changed = CallbackHandler()
        self.callbacks_update_icon = CallbackHandler()
        self.callbacks_compatibility_changed = CallbackHandler()
        self.selected_device = None  # type: Union[str, None]
        self.manual_scorer = None  # type: Union[None, ManualEthologyScorer2]
        self.autosave_settings = {
            "enabled": True,
            "interval_seconds": 300,
            "directory": str(ensure_autosave_dir())
        }
        self.overlay_settings = {
            "dark_font": False,
            "font_size": 15
        }

    def clear_all_callbacks(self):
        self.callbacks_animal_added.clear()
        self.callbacks_animal_name_changed.clear()
        self.callbacks_animal_removed.clear()
        self.callbacks_behaviour_added.clear()
        self.callbacks_behaviour_name_changed.clear()
        self.callbacks_behaviour_color_changed.clear()
        self.callbacks_behaviour_removed.clear()
        self.callbacks_key_binding_changed.clear()
        self.callbacks_update_icon.clear()
        self.callbacks_compatibility_changed.clear()

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
            "movie_bindings": self.movie_bindings.to_dict(),
            "autosave": self.autosave_settings,
            "overlay": self.overlay_settings
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
        """Find the first action bound to *button_identifier*.

        Returns ``(action, is_behaviour)`` or ``(None, False)``.
        """
        for an in self.animals.values():
            hit = an.get_behaviour_assigned_to(
                self.selected_device, button_identifier)
            if hit is not None:
                return hit, True

        hit = self.movie_bindings.get_action_assigned_to(
            self.selected_device, button_identifier)
        if hit is not None:
            return hit, False

        return None, False

    def steal_button(self, button_identifier: str):
        """Clear *button_identifier* from every behaviour and movie action.

        Called before assigning the button to a new action so that no
        duplicates remain.
        """
        device = self.selected_device
        # clear from all behaviours across all animals
        for animal in self.animals.values():
            for behav in animal.behaviours.values():
                if behav.key_bindings[device] == button_identifier:
                    behav.key_bindings[device] = None
                    self._update_UIs_key_binding(behav, True)
        # clear from all movie actions
        for name in self.movie_bindings.keys():
            action = self.movie_bindings[name]
            if action.key_bindings[device] == button_identifier:
                action.key_bindings[device] = None
                self._update_UIs_key_binding(action, False)

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

    def remove_animal(self, animal):
        self.animals.pop(animal.number)
        for callback in self.callbacks_animal_removed:
            callback(animal)

    def get_behaviours_without_icons(self) -> List[Behaviour]:
        items = []
        for an in sorted(self.animals.keys()):
            animal = self.animals[an]
            items += animal.get_behaviours_without_icons()
        return items

    def get_scorer_actions_without_buttons_assigned(self) -> List[ScorerAction]:
        items = []
        for an in sorted(self.animals.keys()):
            animal = self.animals[an]
            items += animal.get_behaviours_without_buttons_assigned(self.selected_device)
        items += self.movie_bindings.get_actions_without_buttons_assigned(self.selected_device)
        return items

    def save_state(self):
        state_dict = self.get_savable_dict()
        settings_file = settings_path('guidefaults_animals.json')
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        with settings_file.open('wt') as fh:
            json.dump(state_dict, fh)


class NameExistsException(RuntimeError):
    pass


class NameIdenticalException(RuntimeError):
    pass
