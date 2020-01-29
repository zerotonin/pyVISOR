
from __future__ import unicode_literals
import sys, os, random
from matplotlib.backends import qt_compat
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pymovscore.analysis.analysis_online  as ana

HERE = os.path.dirname(os.path.abspath(__file__))

# class MyMplCanvas(FigureCanvas):
#     """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

#     def __init__(self, parent=None, width=5, height=4, dpi=100,anaObj =[]):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes   = fig.add_subplot(111)
#         self.anaObj = anaObj



#         FigureCanvas.__init__(self, fig)
#         self.setParent(parent)

#         FigureCanvas.setSizePolicy(self,
#                                    QSizePolicy.Expanding,
#                                    QSizePolicy.Expanding)
#         FigureCanvas.updateGeometry(self)

#     def compute_initial_figure(self):
#         pass


# class MyStaticMplCanvas(MyMplCanvas):
#     """Simple canvas with a sine plot."""

#     def compute_initial_figure(self):
#         if   self.mode == 'percentage':
#             self.anaObj.plotPercentage(self.axes)
#         elif self.mode == 'boutDur':
#             self.anaObj.plotBoutDur(self.axes)
#         elif self.mode == 'frequency':
#             self.anaObj.plotFrequency(self.axes)
#         else:
#             QMessageBox.warning(self, 'Unkown plot format!',
#                                             "Did not recognise plot format in tab results!",
#                                             QMessageBox.Ok)
            


# class MyDynamicMplCanvas(MyMplCanvas):
#     """A canvas that updates itself every second with a new plot."""

#     def __init__(self, *args, **kwargs):
#         MyMplCanvas.__init__(self, *args, **kwargs)
#         timer = QTimer(self)
#         timer.timeout.connect(self.update_figure)
#         timer.start(1000)

#     def compute_initial_figure(self):
#         self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

#     def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        # l = [random.randint(0, 10) for i in range(4)]
        # self.axes.cla()
        # self.axes.bar([0, 1, 2, 3], l)
        # self.draw()

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

    
    

    # def refreshAnaObj(self):
    #     self.sco = self.parent.shortHandAnalysis.sco
    #     self.ana = self.sco.anaO
    #     self.ana.getDataFromScorer()
    #     if not(type(self.ana.behaviours) == bool and self.ana.behaviours == False):
    #         self.ana.getFPS()
    #         self.ana.runAnalysis()

    # def makeStaticPlots(self):
    #     vbox = QVBoxLayout()
    #     hbox = QHBoxLayout()
    #     self.refreshAnaObj()
    #     self.boutDurWidget = MyStaticMplCanvas(parent=self, width=5, height=4, dpi=100)
    #     self.boutDurWidget.analysisObj = self.ana
    #     self.boutDurWidget.mode = 'boutDur'
    #     hbox.addWidget(self.boutDurWidget)

    #     self.freqWidget = MyStaticMplCanvas(parent=self, width=5, height=4, dpi=100)
    #     self.freqWidget.analysisObj = self.ana
    #     self.freqWidget.mode = 'frequency'
    #     hbox.addWidget(self.freqWidget)

    #     self.percWidget = MyStaticMplCanvas(parent=self, width=5, height=4, dpi=100)
    #     self.percWidget.analysisObj = self.ana
    #     self.percWidget.mode = 'percentage'
    #     hbox.addWidget(self.percWidget)

    #     vbox.addLayout(hbox)

    #     # Create Button to save data
    #     self.statRefreshButton = QPushButton('refresh plots')
    #     self.statRefreshButton.clicked.connect(self.refreshStaticPlots)
    #     vbox.addWidget(self.statRefreshButton)
    #     return vbox

    # def makeOverviewPlot(self):
    #     overView = MyDynamicMplCanvas(parent=self, width=5, height=4, dpi=100)
    #     return overView

    # def refreshStaticPlots(self):
        
    #     self.refreshAnaObj()
    #     try:
    #         self.refreshAnaObj()
    #     except:
    #         print 'no data for analysis available'    
    #     self.boutDurWidget.anaObj = self.ana
    #     self.boutDurWidget.compute_initial_figure()
    #     self.percWidget.anaObj = self.ana
    #     self.percWidget.compute_initial_figure()
    #     self.freqWidget.anaObj = self.ana
    #     self.freqWidget.compute_initial_figure()
        
    
    def refreshTab(self):
        # refresh data source
        pass
        
    def close_event(self):        
        self.tabs.close_event()

    def resizeEvent(self, event):
        self.background_image.resize(event.size())

