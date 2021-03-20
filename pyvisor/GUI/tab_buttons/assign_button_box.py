import pygame
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QMessageBox, QWidget, QInputDialog

from ..model.gui_data_interface import GUIDataInterface
from ..model.scorer_action import ScorerAction


class AssignButtonBox(QHBoxLayout):

    def __init__(self,
                 parent_widget: QWidget,
                 gui_data_interface: GUIDataInterface,
                 action: ScorerAction,
                 color: str,
                 is_behaviour: bool):
        super().__init__()
        self.parent_widget = parent_widget
        self.gui_data_interface = gui_data_interface
        gui_data_interface.register_callback_key_binding_changed(self.button_assignment_changed)
        self.action = action
        self.color = color
        self.is_behaviour = is_behaviour
        self._init_UI()

    def _init_UI(self):
        behav_label = QLabel(self.action.name)
        behav_label.setStyleSheet('color: ' + self.color)
        btn_set_uic = QPushButton('assign button/key')
        btn_set_uic.clicked.connect(self.assign_button
                                    )
        self.button_label = self._create_button_label()
        if self.is_behaviour:
            if self.action.icon_path is not None:
                self.icon_label = self._create_icon()
                self.addWidget(self.icon_label)
        self.addWidget(behav_label)
        self.addWidget(btn_set_uic)
        self.addWidget(self.button_label)

    def _create_icon(self):
        imageLabel = QLabel()
        pixmap = QPixmap(self.action.icon_path)
        pixmap = pixmap.scaledToWidth(20)
        imageLabel.setStyleSheet('color: ' + self.color)
        imageLabel.setPixmap(pixmap)
        return imageLabel

    def _create_button_label(self):
        key = self.action.key_bindings[self.gui_data_interface.selected_device]
        label = 'no button assigned' if key is None else key
        button_label = QLabel(label)
        if key is None:
            button_label.setStyleSheet('color: #C0C0C0')
        else:
            button_label.setStyleSheet('color: #ffffff')
        return button_label

    def assign_button(self):
        if self.gui_data_interface.selected_device is None:
            QMessageBox.warning(self.parent_widget, 'Set device first!',
                                "You need to choose an input device first",
                                QMessageBox.Ok)
            return

        if self.gui_data_interface.selected_device == "Keyboard":
            text, ok = QInputDialog.getText(self.parent_widget, 'Press', 'Key Entry:')
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
