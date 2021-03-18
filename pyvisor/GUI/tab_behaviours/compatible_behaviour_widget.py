from PyQt5.QtWidgets import QWidget, QGridLayout
from .behaviour_checkbox import BehaviourCheckbox
from ..model.animal_handler import AnimalHandler
from ..model.behaviour import Behaviour
from ...exception.behaviour_already_in_compatibility_list_exception \
    import BehaviourAlreadyInCompatibilityListException
from ...exception.behaviour_not_in_compatibility_list_exception \
    import BehaviourNotInCompatibilityListException


class CompatibleBehaviourWidget(QWidget):

    def __init__(self, parent_behaviour_widget, behaviour: Behaviour,
                 animal_handler: AnimalHandler):
        super(CompatibleBehaviourWidget, self).__init__()
        self.parent_behaviour_widget = parent_behaviour_widget
        self.behaviour = behaviour
        self.animal_handler = animal_handler
        self.behaviour_checkboxes = {}
        self.init_UI()
        self.suppress_actions = False

    def init_UI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        animal = self.animal_handler.animals[self.behaviour.animal]
        for key in animal.behaviours:
            behav = animal.behaviours[key]
            if behav.name == self.behaviour.name:
                continue
            self.add_checkbox(
                behav.name,
                (self.behaviour.compatible_with.count(behav.name) > 0)
            )

    def add_checkbox(self, name, state):
        checkbox_widget = BehaviourCheckbox(self, name, state)
        self.grid.addWidget(checkbox_widget,
                            *self._get_grid_pos(len(self.behaviour_checkboxes)))
        self.behaviour_checkboxes[name] = checkbox_widget

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
