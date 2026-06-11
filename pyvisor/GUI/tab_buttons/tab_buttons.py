import os
from typing import Dict, List, Any

import pygame
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QComboBox, QPushButton, QScrollArea)

from pyvisor.GUI.model.animal import Animal
from pyvisor.GUI.model.behaviour import Behaviour
from pyvisor.GUI.model.gui_data_interface import GUIDataInterface
from pyvisor.GUI.model.scorer_action import ScorerAction
from pyvisor.GUI.tab_buttons.assign_button_box import AssignButtonBox
from pyvisor.resources import resource_path

HERE = os.path.dirname(os.path.abspath(__file__))

# noinspection PyAttributeOutsideInit
class TabButtons(QWidget):
    """Button Assignment tab — bind gamepad/keyboard inputs to actions.

    Detects connected input devices via pygame, lets the user
    assign physical buttons to behaviours and movie controls,
    and provides default binding presets per device type.
    """

    def __init__(self, parent: QWidget, gui_data_interface: GUIDataInterface):
        super(TabButtons, self).__init__(parent)
        self.analysis_list = []

        self.gui_data_interface = gui_data_interface
        self._callback_id_animal_added = self.gui_data_interface.callbacks_animal_added.register(
            self._create_animal_box
        )
        self._callback_id_animal_name_changed = self.gui_data_interface.callbacks_animal_name_changed.register(
            self._handle_animal_name_changed
        )
        self._callback_id_behav_added = self.gui_data_interface.callbacks_behaviour_added.register(
            self._handle_behaviour_added
        )
        self._callback_id_animal_removed = self.gui_data_interface.callbacks_animal_removed.register(
            self._handle_animal_removed
        )
        self._animal_info_boxes = {}  # type: Dict[int, QVBoxLayout]
        self._animal_name_labels = {}  # type: Dict[int, QLabel]
        self._behaviour_boxes = {}  # type: Dict[str, QWidget]
        self._movie_action_boxes = {}  # type: Dict[str, QWidget]
        self._animal_boxes = {}  # type: Dict[int, QVBoxLayout]

        pygame.init()
        # Initialize the joysticks
        pygame.joystick.init()
        self._initialize_device_members()
        self._init_ui()

    def _handle_animal_removed(self, animal: Animal):
        abox = self._animal_boxes[animal.number]
        self.hbox_animal_columns.removeItem(abox)

    def _handle_behaviour_added(self, animal: Animal, behaviour: Behaviour):
        self._create_box_single_behaviour(behaviour)

    def _handle_animal_name_changed(self, animal: Animal):
        self._animal_name_labels[animal.number].setText("{} (A{})".format(animal.name, animal.number))

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.gui_data_interface.callbacks_behaviour_added.pop(self._callback_id_behav_added)
        self.gui_data_interface.callbacks_animal_added.pop(self._callback_id_animal_added)
        self.gui_data_interface.callbacks_animal_name_changed.pop(self._callback_id_animal_name_changed)
        self.gui_data_interface.callbacks_animal_removed.pop(self._callback_id_animal_removed)

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
            animal_no_str = 'animal No {}'.format(behav_binding.animal_number)
        labels_list.append(QLabel(animal_no_str, self))
        labels_list.append(QLabel(behav_binding.name, self))
        # set labels to transparent background
        for i in range(3):
            labels_list[i].setStyleSheet(self.labelStyle)
        # adjust behaviour color
        labels_list[2].setStyleSheet('color: ' + behav_binding.color)
        # add widgets to layout !!! need to add Icon when implemented
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
        self.combo_input_assign.addItem("-- Select Input Device --")
        for device in self.input_device_names:
            self.combo_input_assign.addItem(device)
        self.combo_input_assign.setCurrentIndex(0)
        # add signal slot for assignment change
        self.combo_input_assign.activated[str].connect(self.set_device)
        self.hboxDeviceChoice.addWidget(self.lbl_input_assign)
        self.hboxDeviceChoice.addWidget(self.combo_input_assign)

        button_reset = QPushButton("Reset bindings")
        button_reset.setToolTip("Clear all button assignments for the current device.")
        button_reset.clicked.connect(self._reset_buttons)
        self.hboxDeviceChoice.addWidget(button_reset)

        button_default_bindings = QPushButton("Set default movie bindings")
        button_default_bindings.setToolTip("Assign standard movie control bindings\n"
                                            "for the selected device type.")
        button_default_bindings.clicked.connect(self._set_default_movie_bindings)
        self.hboxDeviceChoice.addWidget(button_default_bindings)

        button_device_info = QPushButton("Device info…")
        button_device_info.setToolTip("Show detected devices, axes, buttons,\n"
                                       "and current binding summary.")
        button_device_info.clicked.connect(self._show_device_info)
        self.hboxDeviceChoice.addWidget(button_device_info)

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
        from PyQt5.QtWidgets import QGridLayout
        movie_widget = QWidget(self)
        outer = QVBoxLayout(movie_widget)
        name_label = QLabel('movie actions')
        name_label.setStyleSheet(self.labelStyle)
        outer.addWidget(name_label)

        grid = QGridLayout()
        movie_assignments = self.gui_data_interface.movie_bindings
        sorted_names = sorted(movie_assignments.keys())
        n_cols = 2
        for idx, name in enumerate(sorted_names):
            movie_action = movie_assignments[name]
            color = "#d4d4d4"
            box = self._create_assign_button_box(color, movie_action, is_behaviour=False)
            self._movie_action_boxes[movie_action.name] = box
            grid.addWidget(box, idx // n_cols, idx % n_cols)
        outer.addLayout(grid)
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
        self.hbox_animal_columns.addWidget(movie_widget)
        self.hbox_animal_columns.addStretch()

    def _create_behaviours_box(self):
        self.behav_stepLabel = QLabel('Behaviours: ')
        self.behav_stepLabel.resize(20, 40)
        self.behav_stepLabel.setStyleSheet(self.labelStyle)
        self.hbox_animal_columns.addWidget(self.behav_stepLabel)
        for animal_number in sorted(self.gui_data_interface.animals):
            animal = self.gui_data_interface.animals[animal_number]
            self._create_animal_box(animal)

    def _create_animal_box(self, animal: Animal):
        vbox = self.make_animal_behaviour_box(animal)
        self._animal_boxes[animal.number] = vbox
        self.hbox_animal_columns.addLayout(vbox)

    def make_animal_behaviour_box(self, animal: Animal):
        # top label
        animal_box = QVBoxLayout()
        self._animal_info_boxes[animal.number] = animal_box
        name_label = QLabel(animal.name + ' (A' + str(animal.number) + ')')
        self._animal_name_labels[animal.number] = name_label
        name_label.setStyleSheet(self.labelStyle)
        animal_box.addWidget(name_label)

        if not animal.has_behaviour('delete'):
            del_icon = str(resource_path('icons', 'game', 'del.png'))
            behav_delete = Behaviour(animal_number=animal.number,
                                     name="delete",
                                     icon_path=del_icon,
                                     color="#FF2222")
            animal[behav_delete.label] = behav_delete

        for key in sorted(animal.behaviours.keys()):
            behav = animal.behaviours[key]
            self._create_box_single_behaviour(behav)

        return animal_box

    def _create_box_single_behaviour(
            self,
            behaviour: Behaviour
    ):
        box = self._create_assign_button_box(
            behaviour.color,
            behaviour,
            is_behaviour=True
        )
        self._behaviour_boxes[behaviour.label] = box
        behavBox = self._animal_info_boxes[behaviour.animal_number]
        behavBox.addWidget(box)

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

    def set_assignDevice(self, device):
        device = str(device)
        if self.gui_data_interface.selected_device == device:
            return
        self.gui_data_interface.selected_device = device
        if device != "Keyboard":
            self.joystick = pygame.joystick.Joystick(self.deviceNumber)
            self.joystick.init()

    @staticmethod
    def _classify_device(name: str) -> str:
        """Map a pygame joystick name to an internal device category.

        The KeyBindings model stores bindings under 'X-Box', 'Playstation',
        'Keyboard', or 'Free'.  This helper maps detected hardware names
        to the correct category.
        """
        low = name.lower()
        if low == "keyboard":
            return "Keyboard"
        if any(tag in low for tag in ("xbox", "x-box", "xinput",
                                       "microsoft", "360")):
            return "X-Box"
        if any(tag in low for tag in ("playstation", "ps2", "ps3", "ps4",
                                       "ps5", "dualshock", "dualsense",
                                       "sony", "wireless controller")):
            return "Playstation"
        # Anything else (generic gamepads, 8BitDo, etc.)
        return "Free"

    def set_device(self, device: str):
        """Called when the user picks a device from the combo box."""
        device = str(device)
        if device.startswith("--"):
            return  # placeholder item
        category = self._classify_device(device)

        # Update the background image to the matching controller picture
        # (background images removed for cleaner UI)

        # Track which joystick index this is (for pygame init)
        if device in self.input_device_names:
            self.deviceNumber = self.input_device_names.index(device)

        # Update the central data model so assign_button sees the right category
        self.gui_data_interface.selected_device = category
        self.gui_data_interface.save_state()

        # Initialise the joystick if it is not the keyboard
        if category != "Keyboard" and self.deviceNumber >= 0:
            try:
                self.joystick = pygame.joystick.Joystick(self.deviceNumber)
                self.joystick.init()
            except pygame.error as exc:
                print("Could not initialise joystick {}: {}".format(
                    self.deviceNumber, exc))

    def _set_device(self, device):
        """Programmatic device switch (e.g. on startup)."""
        self.set_device(device)

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
            "B11": "toggleRunMov",
            "B12": "stopToggle",
            "A0+": "runMovForward",
            "A0-": "runMovReverse",
            "A1-": "changeFPShigh",
            "A1+": "changeFPSlow",
            "A3+": "changeFrameNoHigh1",
            "A3-": "changeFrameNoLow1",
            "A4-": "changeFrameNoHigh10",
            "A4+": "changeFrameNoLow10"
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
            "A1-": "changeFPShigh", "A1+": "changeFPSlow",
            "A3+": "changeFrameNoHigh1", "A3-": "changeFrameNoLow1",
            "A4-": "changeFrameNoHigh10", "A4+": "changeFrameNoLow10"
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

    def _show_device_info(self):
        """Show detected device details in a popup dialog."""
        from PyQt5.QtWidgets import QDialog, QTextEdit
        dlg = QDialog(self)
        dlg.setWindowTitle("Detected Input Devices")
        dlg.setMinimumSize(450, 350)
        layout = QVBoxLayout(dlg)
        text = QTextEdit()
        text.setReadOnly(True)

        lines = []
        for joyI in range(self.n_joysticks):
            name = self.input_device_names[joyI]
            category = self._classify_device(name)
            lines.append("<b>{}</b>  (mapped to: {})".format(name, category))
            lines.append("  Axes: {}  |  Buttons: {}  |  Hats: {}".format(
                self.axesNum[joyI], self.buttonsNum[joyI], self.hatsNum[joyI]))
            lines.append("  Axes: " + ", ".join(
                "A{}+/A{}-".format(i, i) for i in range(self.axesNum[joyI])))
            lines.append("  Buttons: " + ", ".join(
                "B{}".format(i) for i in range(self.buttonsNum[joyI])))
            if self.hatsNum[joyI] > 0:
                lines.append("  Hats: " + ", ".join(
                    "H{}".format(i) for i in range(self.hatsNum[joyI])))
            lines.append("")

        lines.append("<b>Keyboard</b> (always available)")
        lines.append("")

        if self.n_joysticks == 0:
            lines.insert(0, "<i>No gamepads detected. Plug in a controller "
                            "and restart pyVISOR.</i>")
            lines.insert(1, "")

        # Current bindings summary
        dev = self.gui_data_interface.selected_device
        if dev:
            lines.append("<b>Current bindings (device: {})</b>".format(dev))
            for an in sorted(self.gui_data_interface.animals.keys()):
                animal = self.gui_data_interface.animals[an]
                for label in sorted(animal.behaviours.keys()):
                    behav = animal.behaviours[label]
                    binding = behav.key_bindings[dev]
                    btn = binding if binding else "<i>unassigned</i>"
                    lines.append("  {} → {}".format(btn, behav.name))
            for action_name in sorted(self.gui_data_interface.movie_bindings.keys()):
                action = self.gui_data_interface.movie_bindings[action_name]
                binding = action.key_bindings[dev]
                btn = binding if binding else "<i>unassigned</i>"
                lines.append("  {} → {}".format(btn, action_name))

        text.setHtml("<pre style='font-size:11px'>" + "<br>".join(lines) + "</pre>")
        layout.addWidget(text)
        dlg.exec_()

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
        color: #d4d4d4;
        background-color: transparent;
        margin-top: 2px;
        font-weight: bold;
        """
        # fill major boxes with infos
        self._fill_major_boxes_with_infos()
        self.setLayout(self.vbox)

    def _fill_major_boxes_with_infos(self):
        self.make_animals_box()
        self.make_device_choice()

    def _add_layouts_to_central_vertical_box(self):
        self.vbox.addLayout(self.hboxDeviceChoice)

        # Wrap the assignment columns in a scroll area so the window stays compact
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll_content = QWidget()
        scroll_content.setLayout(self.hbox_animal_columns)
        scroll.setWidget(scroll_content)
        self.vbox.addWidget(scroll, stretch=1)

        self.vbox.addLayout(self.hboxLoadSavePreset)
        # Joystick detail info hidden — not useful for end users
        # self.vbox.addLayout(self.hboxJoyStickInfo)

    def _make_major_boxes(self):
        self.vbox = QVBoxLayout()
        self.hboxDeviceChoice = QHBoxLayout()
        self.hbox_animal_columns = QHBoxLayout()
        self.hboxJoyStickInfo = QHBoxLayout()
        self.hboxLoadSavePreset = QHBoxLayout()

    def _set_background_image(self):
        pass  # replaced by global dark theme

    def resizeEvent(self, event):  # noqa: F811  # intentionally overrides the earlier resize handler; background scaling disabled after the dark-theme refactor
        pass

    def _initialize_device_members(self):
        self.deviceNumber = -2
        self.lastKeyPressed = (71, 'G')
