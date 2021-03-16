from typing import Dict, Union, List, Any, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QFileDialog, QPushButton, QMessageBox, QComboBox, QInputDialog)

import pygame
import json
import os
import copy
import collections

from .model.behaviours import Behaviour
from .model.animal import Animal

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
DEVICES = {"Keyboard": HERE + "/pictures/gamePad_KB.png",
           "Playstation": HERE + "/pictures/gamePad_PS.png",
           "X-Box": HERE + "/pictures/gamePad_XB.png",
           "Free": HERE + "/pictures/gamePad_free.png"}


# noinspection PyAttributeOutsideInit
class TabButtons(QWidget):

    def __init__(self, parent):

        self.analysis_list = []
        super(TabButtons, self).__init__()

        self._current_keys = {
            'Keyboard': None,
            'X-Box': None,
            'Playstation': None,
            'Free': None
        }  # type: Dict[str, Union[Dict[str, Behaviour], None]]

        self.parent = parent
        pygame.init()
        # Initialize the joysticks
        pygame.joystick.init()
        self._get_and_initialize_behaviour()
        self._init_ui()
        try:
            self.load_button_assignments(filename=HOME + '/.pyvisor/guidefaults_buttons.json')
        except FileNotFoundError:
            print('No preset for button bindings found')

    def make_load_save_preset(self):
        load_button = QPushButton('load preset')
        load_button.clicked.connect(lambda x: self.load_button_assignments())
        save_button = QPushButton('save preset')
        save_button.clicked.connect(lambda x: self.save_button_assignments())
        reset_button = QPushButton('reset buttons')
        reset_button.clicked.connect(self.reset_buttons)
        self.hboxLoadSavePreset.addWidget(load_button)
        self.hboxLoadSavePreset.addWidget(save_button)
        self.hboxLoadSavePreset.addWidget(reset_button)
        self.hboxLoadSavePreset.addStretch()

    def load_button_assignments(self, filename=None):
        if filename is None:
            filename = QFileDialog.getOpenFileName(self, 'Load Button Binding',
                                                   HOME, initialFilter='*.pkl')
            filename = filename[0]
        if len(filename) == 0:
            return

        with open(str(filename), 'rt') as filehandle:
            button_bindings = json.load(filehandle)
            button_bindings['behavAssignment'] = Behaviour.from_savable_dict_to_dict_of_objects(
                button_bindings['behavAssignment'])

        if button_bindings['selected_device'] not in self.input_device_names:
            msg = 'Tried to assign buttons for '
            msg += button_bindings['selected_device']
            msg += '.\n Please connect this device to the computer and restart the program!'
            QMessageBox.warning(self, 'Wrong Input device', msg)
            return

        self.set_device(button_bindings['selected_device'])
        self.set_assignDevice(button_bindings['selected_device'])

        list_of_superfluous_behav = self._get_assigned_buttons_of_undefined_behaviours(button_bindings)

        if len(list_of_superfluous_behav) == 0:
            self.set_button_preset(button_bindings)
            return

        ret = self._create_dialogue_message(list_of_superfluous_behav)
        self._handle_response(button_bindings, list_of_superfluous_behav, ret)

    def _handle_response(self, button_bindings, list_of_superfluous_behav, ret):
        if ret == QMessageBox.Yes:
            # delete superfluous behaviours
            behav_assignments = button_bindings['behavAssignment']
            keys = button_bindings['keys']
            for sfKey in list_of_superfluous_behav:
                key_binding = behav_assignments[sfKey].keyBinding
                del behav_assignments[sfKey]
                del keys[key_binding]
            # and reassign
            button_bindings['behavAssignment'] = behav_assignments
            button_bindings['keys'] = keys
            self.set_button_preset(button_bindings)

    def _create_dialogue_message(self, list_of_superfluous_behav):
        msg = 'The following behaviours do not match current behavioural data: \n'
        for behav in list_of_superfluous_behav:
            msg = msg + behav + ', '
        msg = msg[0:-3]
        msg = msg + '\n Do you still want to load this preset?'
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Found too many behaviours")
        msg_box.setInformativeText(msg)
        msg_box.addButton(QMessageBox.Yes)
        msg_box.addButton(QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        ret = msg_box.exec_()
        return ret

    def _get_assigned_buttons_of_undefined_behaviours(self, button_bindings):
        list_of_behaviours = self.behavAssignment.behaviours.keys()
        list_of_superfluous_behav = list()
        for key in button_bindings['behavAssignment']:
            if key not in list_of_behaviours:
                list_of_superfluous_behav.append(key)
        return list_of_superfluous_behav

    def set_button_preset(self, button_binding_save_dict):
        self.selected_device = button_binding_save_dict['selected_device']
        self.deviceLayout = button_binding_save_dict['deviceLayout']
        assignments = button_binding_save_dict['behavAssignment']
        self.behavAssignment = Animal()
        for label in assignments:
            self.behavAssignment[label] = assignments[label]
        # update with current icons from animal tab
        self.update_icons()
        # the device number might change so this has to be set new if not -1
        self.deviceNumber = self.input_device_names.index(button_binding_save_dict['selected_device'])

        self.make_joystick_info()
        self.make_behaviour_box()

    def update_icons(self):
        for i in range(len(self.animal_tabs)):
            behav_dict = self.animal_tabs[i].behaviour_dicts
            for j in range(len(behav_dict)):
                icon_path = behav_dict[j]['icon']
                key = f'A{i}_{behav_dict[j]["name"]}'
                if key in self.behavAssignment:
                    self.behavAssignment[key].icon_path = icon_path

    def save_button_assignments(self, filename=None):
        button_binding_save_dict = self._create_button_binding_dict()

        if filename is None:
            filename = QFileDialog.getSaveFileName(self, 'Save Button Binding', HOME, initialFilter='*.pkl')
            filename = str(filename[0])
        if len(filename) == 0:
            return

        with open(filename, 'wt') as filehandler:
            json.dump(button_binding_save_dict, filehandler)

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
        joy_name = QLabel(self.input_device_names[self.deviceNumber], self)
        joy_name.setStyleSheet(self.labelStyle)
        v_box_device.addWidget(joy_name)

        button_assignments = self.behavAssignment.get_button_assignments()
        od_keys = collections.OrderedDict(sorted(button_assignments.items()))
        for key, bBinding in od_keys.items():
            hbox = self.make_behav_binding_info(key, bBinding)
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
        if key != behav_binding.keyBinding:
            print('Error key is not binding : ' + key + ' ' + behav_binding.keyBinding)
        labels_list = list()
        labels_list.append(QLabel(key + ' :', self))
        if behav_binding.is_movie:
            animal_no_str = 'movie command'
        else:
            animal_no_str = 'animal No {}'.format(behav_binding.animal)
        labels_list.append(QLabel(animal_no_str, self))
        labels_list.append(QLabel(behav_binding.behaviour, self))
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

    def _create_assign_button_box(self, binding: Behaviour):
        box = QHBoxLayout()
        behav_label = QLabel(binding.behaviour)
        behav_label.setStyleSheet('color: ' + binding.color)
        btn_set_uic = QPushButton('assign button/key')
        button_now = binding
        # double lambda to get the variable out of the general scope and let each button call assignBehav
        # with its own behaviour
        btn_set_uic.clicked.connect((lambda buttonNow: lambda: self.assign_button(buttonNow))(button_now))
        button_label = self._create_button_label(binding)
        box.addWidget(behav_label)
        return box, btn_set_uic, button_label

    def _create_button_label(self, binding):
        label = 'no button assigned' if binding.keyBinding is None else binding.keyBinding
        button_label = QLabel(label)
        if binding.keyBinding is None:
            button_label.setStyleSheet('color: #C0C0C0')
        else:
            button_label.setStyleSheet('color: #ffffff')
        return button_label

    def make_behaviour_box(self):
        self.clearLayout(self.hbox_behaviour_buttons)

        self._create_step_label()
        vbox = self.make_movie_actions_box()
        self.hbox_behaviour_buttons.addLayout(vbox)
        self.hbox_behaviour_buttons.addStretch()

        self.make_joystick_info()

    def _create_step_label(self):
        self.behav_stepLabel = QLabel('Behaviours: ')
        self.behav_stepLabel.resize(20, 40)
        self.behav_stepLabel.setStyleSheet(self.labelStyle)
        self.hbox_behaviour_buttons.addWidget(self.behav_stepLabel)
        self.animal_tabs = self.parent.get_animal_tabs()
        for animalI in range(len(self.animal_tabs)):
            self._create_info_label(animalI)

    def _create_info_label(self, animal):
        vbox = self.make_behaviour_info_box(animal, self.animal_tabs[animal].name,
                                            self.animal_tabs[animal].behaviour_dicts)
        self.hbox_behaviour_buttons.addLayout(vbox)

    def make_behaviour_info_box(self, animal_number, animal_name, behaviors: List[Dict[str, Any]]):
        # top label
        behavBox = QVBoxLayout()
        nameLabel = QLabel(animal_name + ' (A' + str(animal_number) + ')')
        nameLabel.setStyleSheet(self.labelStyle)
        behavBox.addWidget(nameLabel)
        behaviours_of_animal = self._get_behaviour_assignments_of_animal(self.behavAssignment.behaviours,
                                                                         animal_number)
        self.synchronizeBehaviourTabAndBindings(animal_number, behaviors, behaviours_of_animal)

        binding_for_delete = Behaviour(animal=animal_number, behaviour="delete", device=self.deviceLayout)
        behaviours_of_animal[binding_for_delete.label] = binding_for_delete
        self.behavAssignment[binding_for_delete.label] = binding_for_delete

        for key in sorted(behaviours_of_animal.keys()):
            binding = behaviours_of_animal[key]
            box = self._create_box_single_behaviour(binding)
            behavBox.addLayout(box)

        return behavBox

    def _create_box_single_behaviour(self, binding):
        box, btn_assign, buttonLabel = self._create_assign_button_box(binding)
        if binding.icon_path is not None:
            icon_label = self._create_icon(binding)
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

    def _add_missing_behaviour_bindings(self, animal_number, behaviour_assignments, behaviour_dict, listOfAssignments):
        for i in range(len(behaviour_dict)):
            behav = 'A' + str(animal_number) + '_' + behaviour_dict[i]['name']
            if behav not in listOfAssignments:
                temp = Behaviour(animal=animal_number,
                                 icon_path=behaviour_dict[i]['icon'],
                                 behaviour=behaviour_dict[i]['name'],
                                 color=behaviour_dict[i]['color'],
                                 key_binding=None,
                                 device=None)

                self.behavAssignment[temp.label] = temp
                behaviour_assignments.update({behav: temp})

    def _check_for_removed_behaviour_and_delete_bindings(self, behaviour_assignments, listOfAssignments,
                                                         listOfUserBehaviours):
        for key in listOfAssignments:
            if key not in listOfUserBehaviours:
                self._delete_removed_behaviour_binding(behaviour_assignments, key)

    def _delete_removed_behaviour_binding(self, behaviour_assignments, key):
        print("in _delete_behavior_not_in_both_lists")
        del behaviour_assignments[key]
        del self.behavAssignment.behaviours[key]

    @staticmethod
    def _get_behaviour_assignments_of_animal(all_assignments: Dict[str, Behaviour],
                                             animal_number: int) -> Dict[str, Behaviour]:
        behavs_of_animal = {k: v for k, v in all_assignments.items() if v.animal == animal_number}
        return behavs_of_animal

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
        self.make_behaviour_box()

    def _device_is_keyboard(self) -> bool:
        return self.deviceNumber == self.input_device_names.index('Keyboard')

    def _handle_not_existing(self, buttonBinding, inputCode) -> Tuple[str, Behaviour]:
        # check if a button was assigned to that behaviour
        key, newBinding = self._make_behaviour_key_and_set_binding(buttonBinding, inputCode)
        return key, newBinding

    def _make_behaviour_key_and_set_binding(self, buttonBinding: Behaviour, inputCode):
        label = buttonBinding.label
        oldBehaviourBinding = self.behavAssignment[label]
        if oldBehaviourBinding.keyBinding is not None:
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
        newBinding.behaviour = buttonBinding.behaviour
        newBinding.color = buttonBinding.color
        newBinding.keyBinding = button_identifier
        return label, newBinding

    def _delete_old_behaviour_info(self, oldBehaviourBinding):
        oldButtonBinding = self.behavAssignment[oldBehaviourBinding.label]
        oldButtonBinding.color = '#C0C0C0'
        oldButtonBinding.animal = None
        oldButtonBinding.behaviour = None
        self.behavAssignment[oldBehaviourBinding.label] = oldButtonBinding

    def _handle_already_existing(self, buttonBinding, inputCode):
        # get old button binding object
        oldButtonBinding = self.behavAssignment[inputCode]
        # we check if there was already a behaviour attached to this button
        if oldButtonBinding.behaviour is not None:
            # the button binding also in the behavAssignment
            key = oldButtonBinding.label
            oldBehaviourBinding = self.behavAssignment[key]
            oldBehaviourBinding.keyBinding = None
            self.behavAssignment[key] = oldBehaviourBinding
        key, newBinding = self._make_behaviour_key_and_set_binding(buttonBinding, inputCode)
        # update both lists
        self.behavAssignment[key] = newBinding
        return key, newBinding

    def waitOnUICpress(self):
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
        self.make_behaviour_box()

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
        self.make_behaviour_box()

    def initializeKeys(self, device):
        if device == "X-Box":
            if self._current_keys['X-Box'] is None:
                keys = TabButtons._get_default_xbox_keys()
            else:
                keys = self._current_keys['X-Box']
        elif device == "Playstation":
            if self._current_keys['Playstation'] is None:
                keys = TabButtons._get_default_playstation_keys()
            else:
                keys = self._current_keys['Playstation']
        elif device == "Keyboard":
            if self._current_keys['Keyboard'] is None:
                keys = TabButtons._get_default_keyboard_keys()
            else:
                keys = self._current_keys['Keyboard']
        newBehavAssignments = Animal.from_key_assignment_dictionary(keys)
        self.behavAssignment = newBehavAssignments

    @staticmethod
    def _get_default_playstation_keys() -> Dict[str, Behaviour]:
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
        keys = {"B0": Behaviour(device="Playstation", key_binding="B0", color='#C0C0C0'),
                "B1": Behaviour(device="Playstation", key_binding="B1", color='#C0C0C0'),
                "B2": Behaviour(device="Playstation", key_binding="B2", color='#C0C0C0'),
                "B3": Behaviour(device="Playstation", key_binding="B3", color='#C0C0C0'),
                "B4": Behaviour(device="Playstation", key_binding="B4", color='#C0C0C0'),
                "B5": Behaviour(device="Playstation", key_binding="B5", color='#C0C0C0'),
                "B6": Behaviour(device="Playstation", key_binding="B6", color='#C0C0C0'),
                "B7": Behaviour(device="Playstation", key_binding="B7", color='#C0C0C0'),
                "B8": Behaviour(device="Playstation", key_binding="B8", color='#C0C0C0'),
                "B9": Behaviour(device="Playstation", key_binding="B9", color='#C0C0C0'),
                "H01": Behaviour(device="Playstation", key_binding="H01", color='#C0C0C0'),
                "H0-1": Behaviour(device="Playstation", key_binding="H0-1", color='#C0C0C0'),
                "H-10": Behaviour(device="Playstation", key_binding="H-10", color='#C0C0C0'),
                "H10": Behaviour(device="Playstation", key_binding="H10", color='#C0C0C0')}
        movie_keys = {
            "B10": Behaviour(behaviour="toggleRunMov", key_binding="B9", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "B11": Behaviour(behaviour="stopToggle", key_binding="B10", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A0+": Behaviour(behaviour="runMovForward", key_binding="A0+", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A0-": Behaviour(behaviour="runMovReverse", key_binding="A0-", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A1+": Behaviour(behaviour="changeFPShigh", key_binding="A1+", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A1-": Behaviour(behaviour="changeFPSlow", key_binding="A1-", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A3+": Behaviour(behaviour="changeFrameNoHigh1", key_binding="A3+", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A3-": Behaviour(behaviour="changeFrameNoLow1", key_binding="A3-", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A4+": Behaviour(behaviour="changeFrameNoHigh10", key_binding="A4+", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A4-": Behaviour(behaviour="changeFrameNoLow10", key_binding="A4-", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE)
        }
        keys.update(movie_keys)
        return keys

    @staticmethod
    def _get_default_xbox_keys() -> Dict[str, Behaviour]:
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
        keys = {"B0": Behaviour(device="X-Box", key_binding="B0", color='#C0C0C0'),
                "B1": Behaviour(device="X-Box", key_binding="B1", color='#C0C0C0'),
                "B2": Behaviour(device="X-Box", key_binding="B2", color='#C0C0C0'),
                "B3": Behaviour(device="X-Box", key_binding="B3", color='#C0C0C0'),
                "B4": Behaviour(device="X-Box", key_binding="B4", color='#C0C0C0'),
                "B5": Behaviour(device="X-Box", key_binding="B5", color='#C0C0C0'),
                "B6": Behaviour(device="X-Box", key_binding="B6", color='#C0C0C0'),
                "B7": Behaviour(device="X-Box", key_binding="B7", color='#C0C0C0'),
                "B8": Behaviour(device="X-Box", key_binding="B8", color='#C0C0C0'),
                "A2+": Behaviour(device="X-Box", key_binding="A2+", color='#C0C0C0'),
                "A5+": Behaviour(device="X-Box", key_binding="A5+", color='#C0C0C0'),
                "A2-": Behaviour(device="X-Box", key_binding="A2-", color='#C0C0C0'),
                "A5-": Behaviour(device="X-Box", key_binding="A5-", color='#C0C0C0'),
                "H01": Behaviour(device="X-Box", key_binding="H01", color='#C0C0C0'),
                "H0-1": Behaviour(device="X-Box", key_binding="H0-1", color='#C0C0C0'),
                "H-10": Behaviour(device="X-Box", key_binding="H-10", color='#C0C0C0'),
                "H10": Behaviour(device="X-Box", key_binding="H10", color='#C0C0C0')}

        movie_keys = {
            "B9": Behaviour(behaviour="toggleRunMov", key_binding="B9", device="X-Box",
                            color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "B10": Behaviour(behaviour="stopToggle", key_binding="B10", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A0+": Behaviour(behaviour="runMovForward", key_binding="A0+", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A0-": Behaviour(behaviour="runMovReverse", key_binding="A0-", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A1+": Behaviour(behaviour="changeFPShigh", key_binding="A1+", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A1-": Behaviour(behaviour="changeFPSlow", key_binding="A1-", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A3+": Behaviour(behaviour="changeFrameNoHigh1", key_binding="A3+", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A3-": Behaviour(behaviour="changeFrameNoLow1", key_binding="A3-", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A4+": Behaviour(behaviour="changeFrameNoHigh10", key_binding="A4+", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            "A4-": Behaviour(behaviour="changeFrameNoLow10", key_binding="A4-", device="X-Box",
                             color='#ffffff', animal=Behaviour.ANIMAL_MOVIE)
        }
        keys.update(movie_keys)
        return keys

    @staticmethod
    def _get_default_keyboard_keys():
        movie_keys = {
            'k': Behaviour(behaviour="toggleRunMov", device="Keyboard", key_binding='k',
                           color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            'l': Behaviour(behaviour="runMovForward", device="Keyboard", key_binding='l',
                           color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            'j': Behaviour(behaviour="runMovReverse", device="Keyboard", key_binding='j',
                           color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            '.': Behaviour(behaviour="changeFPShigh", device="Keyboard", key_binding='.',
                           color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            ',': Behaviour(behaviour="changeFPSlow", device="Keyboard", key_binding=',',
                           color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            'i': Behaviour(behaviour="stopToggle", device="Keyboard", key_binding='i',
                           color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            'o': Behaviour(behaviour="changeFrameNoHigh1", device="Keyboard", key_binding='o',
                           color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            'u': Behaviour(behaviour="changeFrameNoLow1", device="Keyboard", key_binding='u',
                           color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            '[': Behaviour(behaviour="changeFrameNoLow10", device="Keyboard", key_binding='[',
                           color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
            ']': Behaviour(behaviour="changeFrameNoHigh10", device="Keyboard", key_binding=']',
                           color='#ffffff', animal=Behaviour.ANIMAL_MOVIE),
        }
        return movie_keys

    def initialise_behaviour_assignment(self):
        self.behavAssignment = Animal()

        for animalI in range(len(self.animal_tabs)):
            behavDict = self.animal_tabs[animalI].behaviour_dicts

            # add all behaviours
            for i in range(len(behavDict)):
                temp = Behaviour(animal=animalI,
                                 icon_path=behavDict[i]['icon'],
                                 behaviour=behavDict[i]['name'],
                                 color=behavDict[i]['color'],
                                 key_binding=None,
                                 device=None)
                label = temp.label
                self.behavAssignment[label] = temp

            # add delete function
            temp = Behaviour(animal=animalI,
                             icon_path=None,
                             behaviour='delete',
                             color='#ffffff',
                             key_binding=None,
                             device=None)

            self.behavAssignment[temp.label] = temp

        movie_actions = ["toggleRunMov", "stopToggle", "runMovForward", "runMovReverse",
                         "changeFPShigh", "changeFPSlow",
                         "changeFrameNoHigh1",
                         "changeFrameNoLow1",
                         "changeFrameNoHigh10",
                         "changeFrameNoLow10",]

        for ma in movie_actions:
            binding = Behaviour(animal=Behaviour.ANIMAL_MOVIE, behaviour=ma,
                                color="#ffffff")
            self.behavAssignment[binding.label] = binding

        print("behavAssignment: ", self.behavAssignment)

    def close_event(self):
        self.save_button_assignments(filename=HOME + '/.pyvisor/guidefaults_buttons.json')

    def resizeEvent(self, event):
        self.background_image.resize(event.size())

    def getAssignments(self):
        return self.behavAssignment.get_button_assignments(), self.behavAssignment

    def getSelectedLayout(self):
        return self.deviceLayout

    def reset_buttons(self):
        self._get_and_initialize_behaviour()
        self._initialize_joystick()
        self.make_behaviour_box()

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
        self.parent.tabs.currentChanged.connect(self.make_behaviour_box)

    def _fill_major_boxes_with_infos(self):
        self.make_joystick_info()
        self.make_behaviour_box()
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

    def _get_and_initialize_behaviour(self):
        self.animal_tabs = self.parent.get_animal_tabs()
        self.selected_device = None
        self.deviceLayout = None
        self.deviceNumber = -2
        self.initialise_behaviour_assignment()
        self.lastKeyPressed = (71, 'G')


