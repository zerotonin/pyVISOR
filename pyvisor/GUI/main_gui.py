"""
@author Ilyas Kuhlemann
@mail ilyasp.ku@gmail.com
@date 15.06.16
"""
import json
import os
import pickle

from PyQt5.QtCore import QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QMessageBox, QApplication, QHBoxLayout, QLabel)

from pyvisor.GUI.model.movie_bindings import MovieBindings
from .model.animal import Animal
from .model.gui_data_interface import GUIDataInterface
from .tab_analysis import TabAnalysis
from .tab_behaviours.tab_behaviours import TabBehaviours
from pyvisor.GUI.tab_buttons.tab_buttons import TabButtons
from .tab_results import TabResults
from pyvisor.resources import resource_path

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


class MovScoreGUI(QWidget):

    def __init__(self):
        """
        """    
        super(MovScoreGUI, self).__init__()
        self.gui_data_interface = GUIDataInterface()
        self._load_defaults()

        self.initUI()

    def _load_defaults(self):
        self._load_state()
        self._load_display_values()

    def _load_display_values(self):
        try:
            with open(HOME + "/.pyvisor/guidefaults_movscoregui.pkl", 'rb') as f:
                self.values = pickle.load(f)
        except FileNotFoundError:
            try:
                with open(HERE + "/guidefaults_movscoregui.pkl", 'rb') as f:
                    self.values = pickle.load(f)
            except FileNotFoundError:
                self.values = dict()
                self.values['display'] = dict()
                self.values['display']['geometry'] = QRect(0, 0, 640, 480)

    def _load_state(self):
        try:
            with open(HOME + "/.pyvisor/guidefaults_animals.json", 'r') as f:
                state = json.load(f)
        except FileNotFoundError:
            with open(HERE + "/guidefaults_animals.json", 'r') as f:
                state = json.load(f)

        for a in state["animals"]:
            ani = Animal.from_json_dict(a)
            self.gui_data_interface.animals[ani.number] = ani
        self.gui_data_interface.selected_device = state["selected_device"]
        if "movie_bindings" in state:
            self.gui_data_interface.movie_bindings = MovieBindings.from_dict(
                state["movie_bindings"]
            )

    def initUI(self):
        """
        """        
        self._load_size_and_position_of_last_usage()
        self.setWindowTitle('Pyvisor')
        self.setWindowIcon(QIcon(str(resource_path('icons', 'game', 'MES_trans.png'))))
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self._initiate_tabs(vbox)

    def _initiate_tabs(self, vbox):
        self.tabs = QTabWidget()
        vbox.addWidget(self.tabs)
        self.tab_behaviours = TabBehaviours(self, self.gui_data_interface)
        self.tab_buttons = TabButtons(self, self.gui_data_interface)
        self.tab_analysis = TabAnalysis(self, self.gui_data_interface)
        self.tab_results = TabResults(self, self.gui_data_interface)
        self.tab_names = ['Behaviours',
                          'Button Assignment',
                          'Analysis',
                          'Results Overview']
        tab_list = [self.tab_behaviours, self.tab_buttons, self.tab_analysis, self.tab_results]
        for tab, name in zip(tab_list, self.tab_names):
            self.tabs.addTab(tab, name)

    def _load_size_and_position_of_last_usage(self):
        self.setGeometry(self.values['display']['geometry'])
        self.move(self.values['display']['geometry'].topLeft())

    def get_animal_tabs(self):        
        return self.tab_behaviours.tabs.tabs_

    def get_assignments(self):
        raise NotImplementedError
    
    def get_UIC_layout(self):
        return self.tab_buttons.getSelectedLayout()
            
    def set_value(self, key, value):
        """
        """
        self.values[key] = value

    def closeEvent(self, event):
        """
        Pops up a dialog-window when the user wants to close the GUI's window.
        """
        self._save_display_values()
        self.gui_data_interface.save_state()

        reply = QMessageBox.question(self,
                                     'Message',
                                     "Do you really want to quit? \n(Saved everything etc.?)",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def _save_display_values(self):
        self.values['display']['geometry'] = self.frameGeometry()
        with open(HOME + '/.pyvisor/guidefaults_movscoregui.pkl', 'wb') as f:
            pickle.dump(self.values, f, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":

    import sys
    app = QApplication(sys.argv)
    gui = MovScoreGUI()
    gui.show()

    import os
    if not os.path.isdir(HOME+'/.pyvisor'):
        os.makedirs(HOME+'/.pyvisor')

    sys.exit(app.exec_())
