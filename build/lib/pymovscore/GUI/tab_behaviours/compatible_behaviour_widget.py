from PyQt5.QtWidgets import QWidget, QGridLayout
from .behaviour_checkbox import BehaviourCheckbox
from ...exception.behaviour_already_in_compatibility_list_exception \
    import BehaviourAlreadyInCompatibilityListException
from ...exception.behaviour_not_in_compatibility_list_exception \
    import BehaviourNotInCompatibilityListException


class CompatibleBehaviourWidget(QWidget):

    def __init__(self, parent_behaviour_widget):
        super(CompatibleBehaviourWidget, self).__init__()
        self.parent = parent_behaviour_widget
        self.compatible = self.parent.param_dict['compatible']
        self.behaviour_checkboxes = {}
        self.init_UI()
        self.suppress_actions = False

    def init_UI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)        
        for d in self.parent.parent.behaviour_dicts:
            name = d['name']
            if name == self.parent.param_dict['name']:
                continue
            self.add_checkbox(name, (self.compatible.count(name) > 0))            

    def add_checkbox(self, name, state):
        checkbox_widget = BehaviourCheckbox(self, name, state)
        self.grid.addWidget(checkbox_widget, *self._get_grid_pos(len(self.behaviour_checkboxes)))
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
        
    def _get_grid_pos(self, count):
        return [count / 2, count % 2]

    def compatibility_toggled(self, name, state):
        if self.suppress_actions:
            return
        this_name = self.parent.param_dict['name']
        other_behav_widget = self.parent.parent.get_behav_widget_by_name(name)
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
        if self.compatible.count(behav_name):
            raise BehaviourAlreadyInCompatibilityListException(
                self.parent.param_dict['name'], behav_name)
        self.compatible.append(behav_name)

    def remove_compatibility(self, behav_name):
        if not self.compatible.count(behav_name):
            raise BehaviourNotInCompatibilityListException(
                self.parent.param_dict['name'], behav_name)
        self.compatible.remove(behav_name)
