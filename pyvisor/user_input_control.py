from typing import Dict, Callable

from .GUI.model.animal import AnimalNumber, Animal
from .GUI.model.movie_bindings import MovieBindings
from .MediaHandler import MediaHandler
from .ethogram import Ethogram


class UserInputControl2:

    def __init__(self, animals: Dict[AnimalNumber, Animal],
                 movie_bindings: MovieBindings,
                 selected_device: str,
                 movie: MediaHandler,
                 ethogram: Ethogram):
        self.movie = movie
        self.ethogram = ethogram
        self._map_button_to_action = {}  # type: Dict[str, Callable[[int], None]]

        self._init_animal_buttons(animals, selected_device)
        self._init_movie_buttons(movie_bindings, selected_device)

    def _init_animal_buttons(self, animals: Dict[AnimalNumber, Animal],
                             selected_device: str):
        for an in animals:
            animal = animals[an]
            for label in animal.behaviours:
                behav = animal.behaviours[label]
                self._map_button_to_action[
                    behav.key_bindings[selected_device]
                ] = _ToggleStateCaller(self.ethogram, label)

    def _init_movie_buttons(self, movie_bindings: MovieBindings, selected_device: str):
        self._map_button_to_action.update({
            movie_bindings["toggleRunMov"].key_bindings[selected_device]:
                self.movie.toggle_play,
            movie_bindings["stopToggle"].key_bindings[selected_device]:
                self._stop_and_reset,
            movie_bindings["runMovForward"].key_bindings[selected_device]:
                self.movie.set_run_forward,
            movie_bindings["runMovReverse"].key_bindings[selected_device]:
                self.movie.set_run_reverse,
            movie_bindings["changeFPShigh"].key_bindings[selected_device]:
                self.movie.increase_fps,
            movie_bindings["changeFPSlow"].key_bindings[selected_device]:
                self.movie.decrease_fps,
            movie_bindings["changeFrameNoHigh1"].key_bindings[selected_device]:
                lambda: self.movie.set_current_frame_delta(1),
            movie_bindings["changeFrameNoLow1"].key_bindings[selected_device]:
                lambda: self.movie.set_current_frame_delta(-1),
            movie_bindings["changeFrameNoHigh10"].key_bindings[selected_device]:
                lambda: self.movie.set_current_frame_delta(10),
            movie_bindings["changeFrameNoLow10"].key_bindings[selected_device]:
                lambda: self.movie.set_current_frame_delta(-10)

        })

    def _stop_and_reset(self):
        self.movie.set_stop()
        self.ethogram.clear_states()

    def handle_input(self, input_code: str):
        if input_code not in self._map_button_to_action:
            return
        self._map_button_to_action[input_code]()


class _ToggleStateCaller:

    def __init__(self, ethogram: Ethogram, label: str):
        self._ethogram = ethogram
        self._label = label

    def __call__(self):
        self._ethogram.toggle_state(self._label)
