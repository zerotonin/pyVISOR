from PyQt5.QtWidgets import QCheckBox


class BehaviourCheckbox(QCheckBox):

    def __init__(self, parent, name, initial_state):
        super(BehaviourCheckbox, self).__init__(name)
        self.parent = parent        
        self.init_UI(initial_state)

    def init_UI(self, initial_state):
        self.setChecked(initial_state)
        self.toggled.connect(
            lambda: self.parent.compatibility_toggled(
                str(self.text()), self.isChecked()))
