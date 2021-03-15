from typing import Dict, Union, List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QFileDialog, QPushButton, QMessageBox, QComboBox, QInputDialog)

import pygame
import json
from .behavBinding import BehavBinding
import os
import copy
import collections

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
        }  # type: Dict[str, Union[BehavBinding, None]]

        self.parent = parent
        pygame.init()
        # Initialize the joysticks
        pygame.joystick.init()
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
            for key in ['keys', 'behavAssignment']:
                button_bindings[key] = BehavBinding.from_savable_dict_to_dict_of_objects(button_bindings[key])

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
        list_of_behaviours = self.behavAssignment.assignments.keys()
        list_of_superfluous_behav = list()
        for key in button_bindings['behavAssignment']:
            if key not in list_of_behaviours:
                list_of_superfluous_behav.append(key)
        return list_of_superfluous_behav

    def set_button_preset(self, button_binding_save_dict):
        self.selected_device = button_binding_save_dict['selected_device']
        self.deviceLayout = button_binding_save_dict['deviceLayout']
        self.keys = button_binding_save_dict['keys']
        self.behavAssignment = button_binding_save_dict['behavAssignment']
        # update with current icons from animal tab
        self.update_icons()
        # the device number might change so this has to be set new if not -1
        self.deviceNumber = self.input_device_names.index(button_binding_save_dict['selected_device'])

        self.make_joystick_info()
        self.makeBehaviourSummary()

    def update_icons(self):
        for i in range(len(self.animal_tabs)):
            behav_dict = self.animal_tabs[i].behaviour_dicts
            for j in range(len(behav_dict)):
                icon_path = behav_dict[j]['icon']
                key = f'A{i}_{behav_dict[j]["name"]}'
                if key in self.behavAssignment:
                    self.behavAssignment[key].icon_path = icon_path

    def save_button_assignments(self, filename=None):
        for key in self.behavAssignment.assignments.keys():
            button_key = self.behavAssignment[key].keyBinding
            # check if keyBinding is the same in both dictionaries
            if button_key not in self.keys:
                import ipdb
                ipdb.set_trace()
                QMessageBox.warning(self, 'Key Assignment failed!',
                                    key + " is not assigned to a key / button",
                                    QMessageBox.Ok)
                return

            ba_behav = self.behavAssignment[key].behaviour
            key_behav = self.keys[button_key].behaviour

            if key_behav != ba_behav:
                QMessageBox.warning(self, 'Behaviours Not Synchronized!',
                                    "There is an internal problem with " + ba_behav + "/" + key_behav,
                                    QMessageBox.Ok)
                return

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
        d.update({'keys': BehavBinding.from_object_dict_to_savable_dict(self.keys)})
        d.update({'behavAssignment': BehavBinding.from_object_dict_to_savable_dict(self.behavAssignment)})
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

        od_keys = collections.OrderedDict(sorted(self.keys.items()))
        try:
            for key, bBinding in od_keys.iteritems():
                hbox = self.make_behav_binding_info(key, bBinding)
                v_box_device.addLayout(hbox)
        except AttributeError:
            for key, bBinding in od_keys.items():
                hbox = self.make_behav_binding_info(key, bBinding)
                v_box_device.addLayout(hbox)
        v_box_device.addStretch()
        self.hboxJoyStickInfo.addLayout(v_box_device)
        self.hboxJoyStickInfo.addStretch()

    def make_keyboard_info(self):
        vbox_temp = QVBoxLayout()
        joy_name = QLabel('Keyboard', self)
        joy_name.setStyleSheet(self.labelStyle)
        vbox_temp.addWidget(joy_name)
        if bool(self.keys):
            pass
        else:
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

    def make_behav_binding_info(self, key, behav_binding: BehavBinding):
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

    def make_movie_info_box(self):
        # top label
        movie_box = QVBoxLayout()
        name_label = QLabel('movie actions')
        name_label.setStyleSheet(self.labelStyle)
        movie_box.addWidget(name_label)
        behaviour_assignments = collections.OrderedDict(sorted(self.behavAssignment.items()))
        try:
            item_iterator = behaviour_assignments.iteritems()
        except AttributeError:
            item_iterator = behaviour_assignments.items()
        for key, binding in item_iterator:
            if binding.animal == 'movie':
                self._make_movie_label_box(binding, movie_box)

        return movie_box

    def _make_movie_label_box(self, binding, movie_box):
        box, btn_set_uic, button_label = self._create_layout_of_movie_label_box(binding)
        box.addWidget(btn_set_uic)
        box.addWidget(button_label)
        movie_box.addLayout(box)

    def _create_layout_of_movie_label_box(self, binding):
        box = QHBoxLayout()
        behav_label = QLabel(binding.behaviour)
        behav_label.setStyleSheet('color: ' + binding.color)
        btn_set_uic = QPushButton('assign button/key')
        button_now = binding
        # double lambda to get the variable out of the general scope and let each button call assignBehav
        # with its own behaviour
        btn_set_uic.clicked.connect((lambda buttonNow: lambda: self.assignBehav(buttonNow))(button_now))
        # now check if the behaviour is allready in behavAssignments
        button_label = QLabel(binding.keyBinding)
        if binding.keyBinding == 'no button assigned':
            button_label.setStyleSheet('color: #C0C0C0')
        else:
            button_label.setStyleSheet('color: #ffffff')
        box.addWidget(behav_label)
        return box, btn_set_uic, button_label

    def makeBehaviourSummary(self):
        self.clearLayout(self.hboxConciseBehav)

        self._create_step_label()
        vbox = self.make_movie_info_box()
        self.hboxConciseBehav.addLayout(vbox)
        self.hboxConciseBehav.addStretch()

        self.make_joystick_info()

    def _create_step_label(self):
        self.behav_stepLabel = QLabel('Behaviours: ')
        self.behav_stepLabel.resize(20, 40)
        self.behav_stepLabel.setStyleSheet(self.labelStyle)
        self.hboxConciseBehav.addWidget(self.behav_stepLabel)
        self.animal_tabs = self.parent.get_animal_tabs()
        for animalI in range(len(self.animal_tabs)):
            self._create_info_label(animalI)

    def _create_info_label(self, animal):
        vbox = self.makeBehavInfoBox(animal, self.animal_tabs[animal].name,
                                     self.animal_tabs[animal].behaviour_dicts)
        self.hboxConciseBehav.addLayout(vbox)

    def makeBehavInfoBox(self, animal_number, animal_name, behaviors: Dict[str, str]):
        # top label
        behavBox = QVBoxLayout()
        nameLabel = QLabel(animal_name + ' (A' + str(animal_number) + ')')
        nameLabel.setStyleSheet(self.labelStyle)
        behavBox.addWidget(nameLabel)
        behavAs = self.slicedict(self.behavAssignment, 'A' + str(animal_number) + '_')
        behavAs = self.synchronizeBehaviourTabAndBindings(animal_number, behaviors, behavAs)
        behavAs = collections.OrderedDict(sorted(behavAs.items()))

        try:
            item_iterator = behavAs.iteritems()
        except AttributeError:
            item_iterator = behavAs.items()

        for key, binding in item_iterator:
            box, btn_setUIC, buttonLabel = self._create_layout_of_movie_label_box(binding)
            if binding.icon_path is not None and binding.icon_path is not None and binding.icon_path:
                imageLabel = QLabel()
                pixmap = QPixmap(binding.icon_path)
                pixmap = pixmap.scaledToWidth(20)
                imageLabel.setStyleSheet('color: ' + binding.color)
                imageLabel.setPixmap(pixmap)
                box.addWidget(imageLabel)
            box.addWidget(btn_setUIC)
            box.addWidget(buttonLabel)
            behavBox.addLayout(box)

        return behavBox

    def synchronizeBehaviourTabAndBindings(self, animal_number, behaviour_dict: Dict[str, str],
                                           behaviour_assignments):
        startPoint = len('A' + str(animal_number) + '_')
        listOfUserBehaviours = list()
        for bd in behaviour_dict:
            listOfUserBehaviours.append(bd['name'])
        listOfUserBehaviours.append('delete')
        listOfAssignments = behaviour_assignments.keys()

        for key in listOfAssignments:
            if key[startPoint:] not in listOfUserBehaviours:
                del behaviour_assignments[key]
                buttonKey = self.behavAssignment[key].keyBinding
                del self.behavAssignment[key]

                if buttonKey != 'no button assigned':
                    self.keys[buttonKey].behaviour = None
                    self.keys[buttonKey].animal = None
                    self.keys[buttonKey].color = '#C0C0C0'

        for i in range(len(behaviour_dict)):
            behav = 'A' + str(animal_number) + '_' + behaviour_dict[i]['name']
            if behav not in listOfAssignments:
                temp = BehavBinding(animal=animal_number,
                                    icon_path=behaviour_dict[i]['icon'],
                                    behaviour=behaviour_dict[i]['name'],
                                    color=behaviour_dict[i]['color'],
                                    key_binding=None,
                                    device=None)

                self.behavAssignment.update({behav: temp})
                behaviour_assignments.update({behav: temp})
        return behaviour_assignments

    @staticmethod
    def slicedict(d, s):
        try:
            return {k: v for k, v in d.iteritems() if k.startswith(s)}
        except AttributeError:
            return {k: v for k, v in d.items() if k.startswith(s)}

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())

    def assignBehav(self, buttonBinding):
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
        # Check if this is a keyboard assignment
        if self._device_is_keyboard():
            text, ok = QInputDialog.getText(self, 'Press', 'Key Entry:')
            if not ok:
                return
            inputCode = str(text)
            # No this is a gamepad assignment
        else:
            inputCode = self.waitOnUICpress()

        if self._key_already_existing(inputCode):
            key, newBinding = self._handle_already_existing(buttonBinding, inputCode)
        else:
            key, newBinding = self._handle_not_existing(buttonBinding, inputCode)
        self.behavAssignment.update({key: newBinding})
        self.keys.update({inputCode: copy.deepcopy(newBinding)})
        self.make_joystick_info()
        self.makeBehaviourSummary()

    def _device_is_keyboard(self) -> bool:
        return self.deviceNumber == self.input_device_names.index('Keyboard')

    def _key_already_existing(self, inputCode) -> bool:
        return inputCode in self.keys.keys()

    def _handle_not_existing(self, buttonBinding, inputCode):
        # check if a button was assigned to that behaviour
        key, newBinding = self._make_behaviour_key_and_set_binding(buttonBinding, inputCode)
        return key, newBinding

    def _make_behaviour_key_and_set_binding(self, buttonBinding, inputCode):
        key = self.makeAnimalBehavKey(buttonBinding)
        oldBehaviourBinding = self.behavAssignment[key]
        if oldBehaviourBinding.keyBinding != 'no button assigned':
            self._delete_old_behaviour_info(oldBehaviourBinding)
        key, newBinding = self._get_behaviour_and_set_new_binding(buttonBinding, inputCode, key)
        # icon has to be attached here as well
        newBinding.device = self.selected_device
        return key, newBinding

    def _get_behaviour_and_set_new_binding(self, buttonBinding, inputCode, key):
        key = 'A' + str(buttonBinding.animal) + '_' + buttonBinding.behaviour
        newBinding = copy.deepcopy(self.behavAssignment[key])
        newBinding.animal = buttonBinding.animal
        newBinding.behaviour = buttonBinding.behaviour
        newBinding.color = buttonBinding.color
        newBinding.keyBinding = inputCode
        return key, newBinding

    def _delete_old_behaviour_info(self, oldBehaviourBinding):
        oldButtonBinding = self.keys[oldBehaviourBinding.keyBinding]
        oldButtonBinding.color = '#C0C0C0'
        oldButtonBinding.animal = None
        oldButtonBinding.behaviour = None
        self.keys.update({oldBehaviourBinding.keyBinding: oldButtonBinding})

    def _handle_already_existing(self, buttonBinding, inputCode):
        # get old button binding object
        oldButtonBinding = self.keys[inputCode]
        # we check if there was already a behaviour attached to this button
        if oldButtonBinding.behaviour is not None:
            # the button binding also in the behavAssignment
            key = self.makeAnimalBehavKey(oldButtonBinding)
            oldBehaviourBinding = self.behavAssignment[key]
            oldBehaviourBinding.keyBinding = 'no button assigned'
            self.behavAssignment.update({key: oldBehaviourBinding})
        key, newBinding = self._make_behaviour_key_and_set_binding(buttonBinding, inputCode)
        # update both lists
        self.behavAssignment.update({key: newBinding})
        self.keys.update({inputCode: copy.deepcopy(newBinding)})
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
        self.makeBehaviourSummary()

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
        self._current_keys[self.deviceLayout] = self.keys.copy()
        self.deviceLayout = device
        self.initializeKeys(device)
        self.pixmap = QPixmap(DEVICES[str(device)])
        self.background_image.setPixmap(self.pixmap.scaled(self.background_image.size(), Qt.KeepAspectRatio))
        self.background_image.setScaledContents(True)
        self.make_joystick_info()
        self.makeBehaviourSummary()

    def initializeKeys(self, device):
        self.keys.clear()
        if device == "X-Box":
            if self._current_keys['X-Box'] is None:
                self._set_up_xbox_keys()
            else:
                self.keys = self._current_keys['X-Box']
        elif device == "Playstation":
            if self._current_keys['Playstation'] is None:
                self._set_up_playstation_keys()
            else:
                self.keys = self._current_keys['Playstation']
        elif device == "Keyboard":
            if self._current_keys['Keyboard'] is None:
                self._set_up_keyboard_keys()
            else:
                self.keys = self._current_keys['Keyboard']

    def _set_up_playstation_keys(self):
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
        self.keys = {"B0": BehavBinding(device=self.selected_device, key_binding="B0", color='#C0C0C0'),
                     "B1": BehavBinding(device=self.selected_device, key_binding="B1", color='#C0C0C0'),
                     "B2": BehavBinding(device=self.selected_device, key_binding="B2", color='#C0C0C0'),
                     "B3": BehavBinding(device=self.selected_device, key_binding="B3", color='#C0C0C0'),
                     "B4": BehavBinding(device=self.selected_device, key_binding="B4", color='#C0C0C0'),
                     "B5": BehavBinding(device=self.selected_device, key_binding="B5", color='#C0C0C0'),
                     "B6": BehavBinding(device=self.selected_device, key_binding="B6", color='#C0C0C0'),
                     "B7": BehavBinding(device=self.selected_device, key_binding="B7", color='#C0C0C0'),
                     "B8": BehavBinding(device=self.selected_device, key_binding="B8", color='#C0C0C0'),
                     "B9": BehavBinding(device=self.selected_device, key_binding="B9", color='#C0C0C0'),
                     "H01": BehavBinding(device=self.selected_device, key_binding="H01", color='#C0C0C0'),
                     "H0-1": BehavBinding(device=self.selected_device, key_binding="H0-1", color='#C0C0C0'),
                     "H-10": BehavBinding(device=self.selected_device, key_binding="H-10", color='#C0C0C0'),
                     "H10": BehavBinding(device=self.selected_device, key_binding="H10", color='#C0C0C0')}
        standardKeys = ["B10", "B11", "A0+", "A0-", "A1-", "A1+", "A3+", "A3-", "A4-", "A4+"]
        movieBehavs = ["toggleRunMov", "stopToggle", "runMovForward", "runMovReverse",
                       "changeFPShigh", "changeFPSlow", "changeFrameNoHigh1", "changeFrameNoLow1",
                       "changeFrameNoHigh10", "changeFrameNoLow10"]
        self.fillStandardKeys(standardKeys, movieBehavs)

    def _set_up_xbox_keys(self):
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
        self.keys = {"B0": BehavBinding(device=self.selected_device, key_binding="B0", color='#C0C0C0'),
                     "B1": BehavBinding(device=self.selected_device, key_binding="B1", color='#C0C0C0'),
                     "B2": BehavBinding(device=self.selected_device, key_binding="B2", color='#C0C0C0'),
                     "B3": BehavBinding(device=self.selected_device, key_binding="B3", color='#C0C0C0'),
                     "B4": BehavBinding(device=self.selected_device, key_binding="B4", color='#C0C0C0'),
                     "B5": BehavBinding(device=self.selected_device, key_binding="B5", color='#C0C0C0'),
                     "B6": BehavBinding(device=self.selected_device, key_binding="B6", color='#C0C0C0'),
                     "B7": BehavBinding(device=self.selected_device, key_binding="B7", color='#C0C0C0'),
                     "B8": BehavBinding(device=self.selected_device, key_binding="B8", color='#C0C0C0'),
                     "A2+": BehavBinding(device=self.selected_device, key_binding="A2+", color='#C0C0C0'),
                     "A5+": BehavBinding(device=self.selected_device, key_binding="A5+", color='#C0C0C0'),
                     "A2-": BehavBinding(device=self.selected_device, key_binding="A2-", color='#C0C0C0'),
                     "A5-": BehavBinding(device=self.selected_device, key_binding="A5-", color='#C0C0C0'),
                     "H01": BehavBinding(device=self.selected_device, key_binding="H01", color='#C0C0C0'),
                     "H0-1": BehavBinding(device=self.selected_device, key_binding="H0-1", color='#C0C0C0'),
                     "H-10": BehavBinding(device=self.selected_device, key_binding="H-10", color='#C0C0C0'),
                     "H10": BehavBinding(device=self.selected_device, key_binding="H10", color='#C0C0C0')}
        standardKeys = ["B9", "B10", "A0+", "A0-", "A1-", "A1+", "A3+", "A3-", "A4-", "A4+"]
        movieBehavs = ["toggleRunMov", "stopToggle", "runMovForward", "runMovReverse",
                       "changeFPShigh", "changeFPSlow", "changeFrameNoHigh1", "changeFrameNoLow1",
                       "changeFrameNoHigh10", "changeFrameNoLow10"]
        self.fillStandardKeys(standardKeys, movieBehavs)

    def _set_up_keyboard_keys(self):
        movie_keys = {
            'k': "toggleRunMov",
            'l': "runMovForward",
            'j': "runMovReverse",
            '.': "changeFPShigh",
            ',': "changeFPSlow",
            'i': "stopToggle",
            'o': "changeFrameNoHigh1",
            'u': "changeFrameNoLow1",
            '[': "changeFrameNoLow10",
            ']': "changeFrameNoHigh10"
        }
        self.fillStandardKeys(list(movie_keys.keys()), list(movie_keys.values()))

    def fillStandardKeys(self, standardKeys, movieBehavs):
        """
        This function adds the standard movie behaviour functions to the self.keys dict,
        using preset keys
        """

        for i in range(len(standardKeys)):
            self.behavAssignment['Amovie_' + movieBehavs[i]].device = self.selected_device
            self.behavAssignment['Amovie_' + movieBehavs[i]].keyBinding = standardKeys[i]
            temp = copy.deepcopy(self.behavAssignment['Amovie_' + movieBehavs[i]])
            temp.device = self.selected_device
            temp.keyBinding = standardKeys[i]
            self.keys.update({standardKeys[i]: temp})

            # idx = self.IndexOfDictList(self.bindingList,'behaviour',movieBehavs[i])
            # self.bindingList[idx].update('keyBinding':standardKeys[i])
            # self.bindingList[idx].update('device': self.selected_device)

    @staticmethod
    def makeAnimalBehavKey(obj):
        return 'A' + str(obj.animal) + '_' + obj.behaviour

    def initialiseBehavAssignment(self):
        self.behavAssignment.clear()

        for animalI in range(len(self.animal_tabs)):
            behavDict = self.animal_tabs[animalI].behaviour_dicts

            # add all behaviours
            for i in range(len(behavDict)):
                temp = BehavBinding(animal=animalI,
                                    icon_path=behavDict[i]['icon'],
                                    behaviour=behavDict[i]['name'],
                                    color=behavDict[i]['color'],
                                    key_binding='no button assigned',
                                    device=None)

                self.behavAssignment.update({'A' + str(animalI) + '_' + behavDict[i]['name']: temp})

            # add delete function
            temp = BehavBinding(animal=animalI,
                                icon_path=None,
                                behaviour='delete',
                                color='#ffffff',
                                key_binding='no button assigned',
                                device=None)

            self.behavAssignment.update({'A' + str(animalI) + '_delete': temp})

        # add movie behaviours    
        movieBehavs = ['toggleRunMov', 'stopToggle', 'runMovReverse', 'runMovForward',
                       'changeFPSlow', 'changeFPShigh', 'changeFrameNoLow1',
                       'changeFrameNoHigh1', 'changeFrameNoLow10', 'changeFrameNoHigh10']
        for behavI in movieBehavs:
            temp = BehavBinding(animal=BehavBinding.ANIMAL_MOVIE,
                                color='#ffffff',
                                icon_path=None,
                                behaviour=behavI,
                                key_binding=None,
                                device=None)
            self.behavAssignment.update({"Amovie_" + behavI: temp})

    def close_event(self):
        self.save_button_assignments(filename=HOME + '/.pyvisor/guidefaults_buttons.json')

    def resizeEvent(self, event):
        self.background_image.resize(event.size())

    def getAssignments(self):
        return self.keys, self.behavAssignment

    def getSelectedLayout(self):
        return self.deviceLayout

    def reset_buttons(self):
        self._get_and_initialize_behaviour()
        self._initialize_joystick()
        self.makeBehaviourSummary()

    def _initialize_joystick(self):
        # Get count of joysticks
        self.n_joysticks = pygame.joystick.get_count()
        # variables
        self.hatsNum = []
        self.buttonsNum = []
        self.axesNum = []
        self.input_device_names = []
        for i in range(self.n_joysticks):
            self.joystick = pygame.joystick.Joystick(i)
            self.joystick.init()
            # count the axes
            self.axesNum.append(self.joystick.get_numaxes())
            self.buttonsNum.append(self.joystick.get_numbuttons())
            self.hatsNum.append(self.joystick.get_numhats())
            self.input_device_names.append(self.joystick.get_name())
        self.input_device_names.append('Keyboard')

    def _init_ui(self):
        self._get_and_initialize_behaviour()
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
        self.parent.tabs.currentChanged.connect(self.makeBehaviourSummary)

    def _fill_major_boxes_with_infos(self):
        self.make_joystick_info()
        self.makeBehaviourSummary()
        self.make_device_choice()
        self.make_load_save_preset()

    def _add_layouts_to_central_vertical_box(self):
        self.vbox.addStretch()
        self.vbox.addLayout(self.hboxDeviceChoice)
        self.vbox.addLayout(self.hboxConciseBehav)
        self.vbox.addLayout(self.hboxLoadSavePreset)
        self.vbox.addLayout(self.hboxJoyStickInfo)
        self.vbox.addStretch()

    def _make_major_boxes(self):
        self.vbox = QVBoxLayout()
        self.hboxDeviceChoice = QHBoxLayout()
        self.hboxConciseBehav = QHBoxLayout()
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
        self.behavAssignment = BehaviourAssignments()
        self.animal_tabs = self.parent.get_animal_tabs()
        self.selected_device = None
        self.deviceLayout = None
        self.deviceNumber = -2
        self.initialiseBehavAssignment()
        self.lastKeyPressed = (71, 'G')


class BehaviourAssignments:

    def __init__(self):
        self.assignments = dict()

    def get_button_assignments(self) -> Dict[str, BehavBinding]:
        button_assignments = {}
        for label in self.assignments:
            binding = self.assignments[label]
            button = binding.keyBinding
            button_assignments[button] = binding
        return button_assignments

    def all_actions_have_buttons_assigned(self, animal_behaviours: List[str], movie_commands: List[str]) -> bool:
        for ab in animal_behaviours:
            if ab not in self:
                return False
        for mc in movie_commands:
            if mc not in self:
                return False
        return True

    def __contains__(self, item: str):
        for key in self.assignments.keys():
            if key == item:
                return True
        return False

    def __setitem__(self, key: str, value: BehavBinding):
        if key != value.keyBinding:
            raise ValueError("key {} does not match key binding {}".format(key, value.keyBinding))
        self.assignments[key] = value

    def __getitem__(self, item: str) -> BehavBinding:
        return self.assignments[item]
