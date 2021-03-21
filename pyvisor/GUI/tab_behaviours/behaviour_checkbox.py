from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QCheckBox, QWidget

from ..model.behaviour import Behaviour
from ..model.gui_data_interface import GUIDataInterface


class BehaviourCheckbox(QCheckBox):

    def __init__(self, parent: QWidget,
                 this_behaviour: Behaviour,
                 other_behaviour: Behaviour,
                 initial_state: bool,
                 gui_data_interface: GUIDataInterface):
        super().__init__(other_behaviour.name, parent)
        self.this_behaviour = this_behaviour
        self.other_behaviour = other_behaviour
        self.gui_data_interface = gui_data_interface
        self.callback_id = self.gui_data_interface.register_callback_compatibility_changed(self.compatibility_changed)
        self.init_UI(initial_state)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.gui_data_interface.callbacks_animal_added.pop(self.callback_id)
        super().closeEvent(a0)

    def init_UI(self, initial_state):
        self.setChecked(initial_state)
        self._connect()

    def _connect(self):
        self.clicked.connect(lambda : self.gui_data_interface.set_compatibility(self.this_behaviour,
                                                                                self.other_behaviour,
                                                                                self.isChecked()))

    def _disconnect(self):
        self.toggled.connect(lambda state: print(state))

    def compatibility_changed(self, behav1: Behaviour, behav2: Behaviour):
        if behav1 is not self.this_behaviour and behav1 is not self.other_behaviour:
            return
        if behav2 is not self.this_behaviour and behav2 is not self.other_behaviour:
            return
        self.setChecked(behav1.name in behav2.compatible_with)