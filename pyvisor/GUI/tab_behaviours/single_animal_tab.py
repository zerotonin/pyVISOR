from typing import List

from PyQt5.QtWidgets import (QWidget, QGridLayout,
                             QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit)

from .behaviour_widget import BehaviourWidget
from ..model.animal import Animal
from ..model.gui_data_interface import GUIDataInterface
from ..model.behaviour import Behaviour


class SingleAnimalTab(QWidget):

    def __init__(self, parent,
                 animal: Animal,
                 index_in_parent_tab_widget,
                 gui_data_interface: GUIDataInterface):

        super(SingleAnimalTab, self).__init__(parent)
        self.index = index_in_parent_tab_widget
        self.animal = animal
        self.gui_data_interface = gui_data_interface
        self.current_pos = 0
        self.behav_widgets = []  # type: List[BehaviourWidget]
        self.init_UI()

    @property
    def name(self):
        return self.animal.name

    def init_UI(self):        
        hbox = self._init_main_layout()

        self._init_add_button()
        self._initialize_behaviours()

        # ----------------------
        #   left button vbox
        # ----------------------

        self.vbox_buttons_left = QVBoxLayout()
        hbox.insertLayout(0, self.vbox_buttons_left)
        
        # ---- button edit name
        self.btn_edit_name = QPushButton(self.name)
        self.btn_edit_name.clicked.connect(self.rename)
        self.vbox_buttons_left.addWidget(self.btn_edit_name)

        # ---- button copy animal
        btn_copy_animal = QPushButton('copy animal')
        btn_copy_animal.clicked.connect(self.copy_this_tab)
        self.vbox_buttons_left.addWidget(btn_copy_animal)

        # ---- btn remove
        btn_remove_animal = QPushButton('remove this animal')
        btn_remove_animal.clicked.connect(self.remove_this_tab)    
        btn_remove_animal.setObjectName("removeAnimal")
        self.vbox_buttons_left.addWidget(btn_remove_animal)
        self.vbox_buttons_left.addStretch(1)

    def _initialize_behaviours(self):
        for key in self.animal.behaviours:
            behav = self.animal[key]
            self.add_behaviour_widget(behav)

    def _init_add_button(self):
        self.button_add = QPushButton('add behaviour')
        self.button_add.clicked.connect(self._add_new_behaviour)
        self.grid.addWidget(self.button_add, *self.get_current_pos())

    def _add_new_behaviour(self):
        name = self.animal.get_unique_name()
        new_behav = Behaviour(self.animal.number, name=name)
        self.gui_data_interface.add_behaviour(self.animal, new_behav)
        self.add_behaviour_widget(new_behav)


    def _init_main_layout(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.grid = QGridLayout()
        hbox.addLayout(self.grid)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)
        return hbox

    def _generate_new_name(self):
        return self._generate_unique_name(1)

    def _generate_unique_name(self, subscript):
        name = "behaviour_" + str(subscript)
        if self._is_unique(name):
            return name
        return self._generate_unique_name(subscript + 1)

    def _is_unique(self, name):
        for d in self.behaviour_dicts:
            if d['name'] == name:
                return False
        return True

    def copy_this_tab(self):
        self.parent().copy_tab(self.index)

    def remove_this_tab(self):
        self.parent().remove_tab(self.index)
        self.deleteLater()

    def add_behaviour_widget(self, behaviour: Behaviour):
        for bw in self.behav_widgets:
            if behaviour.name == 'delete':
                break
            if bw.behaviour.name == 'delete':
                continue
            bw.compatible_behaviour_widget.add_checkbox(behaviour, state=False)
        behav_widget = BehaviourWidget(self, behaviour, self.current_pos,
                                       self.gui_data_interface)
        self.behav_widgets.append(behav_widget)
        self.grid.addWidget(behav_widget, *self.get_current_pos())
        self.current_pos += 1
        self.grid.addWidget(self.button_add, *self.get_current_pos())        

    def get_behav_widget_by_name(self, name):
        for w in self.behav_widgets:
            if w.name.name == name:
                return w
        raise KeyError("BehaviourWidget with name {} not found.".format(name))

    def get_current_pos(self):
        return self.get_grid_pos(self.current_pos)

    @staticmethod
    def get_grid_pos(i):
        return [i / 3, i % 3]

    def remove_widget(self, i):
        item = self.behav_widgets.pop(i)
        behav_dict = self.behaviour_dicts.pop(i)
        self.grid.removeWidget(item)
        item.deleteLater()
        self.current_pos -= 1

        for j in range(i, len(self.behav_widgets)):
            w = self.behav_widgets[j]
            w.index = j
            self.grid.addWidget(w, *self.get_grid_pos(w.index))            
        self.grid.addWidget(self.button_add, *self.get_grid_pos(len(self.behav_widgets)))

        name = behav_dict['name']
        for bd in self.behaviour_dicts:
            comp = bd['compatible']
            if comp.count(name):
                comp.pop(comp.index(name))
        for bw in self.behav_widgets:
            bw.create_new_compatible_behaviour_widget()
            # bw.compatible_behaviour_widget.remove_checkbox(name)

    def rename(self):
        self.vbox_buttons_left.removeWidget(self.btn_edit_name)
        self.name_edit = QLineEdit(self.name)
        self.name_edit.returnPressed.connect(self.rename_finished)
        self.vbox_buttons_left.insertWidget(0, self.name_edit)

    def rename_finished(self):
        self.btn_edit_name.setText(self.name_edit.text())
        new_name = str(self.name_edit.text())
        self.main_widget.change_animal_name(self.animal, new_name)
        self.vbox_buttons_left.removeWidget(self.name_edit)
        self.vbox_buttons_left.insertWidget(0, self.btn_edit_name)
        self.name_edit.hide()
        self.parent().rename_tab(self.index, self.name)
