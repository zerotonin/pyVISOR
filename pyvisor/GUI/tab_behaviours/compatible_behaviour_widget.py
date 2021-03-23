from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget, QGridLayout
from .behaviour_checkbox import BehaviourCheckbox
from ..model.animal import Animal
from ..model.gui_data_interface import GUIDataInterface
from ..model.behaviour import Behaviour
from ...exception.behaviour_already_in_compatibility_list_exception \
    import BehaviourAlreadyInCompatibilityListException
from ...exception.behaviour_not_in_compatibility_list_exception \
    import BehaviourNotInCompatibilityListException


class CompatibleBehaviourWidget(QWidget):

    def __init__(self, parent_behaviour_widget, behaviour: Behaviour,
                 gui_data_interface: GUIDataInterface):
        super().__init__()
        self.parent_behaviour_widget = parent_behaviour_widget
        self.behaviour = behaviour
        self.gui_data_interface = gui_data_interface
        self._callback_id_add = self.gui_data_interface.callbacks_behaviour_added.register(
            self._handle_behaviour_added
        )
        self.behaviour_checkboxes = {}
        self.init_UI()
        self.suppress_actions = False

    def _handle_behaviour_added(self, animal: Animal, behaviour: Behaviour):
        if behaviour.animal_number != self.behaviour.animal_number:
            return
        if self.behaviour.name == 'delete':
            return
        self.add_checkbox(behaviour, False)

    def _remove_callbacks(self):
        self.gui_data_interface.callbacks_behaviour_added.pop(self._callback_id_add)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self._remove_callbacks()

    def __del__(self):
        self._remove_callbacks()

    def init_UI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        animal = self.gui_data_interface.animals[self.behaviour.animal_number]
        for key in animal.behaviours:
            if self.behaviour.name == "delete":
                break
            behav = animal.behaviours[key]
            if behav.name == 'delete':
                continue
            if behav.name == self.behaviour.name:
                continue
            if self.behaviour.compatible_with is None:
                continue
            self.add_checkbox(
                behav,
                (self.behaviour.compatible_with.count(behav.name) > 0)
            )

    def add_checkbox(self, other_behaviour: Behaviour, state):
        if other_behaviour.label in self.behaviour_checkboxes:
            return
        checkbox_widget = BehaviourCheckbox(self, self.behaviour, other_behaviour, state, self.gui_data_interface)
        self.grid.addWidget(checkbox_widget,
                            *self._get_grid_pos(len(self.behaviour_checkboxes)))
        self.behaviour_checkboxes[other_behaviour.label] = checkbox_widget

    def remove_checkbox(self, name):
        w = self.behaviour_checkboxes.pop(name)
        ind = self.grid.indexOf(w)
        self.grid.removeWidget(w)
        w.deleteLater()
        self.rearrange_checkboxes_with_larger_index(ind)

    def rearrange_checkboxes_with_larger_index(self, index_):
        widgets = []
        for i in range(index_, self.grid.count()):
            w = self.grid.takeAt(i)
            if w is not None:
                widgets.append(w)
        count = index_
        for w in widgets:
            actual_widget = w.widget()
            self.grid.removeWidget(actual_widget)
            coords = self._get_grid_pos(count)
            self.grid.addWidget(actual_widget, *coords)
            count += 1

    @staticmethod
    def _get_grid_pos(count):
        return [count / 2, count % 2]

    def compatibility_toggled(self, name, state):
        if self.suppress_actions:
            return
        this_name = self.behaviour.name
        other_behav_widget = self.parent_behaviour_widget.parent.get_behav_widget_by_name(name)
        other_compatible_behav_widget = other_behav_widget.compatible_behaviour_widget
        other_checkbox = other_compatible_behav_widget.behaviour_checkboxes[
            this_name]
        other_compatible_behav_widget.suppress_actions = True
        if state:
            self.add_compatibility(name)
            other_compatible_behav_widget.add_compatibility(this_name)
            other_checkbox.setChecked(True)
        else:
            self.remove_compatibility(name)
            other_compatible_behav_widget.remove_compatibility(this_name)
            other_checkbox.setChecked(False)
        other_compatible_behav_widget.suppress_actions = False

    def add_compatibility(self, behav_name):
        if self.behaviour.compatible_with.count(behav_name):
            raise BehaviourAlreadyInCompatibilityListException(
                self.behaviour.name, behav_name)
        self.behaviour.compatible_with.append(behav_name)

    def remove_compatibility(self, behav_name):
        if not self.behaviour.compatible_with.count(behav_name):
            raise BehaviourNotInCompatibilityListException(
                self.behaviour.name, behav_name)
        self.behaviour.compatible_with.remove(behav_name)
