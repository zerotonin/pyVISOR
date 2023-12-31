from typing import Tuple, Dict

from PyQt5.QtWidgets import QTabWidget, QWidget

import os
from .single_animal_tab import SingleAnimalTab
from ..model.animal import Animal
from ..model.gui_data_interface import GUIDataInterface

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


class AnimalTab(QTabWidget):

    def __init__(self, parent: QWidget, gui_data_interface: GUIDataInterface):
        super(AnimalTab, self).__init__(parent)
        self.gui_data_interface = gui_data_interface
        self.animals = gui_data_interface.animals
        self.tabs_ = {}  # type: Dict[int, SingleAnimalTab]
        self._block_add = False
        self.init_UI()

    def init_UI(self):
        if self.animals:
            for number in sorted(self.animals.keys()):
                animal = self.animals[number]
                self.create_new_tab(animal)
        else:
            self.add_tab(-1)

        ## Add a '+' tab, creating a new tab when pressed.
        # Inspired by user Garjy from stackoverflow.com 
        # (full URL: http://stackoverflow.com/questions/19975137/how-can-i-add-a-new-tab-button-next-to-the-tabs-of-a-qmdiarea-in-tabbed-view-m)
        self.addTab(QWidget(), ' + ')
        self.currentChanged.connect(self.add_tab)         

    def add_tab(self, index):
        # if last tab was clicked
        if self._last_tab_was_clicked(index):
            name, number = self._generate_unique_name(0)
            animal = self.gui_data_interface.add_animal(name, number)
            self._create_animal_tab_and_insert(animal, index)
        self._block_add = False

    def _create_animal_tab_and_insert(self, animal, index):
        tab = SingleAnimalTab(self,
                              animal,
                              index,
                              self.gui_data_interface)
        self.insertTab(index, tab, animal.name)
        self.tabs_[animal.number] = tab
        self.setCurrentIndex(index)
        self._block_add = False

    def _last_tab_was_clicked(self, index: int) -> bool:
        return index == self.count() - 1 and not self._block_add

    def _generate_unique_name(self, subscript) -> Tuple[str, int]:
        name = "animal_" + str(subscript)
        if self._is_unique(name, subscript):
            return name, subscript
        return self._generate_unique_name(subscript + 1)

    def _is_unique(self, name, subscript: int) -> bool:
        for number in self.animals:
            animal = self.animals[number]
            if animal.name == name:
                return False
            if animal.number == subscript:
                return False
        return True

    def rename_tab(self, index, name):
        self.tabBar().setTabText(index, name)

    def remove_tab(self, animal_number: int, index: int):
        self.tabs_.pop(animal_number)
        self._block_add = True
        self.removeTab(index)
        for tab in self.tabs_.values():
            if tab.index > index:
                tab.index = tab.index - 1
        if len(self.tabs_) == 0:
            self.add_tab(0)
        current = index if index < len(self.tabs_) else len(self.tabs_) - 1
        self.setCurrentIndex(current)
        self._block_add = False

    def copy_tab(self, animal: Animal, index: int):
        self._block_add = True
        name = 'copy_of_' + animal.name
        uname, number = self._generate_unique_name(0)
        copied_animal = self.gui_data_interface.add_animal(name, number)
        copied_animal.copy_behaviours(animal.behaviours)
        self._create_animal_tab_and_insert(copied_animal, index + 1)

    def create_new_tab(self, animal: Animal):
        tab = SingleAnimalTab(self, animal, len(self.tabs_),
                              self.gui_data_interface)
        self.addTab(tab, animal.name)
        self.tabs_[animal.number] = tab
