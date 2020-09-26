from PyQt5.QtWidgets import QTabWidget, QWidget

import os
import json
from .single_animal_tab import SingleAnimalTab

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")

class AnimalTabWidget(QTabWidget):

    def __init__(self, parent):        
        super(AnimalTabWidget, self).__init__(parent)
        self.parent = parent  # parent should be TabBehaviours object
        try:
            with open(HOME + "/.pyvisor/guidefaults_animaltab.json", 'r') as f:
                self.values = json.load(f)
        except FileNotFoundError:
            with open(HERE + "/../guidefaults_animaltab.json", 'r') as f:
                self.values = json.load(f)
        self.tabs_ = []
        self._block_add = False
        self.init_UI()

    def init_UI(self):
        if self.values:
            for item in self.values:                
                self.create_new_tab(*item)
        else:
            self.add_tab(-1)

        ## Add a '+' tab, creating a new tab when pressed.
        # Inspired by user Garjy from stackoverflow.com 
        # (full URL: http://stackoverflow.com/questions/19975137/how-can-i-add-a-new-tab-button-next-to-the-tabs-of-a-qmdiarea-in-tabbed-view-m)
        self.addTab(QWidget(), ' + ')
        self.currentChanged.connect(self.add_tab)         

    def add_tab(self, index):
        # if last tab was clicked
        if index == self.count() - 1 and not self._block_add:            
            name = self._generate_unique_name(1)
            self.values.append((name, []))
            tab = SingleAnimalTab(self,
                                  self.values[index][0],
                                  self.values[index][1],
                                  len(self.tabs_))
            self.insertTab(index, tab, name)
            self.tabs_.append(tab)
            self.setCurrentIndex(index)
        self._block_add = False

    def _generate_unique_name(self, subscript):
        name = "animal_" + str(subscript)
        if self._is_unique(name):
            return name
        return self._generate_unique_name(subscript + 1)

    def _is_unique(self, name):
        for item in self.values:
            if item[0] == name:
                return False
        return True

    def rename_tab(self, index, name):
        self.tabBar().setTabText(index, name)
        as_list = list(self.values[index])
        as_list[0] = name
        self.values[index] = tuple(as_list)

    def remove_tab(self, index):        
        self.tabs_.pop(index)
        self._block_add = True
        self.removeTab(index)
        self.values.pop(index)
        for t in range(index, len(self.tabs_)):
            self.tabs_[t].index = t
        self.setCurrentIndex(max(index - 1, 0))
        if index > 0:
            return        
        self.add_tab(0)

    def copy_tab(self, index):
        src_tuple = self.values[index]
        new_tuple = ('copy_of_' + src_tuple[0], [item.copy() for item in src_tuple[1]])
        self.values.append(new_tuple)
        tab = SingleAnimalTab(self, self.values[-1][0], self.values[-1][1], len(self.tabs_))
        self.insertTab(len(self.tabs_), tab, new_tuple[0])
        self.tabs_.append(tab)
        self.setCurrentIndex(len(self.tabs_) - 1)

    def create_new_tab(self, name, behaviour_dicts):
        tab = SingleAnimalTab(self, name, behaviour_dicts, len(self.tabs_))
        self.addTab(tab, name)
        self.tabs_.append(tab)

    def set_config(self, config):
        for idx in range(1, self.count()):
            self.remove_tab(idx)
        if config is None:
            self.values = {}
            return
        self.values = config
        for item in self.values:
            self.create_new_tab(*item)

    def close_event(self):
        with open(HOME + '/.pyvisor/guidefaults_animaltab.json', 'w') as f:
            json.dump(self.values, f, indent=4)
