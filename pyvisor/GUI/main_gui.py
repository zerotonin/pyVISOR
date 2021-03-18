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
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QMessageBox, QApplication)

from pyvisor.GUI.model.movie_bindings import MovieBindings
from .model.animal import Animal
from .model.animal_handler import AnimalHandler
from .tab_analysis import TabAnalysis
from .tab_behaviours.tab_behaviours import BehavioursTab
from .tab_buttons import TabButtons
from .tab_results import TabResults

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


class MovScoreGUI(QWidget):

    def __init__(self):
        """
        """    
        super(MovScoreGUI, self).__init__()
        self.animal_handler = AnimalHandler()
        self._load_defaults()

        self.initUI()

    def _load_defaults(self):
        self._load_animals()
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

    def _load_animals(self):
        try:
            with open(HOME + "/.pyvisor/guidefaults_animals.json", 'r') as f:
                animals = json.load(f)
        except FileNotFoundError:
            with open(HERE + "/guidefaults_animals.json", 'r') as f:
                animals = json.load(f)

        for a in animals["animals"]:
            ani = Animal.from_json_dict(a)
            self.animal_handler.animals[ani.number] = ani
        self.animal_handler.selected_device = animals["selected_device"]
        if "movie_bindings" in animals:
            self.animal_handler.movie_bindings = MovieBindings.from_dict(
                animals["movie_bindings"]
            )

    def initUI(self):
        """
        """        
        self._load_size_and_position_of_last_usage()
        self.setWindowTitle('Pyvisor')
        self.setWindowIcon(QIcon(HERE + '/../resources/icons/game/MES_trans.png'))
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self._initiate_tabs(vbox)

    def _initiate_tabs(self, vbox):
        self.tabs = QTabWidget()
        vbox.addWidget(self.tabs)
        self.tab_behaviours = BehavioursTab(self, self.animal_handler)
        self.tab_buttons = TabButtons(self, self.animal_handler)
        self.tab_analysis = TabAnalysis(self)
        self.tab_results = TabResults(self)
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
        return self.tab_buttons.getAssignments()
    
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
        self._save_animals()

        self.tab_buttons.close_event()  # tab_list[1] is a TabButtons object

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

    def _save_animals(self):
        savable_list = self.animal_handler.get_savable_list()
        with open(HOME + '/.pyvisor/guidefaults_animals.json', 'wt') as fh:
            json.dump(savable_list, fh)


if __name__ == "__main__":

    import sys
    app = QApplication(sys.argv)
    gui = MovScoreGUI()
    gui.show()

    import os
    if not os.path.isdir(HOME+'/.pyvisor'):
        os.makedirs(HOME+'/.pyvisor')

    sys.exit(app.exec_())
