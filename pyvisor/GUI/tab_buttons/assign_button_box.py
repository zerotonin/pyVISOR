import pygame
from PyQt5.QtGui import QPixmap, QCloseEvent
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QMessageBox, QWidget, QInputDialog

from ..model.behaviour import Behaviour
from ..model.gui_data_interface import GUIDataInterface
from ..model.scorer_action import ScorerAction


class AssignButtonBox(QWidget):

    def __init__(self,
                 parent_widget: QWidget,
                 gui_data_interface: GUIDataInterface,
                 action: ScorerAction,
                 color: str,
                 is_behaviour: bool):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.gui_data_interface = gui_data_interface
        self.action = action
        self.color = color
        self._init_callbacks(gui_data_interface)
        self.is_behaviour = is_behaviour
        self._init_UI()

    def _init_callbacks(self, gui_data_interface):
        self._callback_id_binding = gui_data_interface.register_callback_key_binding_changed(
            self.button_assignment_changed)
        self._callback_id_color = gui_data_interface.callbacks_behaviour_color_changed.register(
            self.set_color
        )
        self._callback_id_icon = gui_data_interface.callbacks_update_icon.register(
            self._set_icon
        )
        self._callback_id_name = gui_data_interface.callbacks_behaviour_name_changed.register(
            self._set_name
        )
        self._callback_id_removed = gui_data_interface.callbacks_behaviour_removed.register(
            self.remove
        )

    def remove(self, behaviour: Behaviour):
        if behaviour is self.action:
            self.close()

    def _set_name(self, action: ScorerAction):
        if action is not self.action:
            return
        self.behav_label.setText(action.name)

    def set_color(self, action: ScorerAction):
        if action is not self.action:
            return
        assert self.is_behaviour
        self.color = action.color
        self.behav_label.setStyleSheet('color: ' + self.color)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.gui_data_interface.callbacks_key_binding_changed.pop(self._callback_id_binding)
        self.gui_data_interface.callbacks_update_icon.pop(self._callback_id_icon)
        self.gui_data_interface.callbacks_behaviour_color_changed.pop(self._callback_id_color)
        self.gui_data_interface.callbacks_behaviour_name_changed.pop(self._callback_id_name)
        self.gui_data_interface.callbacks_behaviour_removed.pop(self._callback_id_removed)

    def _init_UI(self):
        self.box = QHBoxLayout()
        self.behav_label = QLabel(self.action.name)
        self.behav_label.setStyleSheet('color: ' + self.color)
        btn_set_uic = QPushButton('assign button')
        btn_set_uic.clicked.connect(self.assign_button)
        self._create_button_label()
        if self.is_behaviour:
            self._create_icon()
            self.box.addWidget(self.imageLabel)
        self.box.addWidget(self.behav_label)
        self.box.addWidget(btn_set_uic)
        self.box.addWidget(self.button_label)
        self.setLayout(self.box)

    def _set_icon(self, behaviour: Behaviour):
        if behaviour is not self.action:
            return
        pixmap = QPixmap(self.action.icon_path)
        pixmap = pixmap.scaledToWidth(20)
        self.imageLabel.setPixmap(pixmap)

    def _create_icon(self):
        self.imageLabel = QLabel()
        if self.action.icon_path is None:
            return
        pixmap = QPixmap(self.action.icon_path)
        pixmap = pixmap.scaledToWidth(20)
        self.imageLabel.setStyleSheet('color: ' + self.color)
        self.imageLabel.setPixmap(pixmap)

    def _create_button_label(self):
        key = self.action.key_bindings[self.gui_data_interface.selected_device]
        label = 'no button\nassigned' if key is None else key
        self.button_label = QLabel(self)
        if key is None:
            self.button_label.setStyleSheet('color: #C0C0C0')
        else:
            self.button_label.setStyleSheet('color: #ffffff')
        self.button_label.setText(label)

    def assign_button(self):
        if self.gui_data_interface.selected_device is None:
            QMessageBox.warning(self.parent_widget, 'Set device first!',
                                "You need to choose an input device first",
                                QMessageBox.Ok)
            return

        if self.gui_data_interface.selected_device == "Keyboard":
            text, ok = QInputDialog.getText(self.parent(), 'Press', 'Key Entry:')
            if not ok:
                return
            button_identifier = str(text)
        else:
            button_identifier = self.waitOnUICpress()

        assigned_action, is_behaviour = self.gui_data_interface.get_action_assigned_to(
            button_identifier)

        if assigned_action is not None:
            self.gui_data_interface.change_button_binding(assigned_action,
                                                          None,
                                                          is_behaviour)
        self.gui_data_interface.change_button_binding(self.action, button_identifier, self.is_behaviour)

    def button_assignment_changed(self, action: ScorerAction, is_behaviour: bool):
        if action is not self.action:
            return
        self.button_label.setText(action.key_bindings[self.gui_data_interface.selected_device])

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
