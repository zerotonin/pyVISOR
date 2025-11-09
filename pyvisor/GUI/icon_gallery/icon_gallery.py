from PyQt5.QtCore import QSize
#from PyQt5.QtGui import 
from PyQt5.QtWidgets import QScrollArea, QWidget, QGridLayout, QButtonGroup
import glob

from .icon_button import IconButton
from ... import icon

class IconGallery(QScrollArea):
    
    def __init__(self, _dir, background_color=(0, 0, 0),
                 icon_size_px=(96, 96), cols=4):

        super(IconGallery, self).__init__()
        
        self.bg_color = background_color
        self.icon_size = icon_size_px
        self.icon_buttons = []
        self.ICONS_TO_DELETE = []
        self.selected_icon_index = None
        self.init_ui(_dir, cols)

    def get_current_icon(self):
        path_to_icon = self.icon_buttons[self.selected_icon_index].path_to_icon_template
        return path_to_icon
        
    def init_ui(self, _dir, cols):        
        icon_paths = glob.glob(_dir + "/*")
        n = len(icon_paths)            
        w = QWidget()
        grid = QGridLayout()
        w.setLayout(grid)
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        for i in range(n):
            row, column = (i / cols, i % cols)
            tmp_icon_path = icon.write_tmp_icon(icon_paths[i], self.bg_color)
            if tmp_icon_path is None:
                continue
            self.ICONS_TO_DELETE.append(tmp_icon_path)
            new_icon_button = IconButton(self,
                                         str(tmp_icon_path),
                                         icon_paths[i])
            new_icon_button.setIconSize(QSize(*self.icon_size))                        
            grid.addWidget(new_icon_button, row, column)
            new_icon_button.index_in_parent_list = i
            self.icon_buttons.append(new_icon_button)
            self.button_group.addButton(new_icon_button)
        self.setWidget(w)
