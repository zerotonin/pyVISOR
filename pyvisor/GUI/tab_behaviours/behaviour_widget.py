from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QFrame, QGridLayout,
                             QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel,
                             QFileDialog, QLineEdit,
                             QColorDialog, QMessageBox)
import os
from .compatible_behaviour_widget import CompatibleBehaviourWidget
from ..icon_gallery.icon_selection_widget import IconSelectionWidget
from ..model.gui_data_interface import GUIDataInterface, NameExistsException, NameIdenticalException
from ..model.behaviour import Behaviour
from ...icon import write_tmp_icon
from pyvisor.resources import resource_path

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


class BehaviourWidget(QFrame):

    def __init__(self, parent, behaviour: Behaviour,
                 index_in_parent_list,
                 gui_data_interface: GUIDataInterface):
        super().__init__(parent)
        self.gui_data_interface = gui_data_interface
        self.behaviour = behaviour
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

        self._init_name_button()
        self._init_color_row()
        self._init_icon_row()
        self._init_remove_button()

        self.compatible_behaviour_widget = CompatibleBehaviourWidget(
            self, self.behaviour, self.gui_data_interface)
        self.vbox.addWidget(self.compatible_behaviour_widget)

    def _init_remove_button(self):
        self.hbox.addStretch(1)
        vbox_remove = QVBoxLayout()
        self.btn_remove = QPushButton('', self)
        self.btn_remove.setIcon(QIcon(str(resource_path('icons', 'game', 'del.png'))))
        self.btn_remove.clicked.connect(self.remove)
        vbox_remove.addWidget(self.btn_remove)
        vbox_remove.addStretch(1)
        self.hbox.addLayout(vbox_remove)

    def _init_name_button(self):
        self.btn_name = QPushButton(self.behaviour.name)
        self.btn_name.clicked.connect(self.rename)
        self.grid.addWidget(self.btn_name,
                            0, 0, 1, 2)

    def _init_icon_row(self):
        lbl_icon = QLabel('Icon')
        self.grid.addWidget(lbl_icon,
                            2, 1, 1, 1)
        self.btn_icon = QPushButton('')
        self.current_icon = self.behaviour.icon_path
        if self.current_icon:
            self._set_icon_from_tmp_file()
        self.btn_icon.clicked.connect(self.set_icon_via_gallery)
        self.grid.addWidget(self.btn_icon,
                            2, 0)

    def _init_color_row(self):
        lbl_color = QLabel('color')
        self.grid.addWidget(lbl_color,
                            1, 1, 1, 1)
        self.btn_color = QPushButton('  ')
        self.btn_color.clicked.connect(self.set_color)
        if self.behaviour.color is None:
            self.behaviour.color = '#000000'
        self.btn_color.setStyleSheet(
            "QWidget { background-color: %s}" % self.behaviour.color)
        self.grid.addWidget(self.btn_color,
                            1, 0)

    def remove(self):        
        if self.behaviour.name == 'delete':
            QMessageBox.warning(self, 'Can\'t remove!',
                                "'delete' action can't be removed.",
                                QMessageBox.Ok)
            return
        self.parent().remove_widget(self.index, self.behaviour)
        self.close()

    def set_icon(self):
        icon = QFileDialog.getOpenFileName(self,
                                           'select Icon',
                                           self.behaviour.icon_path)
        if not icon:
            return
        self.gui_data_interface.set_icon(
            self.behaviour, str(icon)
        )
        self.btn_icon.setIcon(QIcon(self.behaviour.icon_path))

    def set_icon_via_gallery(self):
        color_str = self.behaviour.color
        color_tuple = (int(color_str[1: 3], 16),
                       int(color_str[3: 5], 16),
                       int(color_str[5: 7], 16))
        gallery = IconSelectionWidget(self, color_tuple)
        gallery.exec_()
        if not gallery.accept:
            return
        current_icon = gallery.get_current_icon()
        self.gui_data_interface.set_icon(self.behaviour, current_icon)
        tmp_icon_str = write_tmp_icon(self.behaviour.icon_path,
                                      color_tuple)
        self.btn_icon.setIcon(QIcon(HOME + "/.pyvisor/.tmp_icons/" + tmp_icon_str))

    def set_color(self):
        color = QColorDialog.getColor()
        self.btn_color.setStyleSheet("QWidget { background-color: %s}" % color.name())
        self.gui_data_interface.set_icon_color(self.behaviour, str(color.name()))
        self._set_icon_from_tmp_file()

    def _set_icon_from_tmp_file(self):
        color_str = self.behaviour.color
        color_tuple = (int(color_str[1: 3], 16),
                       int(color_str[3: 5], 16),
                       int(color_str[5: 7], 16))
        tmp_icon_str = write_tmp_icon(self.current_icon,
                                      color_tuple)
        self.btn_icon.setIcon(QIcon(HOME + "/.pyvisor/.tmp_icons/" + tmp_icon_str))

    def rename(self):
        if self.behaviour.name == 'delete':
            QMessageBox.warning(self, 'Can\'t change name!',
                                "'delete' action can't be edited.",
                                QMessageBox.Ok)
            return
        self.name_edit = QLineEdit(self.btn_name.text())
        self.grid.addWidget(self.name_edit,
                            0, 0, 1, 2)
        self.name_edit.returnPressed.connect(self.rename_finished)

    def rename_finished(self):
        name = str(self.name_edit.text())
        try:
            self.gui_data_interface.change_behaviour_name(self.behaviour, name)
            self.btn_name.setText(self.name_edit.text())
        except NameIdenticalException:
            QMessageBox.warning(self, 'Name unchanged!',
                                "Specified name is identical.",
                                QMessageBox.Ok)
        except NameExistsException:
            QMessageBox.warning(self, "Name unchanged!",
                                "Behaviour with that name already exists.",
                                QMessageBox.Ok)
        self.name_edit.hide()
