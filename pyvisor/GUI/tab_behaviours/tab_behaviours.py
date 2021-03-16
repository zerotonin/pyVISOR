from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
import os

from ..main_gui import MovScoreGUI
from ..styles import style_tab_behaviours
from .animal_tab import AnimalTabWidget
HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


class TabBehaviours(QWidget):

    def __init__(self, parent: MovScoreGUI):
        super(TabBehaviours, self).__init__(parent)
        self.parent = parent  # type: MovScoreGUI
        self.init_UI()

    def init_UI(self):

        # ===========================
        # background image 
        # ===========================
        self.background_image = QLabel(self)
        self.background_image.setGeometry(0, 0, self.parent.height(), self.parent.width())
        self.pixmap = QPixmap(HERE + '/../pictures/behaviour.png')
        self.background_image.setPixmap(self.pixmap.scaled(
            self.background_image.size(),
            Qt.KeepAspectRatio))
        self.background_image.setScaledContents(True)

        self.background_image.resize(self.size())

        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self.tabs = AnimalTabWidget(self)
        self.setStyleSheet(style_tab_behaviours)
        vbox.addStretch()
        vbox.addWidget(self.tabs)
        vbox.addStretch()
        stylesheetTab = """ 
        QTabBar::tab:selected {background: rgba(255, 255, 255, 100);}
        QTabWidget>QWidget{background: rgba(255, 255, 255, 100);}
        """        
        self.setStyleSheet(stylesheetTab)

    def resizeEvent(self, event):
        self.background_image.resize(event.size())

    def get_number_of_animals(self):
        return len(self.tabs.tabs_)

    def get_number_of_behaviours_of_animal(self, i):
        return len(self.tabs.tabs_[i].behav_widgets)
