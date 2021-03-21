import os
from typing import Dict, List, Any

import os
from typing import Dict, List, Any

import pygame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QMessageBox, QComboBox, QPushButton)

from pyvisor.GUI.model.animal import Animal
from pyvisor.GUI.model.behaviour import Behaviour
from pyvisor.GUI.model.gui_data_interface import GUIDataInterface
from pyvisor.GUI.model.scorer_action import ScorerAction
from pyvisor.GUI.tab_buttons.assign_button_box import AssignButtonBox

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
DEVICES = {"Keyboard": HERE + "/../pictures/gamePad_KB.png",
           "Playstation": HERE + "/../pictures/gamePad_PS.png",
           "X-Box": HERE + "/../pictures/gamePad_XB.png",
           "Free": HERE + "/../pictures/gamePad_free.png"}


# noinspection PyAttributeOutsideInit
class TabButtons(QWidget):

    def __init__(self, parent: QWidget, gui_data_interface: GUIDataInterface):
        super(TabButtons, self).__init__(parent)
        self.analysis_list = []

        self.gui_data_interface = gui_data_interface
        self._behaviour_boxes = {}  # type: Dict[str, QWidget]
        self._movie_action_boxes = {}  # type: Dict[str, QWidget]
        self._animal_boxes = {}  # type: Dict[int, QVBoxLayout]

        pygame.init()
        # Initialize the joysticks
        pygame.joystick.init()
        self._initialize_device_members()
        self._init_ui()

    def make_joystick_info(self):
        if self.deviceNumber == -2:
            self.make_joystick_info_initial()
        else:
            self.make_selected_joystick_info()

    def make_selected_joystick_info(self):
        v_box_device = QVBoxLayout()
        joy_name = QLabel(self.input_device_names[self.deviceNumber],
                          self)
        joy_name.setStyleSheet(self.labelStyle)
        v_box_device.addWidget(joy_name)

        for animal_number in sorted(self.gui_data_interface.animals.keys()):
            animal = self.gui_data_interface.animals[animal_number]
            button_assignments = animal.get_button_assignments(
                self.gui_data_interface.selected_device
            )
            for key in sorted(button_assignments.keys()):
                behaviour = button_assignments[key]
                hbox = self.make_behav_binding_info(key, behaviour)
                if hbox is None:
                    continue
                v_box_device.addLayout(hbox)
            v_box_device.addStretch()
        self.hboxJoyStickInfo.addLayout(v_box_device)
        self.hboxJoyStickInfo.addStretch()

    def make_keyboard_info(self):
        vbox_temp = QVBoxLayout()
        joy_name = QLabel('Keyboard', self)
        joy_name.setStyleSheet(self.labelStyle)
        vbox_temp.addWidget(joy_name)
        vbox_temp.addStretch()
        return vbox_temp

    def make_joystick_info_initial(self):
        for joyI in range(self.n_joysticks):
            vbox_temp = QVBoxLayout()
            joy_name = QLabel(self.input_device_names[joyI], self)
            joy_name.setStyleSheet(self.labelStyle)
            vbox_temp.addWidget(joy_name)
            for i in range(self.axesNum[joyI]):
                widget = self.make_device_feature_info('axis + ', i, 'None', 'None')
                vbox_temp.addLayout(widget)
                widget = self.make_device_feature_info('axis - ', i, 'None', 'None')
                vbox_temp.addLayout(widget)
            for i in range(self.buttonsNum[joyI]):
                widget = self.make_device_feature_info('button', i, 'None', 'None')
                vbox_temp.addLayout(widget)
            for i in range(self.hatsNum[joyI]):
                widget = self.make_device_feature_info('hat h+ ', i, 'None', 'None')
                vbox_temp.addLayout(widget)
                widget = self.make_device_feature_info('hat h- ', i, 'None', 'None')
                vbox_temp.addLayout(widget)
                widget = self.make_device_feature_info('hat v+ ', i, 'None', 'None')
                vbox_temp.addLayout(widget)
                widget = self.make_device_feature_info('hat v- ', i, 'None', 'None')
                vbox_temp.addLayout(widget)
            vbox_temp.addStretch()
            self.hboxJoyStickInfo.addLayout(vbox_temp)
        key_board_widget = self.make_keyboard_info()
        self.hboxJoyStickInfo.addLayout(key_board_widget)
        self.hboxJoyStickInfo.addStretch()

    def make_behav_binding_info(self, key, behav_binding: Behaviour):
        if key is None:
            return
        # initialise return value
        hbox_temp = QHBoxLayout()
        # make text labels
        if key != behav_binding.key_bindings:
            print('Error key is not binding : ' + key + ' ' + behav_binding.key_bindings)
        labels_list = list()
        labels_list.append(QLabel(key + ' :', self))
        if behav_binding.is_movie:
            animal_no_str = 'movie command'
        else:
            animal_no_str = 'animal No {}'.format(behav_binding.animal)
        labels_list.append(QLabel(animal_no_str, self))
        labels_list.append(QLabel(behav_binding.name, self))
        # set labels to transparent background
        for i in range(3):
            labels_list[i].setStyleSheet(self.labelStyle)
        # adjust behaviour color
        labels_list[2].setStyleSheet('color: ' + behav_binding.color)
        # add widgets to layout !!! need to add icon when implemented
        for i in range(3):
            hbox_temp.addWidget(labels_list[i])
        return hbox_temp

    def make_device_feature_info(self, device_feature, number, animal, behaviour):
        hbox = QHBoxLayout()
        device_text = device_feature + ' ' + str(number)
        device_label = QLabel(device_text, self)
        animal_label = QLabel(animal, self)
        behav_label = QLabel(behaviour, self)
        hbox.addWidget(device_label)
        hbox.addWidget(animal_label)
        hbox.addWidget(behav_label)
        return hbox

    def make_device_choice(self):
        self.lbl_input_assign = QLabel("select device to assign ", self)
        self.lbl_input_assign.setStyleSheet(self.labelStyle)
        self.combo_input_assign = QComboBox(self)
        for device in self.input_device_names:
            self.combo_input_assign.addItem(device)
        # add signal slot for assignment change
        self.combo_input_assign.activated[str].connect(self.set_device)
        self.hboxDeviceChoice.addWidget(self.lbl_input_assign)
        self.hboxDeviceChoice.addWidget(self.combo_input_assign)

        button_reset = QPushButton("Reset bindings")
        button_reset.clicked.connect(self._reset_buttons)
        self.hboxDeviceChoice.addWidget(button_reset)

        button_default_bindings = QPushButton("Set default movie bindings")
        button_default_bindings.clicked.connect(self._set_default_movie_bindings)
        self.hboxDeviceChoice.addWidget(button_default_bindings)

        self.hboxDeviceChoice.addStretch()

    def _set_default_movie_bindings(self):
        dev = self.gui_data_interface.selected_device
        if dev == "Keyboard":
            bindings_map = self._get_default_keyboard_keys()
        elif dev == "Playstation":
            bindings_map = self._get_default_playstation_keys()
        elif dev == "X-Box":
            bindings_map = self._get_default_xbox_keys()
        else:
            return
        inv_key_values = {value: key for (key, value) in bindings_map.items()}
        for action_name in inv_key_values:
            action = self.gui_data_interface.movie_bindings[action_name]
            new_button = inv_key_values[action_name]
            self.gui_data_interface.change_button_binding(action, new_button, is_behaviour=False)

    def make_movie_actions_box(self) -> QWidget:
        # top label
        movie_widget = QWidget(self)
        self.movie_box = QVBoxLayout(movie_widget)
        name_label = QLabel('movie actions')
        name_label.setStyleSheet(self.labelStyle)
        self.movie_box.addWidget(name_label)
        movie_assignments = self.gui_data_interface.movie_bindings
        for name in sorted(movie_assignments.keys()):
            movie_action = movie_assignments[name]
            self._make_movie_label_box(movie_action, self.movie_box)

        return movie_widget

    def _make_movie_label_box(
            self,
            movie_action: ScorerAction,
            movie_box):
        color = "#ffffff"
        box = self._create_assign_button_box(
            color,
            movie_action,
            is_behaviour=False
        )
        self._movie_action_boxes[movie_action.name] = box
        movie_box.addWidget(box)

    def _create_assign_button_box(self,
                                  color: str,
                                  bound_object: ScorerAction,
                                  is_behaviour: bool) -> AssignButtonBox:

        box = AssignButtonBox(self, self.gui_data_interface, bound_object, color, is_behaviour)
        return box

    def make_animals_box(self):
        self._create_behaviours_box()
        movie_widget = self.make_movie_actions_box()
        self.hbox_behaviour_buttons.addWidget(movie_widget)
        self.hbox_behaviour_buttons.addStretch()

    def _create_behaviours_box(self):
        self.behav_stepLabel = QLabel('Behaviours: ')
        self.behav_stepLabel.resize(20, 40)
        self.behav_stepLabel.setStyleSheet(self.labelStyle)
        self.hbox_behaviour_buttons.addWidget(self.behav_stepLabel)
        for animal_number in sorted(self.gui_data_interface.animals):
            animal = self.gui_data_interface.animals[animal_number]
            self._create_info_label(animal)

    def _create_info_label(self, animal: Animal):
        vbox = self.make_behaviour_info_box(animal)
        self._animal_boxes[animal.number] = vbox
        self.hbox_behaviour_buttons.addLayout(vbox)

    def make_behaviour_info_box(self, animal: Animal):
        # top label
        behavBox = QVBoxLayout()
        nameLabel = QLabel(animal.name + ' (A' + str(animal.number) + ')')
        nameLabel.setStyleSheet(self.labelStyle)
        behavBox.addWidget(nameLabel)

        if not animal.has_behaviour('delete'):
            behav_delete = Behaviour(animal=animal.number,
                                     name="delete")
            animal[behav_delete.label] = behav_delete

        for key in sorted(animal.behaviours.keys()):
            behav = animal.behaviours[key]
            box = self._create_box_single_behaviour(behav)
            self._behaviour_boxes[behav.label] = box
            behavBox.addWidget(box)

        return behavBox

    def _create_box_single_behaviour(
            self,
            behaviour: Behaviour
    ):
        box = self._create_assign_button_box(
            behaviour.color,
            behaviour,
            is_behaviour=True
        )
        return box

    def synchronizeBehaviourTabAndBindings(self, animal_number: int, behaviour_dict: List[Dict[str, Any]],
                                           behaviour_assignments: Dict[str, Behaviour]):

        list_of_behaviours = []
        for bd in behaviour_dict:
            label = 'A{}_{}'.format(animal_number, bd['name'])
            list_of_behaviours.append(label)
        listOfAssignments = list(behaviour_assignments.keys())

        self._check_for_removed_behaviour_and_delete_bindings(behaviour_assignments, listOfAssignments,
                                                              list_of_behaviours)

        self._add_missing_behaviour_bindings(animal_number, behaviour_assignments, behaviour_dict, listOfAssignments)
        return behaviour_assignments

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())

    def set_assignDevice(self, device):
        device = str(device)
        if self.gui_data_interface.selected_device == device:
            return
        self.gui_data_interface.selected_device = device
        if device != "Keyboard":
            self.joystick = pygame.joystick.Joystick(self.deviceNumber)
            self.joystick.init()

    def set_device(self, device: str):
        if self.gui_data_interface.selected_device is None:
            QMessageBox.warning(self, 'Set device first!',
                                "You need to choose an input device first",
                                QMessageBox.Ok)
            return
        self._set_device(device)

    def _set_device(self, device):
        device = str(device)
        if self.gui_data_interface.selected_device == device:
            return
        self.pixmap = QPixmap(DEVICES[str(device)])
        self.background_image.setPixmap(self.pixmap.scaled(self.background_image.size(), Qt.KeepAspectRatio))
        self.background_image.setScaledContents(True)
        self.deviceNumber = self.input_device_names.index(device)

    @staticmethod
    def _get_default_playstation_keys() -> Dict[str, str]:
        #           B6                                   B7
        #           B4                                   B5
        #        _=====_                               _=====_
        #       / _____ \                             / _____ \
        #     +.-'_____'-.---------------------------.-'_____'-.+
        #    /   |     |  '.                       .'  |     |   \
        #   / ___| H2+ |___ \                     / ___| B0  |___ \
        #  / |             | ;  __           _   ; |             | ;
        #  | | H1-      H1+|   |__|B8     B9|_:> | | B3       B1 | |
        #  | |___       ___| ;SELECT       START ; |___       ___| ;
        #  |\    | H2- |    /  _     ___      _   \    | B2  |    /|
        #  | \   |_____|  .','" "', |___|  ,'" "', '.  |_____|  .' |
        #  |  '-.______.-' /  A1-  \ANALOG/  A4-  \  '-._____.-'   |
        #  |               |A0- A0+|------|A3- A3+|                |
        #  |              /\  A1+  /      \  A4+  /\               |
        #  |             /  '.___.'        '.___.'  \              |
        #  |            /     B10            B11     \             |
        #   \          /                              \           /
        #    \________/                                \_________/
        #  PS2 CONTROLLER
        movie_keys = {
            "B10": "toggleRunMov",
            "B11": "stopToggle",
            "A0+": "runMovForward",
            "A0-": "runMovReverse",
            "A1+": "changeFPShigh",
            "A1-": "changeFPSlow",
            "A3+": "changeFrameNoHigh1",
            "A3-": "changeFrameNoLow1",
            "A4+": "changeFrameNoHigh10",
            "A4-": "changeFrameNoLow10"
        }
        return movie_keys

    @staticmethod
    def _get_default_xbox_keys() -> Dict[str, str]:
        #                 AT2+                                         AT5+
        #                  B4                                           B5
        #            ,,,,---------,_                               _,--------,,,,
        #          /-----```````---/`'*-,_____________________,-*'`\---``````-----\
        #         /     A1-                      B8                   ,---,        \
        #        /   , -===-- ,          B6     ( X )    B7     ,---, '-B3' ,---,   \
        #       /A0-||'( : )'||A0+     (<)-|           |-(>)   'B2-' ,---, 'B1-'    \
        #      /    \\ ,__, //           H01                      A4- '-B0'           \
        #     /         A1+         ,--'`!`!`'--,              ,--===--,               \
        #    /  B9              H-10||  ==O==  ||H10       A3-||'( : )'||A3+            \
        #   /                       '--, !,!, --'             \\  ,__, //                \
        #  |                          ,--------------------------, A4+     B10            |
        #  |                      ,-'`  H0-1                     `'-,                     |
        #  \                   ,-'`                                  `'-,                 /
        #   `'----- ,,,, -----'`                                       `'----- ,,,, -----'`
        keys = {
            "B9": "toggleRunMov", "B10": "stopToggle",
            "A0+": "runMovForward", "A0-": "runMovReverse",
            "A1+": "changeFPShigh", "A1-": "changeFPSlow",
            "A3+": "changeFrameNoHigh1", "A3-": "changeFrameNoLow1",
            "A4+": "changeFrameNoHigh10", "A4-": "changeFrameNoLow10"
        }
        return keys

    @staticmethod
    def _get_default_keyboard_keys() -> Dict[str, str]:
        movie_keys = {
            'k': "toggleRunMov", 'l': "runMovForward",
            'j': "runMovReverse",
            '.': "changeFPShigh", ',': "changeFPSlow",
            'i': "stopToggle", 'o': "changeFrameNoHigh1",
            'u': "changeFrameNoLow1", '[': "changeFrameNoLow10",
            ']': "changeFrameNoHigh10"
        }
        return movie_keys

    def resizeEvent(self, event):
        self.background_image.resize(event.size())

    def _reset_buttons(self):
        self.gui_data_interface.reset_all_bindings()

    def _initialize_joystick(self):
        # Get count of joysticks
        self.n_joysticks = pygame.joystick.get_count()
        # variables
        self.hatsNum = []
        self.buttonsNum = []
        self.axesNum = []
        self.input_device_names = []
        for i in range(self.n_joysticks):
            self._append_joystick_info(i)
        self.input_device_names.append('Keyboard')

    def _append_joystick_info(self, joystick_number):
        self.joystick = pygame.joystick.Joystick(joystick_number)
        self.joystick.init()
        # count the axes
        self.axesNum.append(self.joystick.get_numaxes())
        self.buttonsNum.append(self.joystick.get_numbuttons())
        self.hatsNum.append(self.joystick.get_numhats())
        self.input_device_names.append(self.joystick.get_name())

    def _init_ui(self):
        self._initialize_joystick()
        self._set_background_image()
        self._initialize_layout()

    def _initialize_layout(self):
        self._make_major_boxes()
        self._add_layouts_to_central_vertical_box()
        self.labelStyle = """
        color: white;
        background-color: rgba(255, 255, 255, 125);
        margin-top: 2px;
        font-weight: bold;
        """
        # fill major boxes with infos
        self._fill_major_boxes_with_infos()
        self.setLayout(self.vbox)

    def _fill_major_boxes_with_infos(self):
        self.make_joystick_info()
        self.make_animals_box()
        self.make_device_choice()

    def _add_layouts_to_central_vertical_box(self):
        self.vbox.addStretch()
        self.vbox.addLayout(self.hboxDeviceChoice)
        self.vbox.addLayout(self.hbox_behaviour_buttons)
        self.vbox.addLayout(self.hboxLoadSavePreset)
        self.vbox.addLayout(self.hboxJoyStickInfo)
        self.vbox.addStretch()

    def _make_major_boxes(self):
        self.vbox = QVBoxLayout()
        self.hboxDeviceChoice = QHBoxLayout()
        self.hbox_behaviour_buttons = QHBoxLayout()
        self.hboxJoyStickInfo = QHBoxLayout()
        self.hboxLoadSavePreset = QHBoxLayout()

    def _set_background_image(self):
        self.background_image = QLabel(self)
        self.background_image.setGeometry(0, 0, self.parent().height(), self.parent().width())
        self.pixmap = QPixmap(HERE + '/../pictures/gamePad.png')
        self.background_image.setPixmap(self.pixmap.scaled(
            self.background_image.size(),
            Qt.KeepAspectRatio))
        self.background_image.setScaledContents(True)
        self.background_image.resize(self.size())

    def _initialize_device_members(self):
        self.deviceNumber = -2
        self.lastKeyPressed = (71, 'G')
