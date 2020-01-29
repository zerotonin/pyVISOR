"""
@author Ilyas Kuhlemann
@mail ilyasp.ku@gmail.com
@date 15.06.16
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os, pickle

from .tab_behaviours.tab_behaviours import TabBehaviours
from .tab_buttons import TabButtons
from .tab_analysis import TabAnalysis
from .tab_results import TabResults
from .tab_buttons2 import TabSimpleButtons

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


class MovScoreGUI(QWidget):

    def __init__(self):
        """
        """    
        super(MovScoreGUI, self).__init__()

        try:
            with open(HOME + "/.pymovscore/guidefaults_movscoregui.pkl", 'rb') as f:
                self.values = pickle.load(f)
        except:
            try:
                with open(HERE + "/guidefaults_movscoregui.pkl", 'rb') as f:
                    self.values = pickle.load(f)           
            except:
                self.values = dict()
                self.values['display'] = dict()
                self.values['display']['geometry'] = QRect(0,0,640,480)


        self.initUI()

    def initUI(self):
        """
        """        
        # load size and position of last usage
        self.setGeometry(self.values['display']['geometry'])
        self.move(self.values['display']['geometry'].topLeft())
        # set title bar
        self.setWindowTitle('PyMovScore')
        self.setWindowIcon(QIcon(HERE + '/../resources/icons/game/MES_trans.png'))
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        # initiate main tab widget
        self.tabs = QTabWidget()
        vbox.addWidget(self.tabs)
        self.shortHandBehavTab = TabBehaviours(self)
        self.shortHandButton = TabSimpleButtons(self)
        self.shortHandAnalysis = TabAnalysis(self)
        self.tab_list = [self.shortHandBehavTab, 
                         self.shortHandButton,
                         self.shortHandAnalysis, 
                         TabResults(self)]

        self.tab_names = ['Behaviours',
                          'Button Assignment',
                          'Analysis',
                          'Results Overview']        

        for i in range(0, len(self.tab_list)):
            self.tabs.addTab(self.tab_list[i], self.tab_names[i])

    def get_animal_tabs(self):        
        return self.shortHandBehavTab.tabs.tabs_

    def get_assignmens(self):
        return self.shortHandButton.getAssignments()
    def get_UIC_layout(self):
        return self.shortHandButton.getSelectedLayout()
            
    def set_value(self, key, value):
        """
        """
        self.values[key] = value

    def closeEvent(self, event):
        """
        Pops up a dialog-window when the user wants to close the GUI's window.
        """
        self.values['display']['geometry'] = self.frameGeometry()
        with open(HOME + '/.pymovscore/guidefaults_movscoregui.pkl', 'wb') as f:
            pickle.dump(self.values, f, pickle.HIGHEST_PROTOCOL)
        
        ## list of close events of child processes/widgets to call
        self.tab_list[0].close_event()  # tab_list[0] is a TabBehaviours object
        self.tab_list[1].close_event()  # tab_list[1] is a TabButtons object        

        reply = QMessageBox.question(self,
                                           'Message',
                                           "Do you really want to quit? \n(Saved everything etc.?)",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__=="__main__":

    import sys
    app=QApplication(sys.argv)
    gui=MovScoreGUI()
    gui.show()

    import os
    if not os.path.isdir(HOME+'/.pymovscore'):
        os.makedirs(HOME+'/.pymovscore')

    sys.exit(app.exec_())
