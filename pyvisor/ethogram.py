from typing import Dict, List

from pyvisor.GUI.model.animal import Animal, AnimalNumber
from pyvisor.GUI.model.behaviour import BehaviourName
from pyvisor.animal_ethogram_2 import AnimalEthogram2


class Ethogram:

    def __init__(self, animals: Dict[AnimalNumber, Animal], n_frames: int):
        self.animal_ethograms = {
            an: AnimalEthogram2(animals[an], n_frames) for an in animals.keys()
        }  # type: Dict[AnimalNumber, AnimalEthogram2]

        self.current_states = {
            an: [] for an in animals.keys()
        }  # type: Dict[AnimalNumber, List[BehaviourName]]

    def assign_state(self, frame: int, label: str):
        print("assign_state not implemented yet")
