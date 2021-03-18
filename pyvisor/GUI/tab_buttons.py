import copy
import os
from typing import Dict, Union, List, Any, Tuple

import pygame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QPushButton, QMessageBox, QComboBox, QInputDialog)

from .model.animal import Animal
from .model.animal_handler import AnimalHandler
from .model.behaviour import Behaviour

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
DEVICES = {"Keyboard": HERE + "/pictures/gamePad_KB.png",
           "Playstation": HERE + "/pictures/gamePad_PS.png",
           "X-Box": HERE + "/pictures/gamePad_XB.png",
           "Free": HERE + "/pictures/gamePad_free.png"}


# noinspection PyAttributeOutsideInit
class TabButtons(QWidget):

    def __init__(self, parent: QWidget, animal_handler: AnimalHandler):

        self.analysis_list = []
        super(TabButtons, self).__init__()

        self._current_keys = {
            'Keyboard': None,
            'X-Box': None,
            'Playstation': None,
            'Free': None
        }  # type: Dict[str, Union[Dict[str, Behaviour], None]]

        self.parent = parent
        self.animal_handler = animal_handler
        self.animal_handler.register_callback_animal_added(
            lambda x: self.make_animals_box()
        )
        pygame.init()
        # Initialize the joysticks
        pygame.joystick.init()
        self._initialize_device_members()
        self._init_ui()

    def _create_button_binding_dict(self):
        d = {}
        d.update({'selected_device': self.selected_device})
        d.update({'deviceLayout': self.deviceLayout})
        d.update({'deviceNumber': self.deviceNumber})
        d.update({'behavAssignment': Behaviour.from_object_dict_to_savable_dict(self.behavAssignment.behaviours)})
        return d

    def make_joystick_info(self):
        if self.deviceNumber == -2:
            self.make_joystick_info_initial()
        else:
            self.make_selected_joystick_info()

    def make_selected_joystick_info(self):
        self.clearLayout(self.hboxJoyStickInfo)
        v_box_device = QVBoxLayout()
        joy_name = QLabel(self.input_device_names[self.deviceNumber],
                          self)
        joy_name.setStyleSheet(self.labelStyle)
        v_box_device.addWidget(joy_name)

        for animal_number in sorted(self.animal_handler.animals.keys()):
            animal = self.animal_handler.animals[animal_number]
            button_assignments = animal.get_button_assignments(self.selected_device)
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
        if not bool(self.behavAssignment.behaviours):
            key_message = QLabel('no keys defined', self)
            vbox_temp.addWidget(key_message)
        vbox_temp.addStretch()
        return vbox_temp

    def make_joystick_info_initial(self):
        self.clearLayout(self.hboxJoyStickInfo)
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
        self.combo_input_assign.activated[str].connect(self.set_assignDevice)
        self.hboxDeviceChoice.addWidget(self.lbl_input_assign)
        self.hboxDeviceChoice.addWidget(self.combo_input_assign)

        # layout
        self.lbl_input_device = QLabel("select device layout ", self)
        self.lbl_input_device.setStyleSheet(self.labelStyle)
        self.combo_input_device = QComboBox(self)
        for device in DEVICES.keys():
            self.combo_input_device.addItem(device)
        # add signal slot for background change
        self.combo_input_device.activated[str].connect(self.set_device)
        self.hboxDeviceChoice.addWidget(self.lbl_input_device)
        self.hboxDeviceChoice.addWidget(self.combo_input_device)
        self.hboxDeviceChoice.addStretch()
        initial_device = self.input_device_names[0]
        self.set_assignDevice(initial_device)
        self.set_device(initial_device)

    def make_movie_actions_box(self):
        # top label
        movie_box = QVBoxLayout()
        name_label = QLabel('movie actions')
        name_label.setStyleSheet(self.labelStyle)
        movie_box.addWidget(name_label)
        movie_assignments = self._get_behaviour_assignments_of_animal(self.behavAssignment.behaviours,
                                                                      Behaviour.ANIMAL_MOVIE)
        for key in sorted(movie_assignments.keys()):
            binding = movie_assignments[key]
            self._make_movie_label_box(binding, movie_box)

        return movie_box

    def _make_movie_label_box(self, binding: Behaviour, movie_box):
        box, btn_set_uic, button_label = self._create_assign_button_box(binding)
        box.addWidget(btn_set_uic)
        box.addWidget(button_label)
        movie_box.addLayout(box)

    def _create_assign_button_box(self, behaviour: Behaviour):
        box = QHBoxLayout()
        behav_label = QLabel(behaviour.name)
        behav_label.setStyleSheet('color: ' + behaviour.color)
        btn_set_uic = QPushButton('assign button/key')
        button_now = behaviour
        # double lambda to get the variable out of the general scope and let each button call assignBehav
        # with its own behaviour
        btn_set_uic.clicked.connect((lambda buttonNow: lambda: self.assign_button(buttonNow))(button_now))
        button_label = self._create_button_label(behaviour)
        box.addWidget(behav_label)
        return box, btn_set_uic, button_label

    def _create_button_label(self, behaviour: Behaviour):
        key_bindings = behaviour.key_bindings
        key = key_bindings[self.selected_device]
        label = 'no button assigned' if key is None else key
        button_label = QLabel(label)
        if key is None:
            button_label.setStyleSheet('color: #C0C0C0')
        else:
            button_label.setStyleSheet('color: #ffffff')
        return button_label

    def make_animals_box(self):
        self.clearLayout(self.hbox_behaviour_buttons)

        self._create_behaviours_box()
        vbox = self.make_movie_actions_box()
        self.hbox_behaviour_buttons.addLayout(vbox)
        self.hbox_behaviour_buttons.addStretch()
        self.make_joystick_info()

    def _create_behaviours_box(self):
        self.behav_stepLabel = QLabel('Behaviours: ')
        self.behav_stepLabel.resize(20, 40)
        self.behav_stepLabel.setStyleSheet(self.labelStyle)
        self.hbox_behaviour_buttons.addWidget(self.behav_stepLabel)
        for animal_number in sorted(self.animal_handler.animals):
            animal = self.animal_handler.animals[animal_number]
            self._create_info_label(animal)

    def _create_info_label(self, animal: Animal):
        vbox = self.make_behaviour_info_box(animal)
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
            behavBox.addLayout(box)

        return behavBox

    def _create_box_single_behaviour(self, behaviour: Behaviour):
        box, btn_assign, buttonLabel = self._create_assign_button_box(behaviour)
        if behaviour.icon_path is not None:
            icon_label = self._create_icon(behaviour)
            box.addWidget(icon_label)
        box.addWidget(btn_assign)
        box.addWidget(buttonLabel)
        return box

    @staticmethod
    def _create_icon(binding):
        imageLabel = QLabel()
        pixmap = QPixmap(binding.icon_path)
        pixmap = pixmap.scaledToWidth(20)
        imageLabel.setStyleSheet('color: ' + binding.color)
        imageLabel.setPixmap(pixmap)
        return imageLabel

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

    def assign_button(self, buttonBinding: Behaviour):
        # check if device was selected
        if self.selected_device is None:
            QMessageBox.warning(self, 'Set device first!',
                                "You need to choose an input device first",
                                QMessageBox.Ok)
            return

        # check if layout was selected
        if self.deviceLayout is None:
            QMessageBox.warning(self, 'Set layout first!',
                                "You need to choose an input device layout first",
                                QMessageBox.Ok)
            return
        if self._device_is_keyboard():
            text, ok = QInputDialog.getText(self, 'Press', 'Key Entry:')
            if not ok:
                return
            button_identifier = str(text)
        else:
            button_identifier = self.waitOnUICpress()

        if self.behavAssignment.key_is_assigned(button_identifier):
            key, newBinding = self._handle_already_existing(buttonBinding, button_identifier)
        else:
            key, newBinding = self._handle_not_existing(buttonBinding, button_identifier)
        self.behavAssignment[key] = newBinding
        self.make_joystick_info()
        self.make_animals_box()

    def _device_is_keyboard(self) -> bool:
        return self.deviceNumber == self.input_device_names.index('Keyboard')

    def _handle_not_existing(self, buttonBinding, inputCode) -> Tuple[str, Behaviour]:
        # check if a button was assigned to that behaviour
        key, newBinding = self._make_behaviour_key_and_set_binding(buttonBinding, inputCode)
        return key, newBinding

    def _make_behaviour_key_and_set_binding(self, buttonBinding: Behaviour, inputCode):
        label = buttonBinding.label
        oldBehaviourBinding = self.behavAssignment[label]
        if oldBehaviourBinding.key_bindings is not None:
            self._delete_old_behaviour_info(oldBehaviourBinding)
        label, newBinding = self._get_behaviour_and_set_new_binding(buttonBinding, inputCode)
        # icon has to be attached here as well
        newBinding.device = self.selected_device
        return label, newBinding

    def _get_behaviour_and_set_new_binding(self,
                                           buttonBinding: Behaviour,
                                           button_identifier: str) -> Tuple[str, Behaviour]:
        label = buttonBinding.label
        newBinding = copy.deepcopy(self.behavAssignment[label])
        newBinding.animal = buttonBinding.animal
        newBinding.name = buttonBinding.name
        newBinding.color = buttonBinding.color
        newBinding.key_bindings = button_identifier
        return label, newBinding

    def _delete_old_behaviour_info(self, oldBehaviourBinding):
        oldButtonBinding = self.behavAssignment[oldBehaviourBinding.label]
        oldButtonBinding.color = '#C0C0C0'
        oldButtonBinding.animal = None
        oldButtonBinding.name = None
        self.behavAssignment[oldBehaviourBinding.label] = oldButtonBinding

    def _handle_already_existing(self, buttonBinding, inputCode):
        # get old button binding object
        oldButtonBinding = self.behavAssignment[inputCode]
        # we check if there was already a behaviour attached to this button
        if oldButtonBinding.name is not None:
            # the button binding also in the behavAssignment
            key = oldButtonBinding.label
            oldBehaviourBinding = self.behavAssignment[key]
            oldBehaviourBinding.key_bindings = None
            self.behavAssignment[key] = oldBehaviourBinding
        key, newBinding = self._make_behaviour_key_and_set_binding(buttonBinding, inputCode)
        # update both lists
        self.behavAssignment[key] = newBinding
        return key, newBinding

    @staticmethod
    def waitOnUICpress():
        pygame.event.clear()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    inputCode = 'B' + str(event.button)
                    return inputCode
                if event.type == pygame.JOYAXISMOTION:
                    value = event.dict['value']
                    axis = event.dict['axis']
                    if abs(value) > 0.75:
                        if value > 0:
                            inputCode = 'A' + str(axis) + '+'
                        else:
                            inputCode = 'A' + str(axis) + '-'
                        return inputCode
                if event.type == pygame.JOYHATMOTION:
                    value = event.dict['value']
                    inputCode = 'H' + str(value[0]) + str(value[1])
                    return inputCode

    def set_assignDevice(self, device):
        device = str(device)
        if self.selected_device == device:
            return
        self.selected_device = device
        self.deviceNumber = self.input_device_names.index(device)
        self.selected_device = device
        if not self._device_is_keyboard():
            self.joystick = pygame.joystick.Joystick(self.deviceNumber)
            self.joystick.init()
            self.make_joystick_info()
        self.make_animals_box()

    def set_device(self, device: str):
        if self.selected_device is None:
            QMessageBox.warning(self, 'Set device first!',
                                "You need to choose an input device first",
                                QMessageBox.Ok)
            return
        self._set_device(device)

    def _set_device(self, device):
        device = str(device)
        if self.deviceLayout == device:
            return
        self._current_keys[self.deviceLayout] = self.behavAssignment.behaviours.copy()
        self.deviceLayout = device
        self.initializeKeys(device)
        self.pixmap = QPixmap(DEVICES[str(device)])
        self.background_image.setPixmap(self.pixmap.scaled(self.background_image.size(), Qt.KeepAspectRatio))
        self.background_image.setScaledContents(True)
        self.make_joystick_info()
        self.make_animals_box()

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
        keys = {"B0": None, "B1": None, "B2": None,
                "B3": None, "B4": None, "B5": None,
                "B6": None, "B7": None, "B8": None,
                "B9": None, "H01": None, "H0-1": None,
                "H-10": None, "H10": None}
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
        keys.update(movie_keys)
        return keys

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
        keys = {"B0": None, "B1": None, "B2": None,
                "B3": None, "B4": None, "B5": None, "B6": None, "B7": None,
                "B8": None, "A2+": None, "A5+": None, "A2-": None,
                "A5-": None, "H01": None, "H0-1": None,
                "H-10": None, "H10": None}

        movie_keys = {
            "B9": "toggleRunMov", "B10": "stopToggle",
            "A0+": "runMovForward", "A0-": "runMovReverse",
            "A1+": "changeFPShigh", "A1-": "changeFPSlow",
            "A3+": "changeFrameNoHigh1", "A3-": "changeFrameNoLow1",
            "A4+": "changeFrameNoHigh10", "A4-": "changeFrameNoLow10"
        }
        keys.update(movie_keys)
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

    def close_event(self):
        self.save_button_assignments(filename=HOME + '/.pyvisor/guidefaults_buttons.json')

    def resizeEvent(self, event):
        self.background_image.resize(event.size())

    def getAssignments(self):
        return self.behavAssignment.get_button_assignments(), self.behavAssignment

    def getSelectedLayout(self):
        return self.deviceLayout

    def reset_buttons(self):
        self._initialize_device_members()
        self._initialize_joystick()
        self.make_animals_box()

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
        self.parent.tabs.currentChanged.connect(self.make_animals_box)

    def _fill_major_boxes_with_infos(self):
        self.make_joystick_info()
        self.make_animals_box()
        self.make_device_choice()
        self.make_load_save_preset()

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
        self.background_image.setGeometry(0, 0, self.parent.height(), self.parent.width())
        self.pixmap = QPixmap(HERE + '/pictures/gamePad.png')
        self.background_image.setPixmap(self.pixmap.scaled(
            self.background_image.size(),
            Qt.KeepAspectRatio))
        self.background_image.setScaledContents(True)
        self.background_image.resize(self.size())

    def _initialize_device_members(self):
        self.selected_device = None
        self.deviceLayout = None
        self.deviceNumber = -2
        self.lastKeyPressed = (71, 'G')
