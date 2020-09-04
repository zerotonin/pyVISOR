from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



class IconButton(QPushButton):

    def __init__(self, parent, path_to_icon, path_to_icon_template):
        super(IconButton, self).__init__()
        self.index_in_parent_list = None
        self.setCheckable(True)
        self.parent = parent
        self.setFixedSize(*parent.icon_size)
        self.setIcon(QIcon(path_to_icon))
        self.setIconSize(QSize(*parent.icon_size))
        self.path_to_icon = path_to_icon
        self.path_to_icon_template = path_to_icon_template
        self.toggled.connect(self.state_changed)
        self.setStyleSheet("QPushButton:checked { background-color: black}")

    def state_changed(self, state):        
        self.parent.selected_icon_index = self.index_in_parent_list
