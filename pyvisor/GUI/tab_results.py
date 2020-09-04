
from __future__ import unicode_literals
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

HERE = os.path.dirname(os.path.abspath(__file__))

class TabResults(QWidget):
    def __init__(self, parent):        
        self.analysis_list = [] 
        super(TabResults, self).__init__()
        self.parent = parent
        # shorthand
        self.sco = self.parent.shortHandAnalysis.sco
        # create analysis object / if empty scorer object we ignore fps
        self.ana = self.sco.anaO
        try:
            self.refreshAnaObj()
        except:
            print('no data for analysis available')
        
        self.init_UI()

    def init_UI(self):        

        # ===========================
        # background image 
        # ===========================
        self.background_image = QLabel(self)
        self.background_image.setGeometry(0, 0, self.parent.height(), self.parent.width())
        self.pixmap = QPixmap(HERE + '/pictures/behaviour.png')
        self.background_image.setPixmap(self.pixmap.scaled(
            self.background_image.size(),
            Qt.KeepAspectRatio))
        self.background_image.setScaledContents(True)
        
        self.background_image.resize(self.size())
        
        #Widgets

        self.vbox = QVBoxLayout()
        # self.vbox.addLayout(self.makeStaticPlots())
        # self.vbox.addWidget(self.makeOverviewPlot())
        self.setLayout(self.vbox)

        #set signals and slots
        self.parent.tabs.currentChanged.connect(self.refreshTab)

    def refreshTab(self):
        # refresh data source
        pass
        
    def close_event(self):        
        self.tabs.close_event()

    def resizeEvent(self, event):
        self.background_image.resize(event.size())

