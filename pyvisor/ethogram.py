from threading import RLock
from typing import Dict, List

from pyvisor.GUI.model.animal import Animal, AnimalNumber
from pyvisor.GUI.model.behaviour import BehaviourName, Behaviour
from pyvisor.animal_ethogram_2 import AnimalEthogram2


class Ethogram:

    def __init__(self, animals: Dict[AnimalNumber, Animal], n_frames: int, lock: RLock = None):
        self._animals = animals
        self.animal_ethograms = {
            an: AnimalEthogram2(animals[an], n_frames) for an in animals.keys()
        }  # type: Dict[AnimalNumber, AnimalEthogram2]

        self.current_states = {
            an: [] for an in animals.keys()
        }  # type: Dict[AnimalNumber, List[BehaviourName]]
        self._lock = lock or RLock()

    def toggle_state(self, label: str):
        with self._lock:
            animal_number, behaviour_name = Behaviour.parse_label(label)
            animal = self._animals[animal_number]
            states = self.current_states[animal_number]
            if label in states:
                states.pop(states.index(label))
                print('states:', states)
                return
            behav = animal.behaviours[label]
            _to_pop = []
            for other in states:
                _, other_name = Behaviour.parse_label(other)
                if other_name in behav.compatible_with:
                    continue
                _to_pop.append(states.index(other))
            _to_pop.reverse()
            for idx in _to_pop:
                states.pop(idx)
            states.append(label)
            print('states:', states)


    def clear_states(self):
        with self._lock:
            for states in self.current_states.values():
                states.clear()

    def apply_states_at_frame(self, frame_number: int):
        with self._lock:
            for an in self.current_states:
                states = list(self.current_states[an])
                animal = self._animals[an]
                animal_etho = self.animal_ethograms[an]
                if 'A{}_delete'.format(animal.number) in states:
                    animal_etho.delete_behaviours(frame_number)
                    continue
                animal_etho.assign_behaviours(frame_number, states)

    @property
    def lock(self) -> RLock:
        return self._lock
