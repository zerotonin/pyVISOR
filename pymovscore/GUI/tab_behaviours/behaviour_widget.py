from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QFrame, QGridLayout,
                             QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel,
                             QFileDialog, QLineEdit,
                             QCheckBox, QColorDialog)
import os
from .compatible_behaviour_widget import CompatibleBehaviourWidget
from ..icon_gallery.icon_selection_widget import IconSelectionWidget
from ...icon import write_tmp_icon

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


class BehaviourWidget(QFrame):

    def __init__(self, parent, param_dict,
                 index_in_parent_list):
        super(BehaviourWidget, self).__init__()        
        self.param_dict = param_dict
        self.parent = parent
        self.index = index_in_parent_list
        self.init_UI()

    def init_UI(self):        
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.grid = QGridLayout()
        self.vbox.addLayout(self.hbox)        
        self.hbox.addLayout(self.grid)
        self.setLayout(self.vbox)

        # ------------------------
        #       button name 
        # ------------------------
        self.btn_name = QPushButton(self.param_dict['name'])
        self.btn_name.clicked.connect(self.rename)
        self.grid.addWidget(self.btn_name,
                            0, 0, 1, 2)
        # ------------------------
        #       color line 
        # ------------------------    
        lbl_color = QLabel('color')
        self.grid.addWidget(lbl_color,
                            1, 1, 1, 1)        
        self.btn_color = QPushButton('  ')
        self.btn_color.clicked.connect(self.set_color)
        if not self.param_dict['color']:
            self.param_dict['color'] = '#000000'
        self.btn_color.setStyleSheet("QWidget { background-color: %s}" % self.param_dict['color'])
        self.grid.addWidget(self.btn_color,
                            1, 0)

        # ------------------------
        #       icon line
        # ------------------------
        lbl_icon = QLabel('icon')
        self.grid.addWidget(lbl_icon,
                            2, 1, 1, 1)
        self.btn_icon = QPushButton('')
        self.current_icon = self.param_dict['icon']
        if self.current_icon:
            color_str = self.param_dict['color']
            color_tuple = (int(color_str[1: 3], 16),
                           int(color_str[3: 5], 16),
                           int(color_str[5: 7], 16))
            tmp_icon_str = write_tmp_icon(self.current_icon,
                                          color_tuple)
            self.btn_icon.setIcon(QIcon(HOME + "/.pymovscore/.tmp_icons/" + tmp_icon_str))        
        self.btn_icon.clicked.connect(self.set_icon_via_gallery)
        self.grid.addWidget(self.btn_icon,
                            2, 0)        
        # ------------------------
        #       btn remove
        # ------------------------
        self.hbox.addStretch(1)
        vbox_remove = QVBoxLayout()
        self.btn_remove = QPushButton('', self)
        self.btn_remove.setIcon(QIcon(HERE + '/../../../resources/icons/game/del.png'))
        self.btn_remove.clicked.connect(self.remove)
        vbox_remove.addWidget(self.btn_remove)
        vbox_remove.addStretch(1)
        self.hbox.addLayout(vbox_remove)

        # ---------------------------------
        #     compatible behaviour
        #          selection
        # ---------------------------------
        self.compatible_behaviour_widget = CompatibleBehaviourWidget(self)
        self.vbox.addWidget(self.compatible_behaviour_widget)

    def create_new_compatible_behaviour_widget(self):
        self.vbox.removeWidget(self.compatible_behaviour_widget)
        self.compatible_behaviour_widget.deleteLater()
        self.compatible_behaviour_widget = CompatibleBehaviourWidget(self)
        self.vbox.addWidget(self.compatible_behaviour_widget)
        
    def remove(self):        
        self.parent.remove_widget(self.index)
        
    def set_icon(self):
        icon = QFileDialog.getOpenFileName(self,
                                           'select icon',
                                           self.param_dict['icon'])        
        if icon:
            self.param_dict['icon'] = str(icon)
        self.btn_icon.setIcon(QIcon(self.param_dict['icon']))

    def set_icon_via_gallery(self):
        color_str = self.param_dict['color']
        color_tuple = (int(color_str[1: 3], 16),
                       int(color_str[3: 5], 16),
                       int(color_str[5: 7], 16))
        gallery = IconSelectionWidget(self, color_tuple)
        gallery.exec_()
        if not gallery.accept:
            return
        self.current_icon = gallery.get_current_icon()
        self.param_dict['icon'] = self.current_icon        
        tmp_icon_str = write_tmp_icon(self.current_icon,
                                      color_tuple)
        self.btn_icon.setIcon(QIcon(HOME + "/.pymovscore/.tmp_icons/" + tmp_icon_str))

    def set_color(self):
        color = QColorDialog.getColor()
        self.btn_color.setStyleSheet("QWidget { background-color: %s}" % color.name())
        self.param_dict['color'] = str(color.name())
        color_str = self.param_dict['color']
        color_tuple = (int(color_str[1: 3], 16),
                       int(color_str[3: 5], 16),
                       int(color_str[5: 7], 16))
        tmp_icon_str = write_tmp_icon(self.current_icon,
                                      color_tuple)
        self.btn_icon.setIcon(QIcon(HOME + "/.pymovscore/.tmp_icons/" + tmp_icon_str))

    def rename(self):
        self.name_edit = QLineEdit(self.btn_name.text())
        self.grid.addWidget(self.name_edit,
                            0, 0, 1, 2)
        self.name_edit.returnPressed.connect(self.rename_finished)

    def rename_finished(self):
        self.btn_name.setText(self.name_edit.text())
        self.param_dict['name'] = str(self.name_edit.text())
        self.name_edit.hide()

    def makeDisjunctionCheckbox(self, behavName):    
        b1 = QCheckBox(behavName)
        b1.setChecked(False)
        b1.stateChanged.connect(lambda: self.buttonStateChange(b1))
    
    def buttonStateChange(self, b1):
        pass
