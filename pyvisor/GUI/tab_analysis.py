import os
from typing import List, Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QComboBox, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QInputDialog, QMessageBox)

from .model.animal import Animal
from .model.behaviour import Behaviour
from .model.gui_data_interface import GUIDataInterface
from ..ManualEthologyScorer import ManualEthologyScorer
from ..manual_ethology_scorer_2 import ManualEthologyScorer2

try:
    import thread as _thread
except ImportError:
    import _thread
from itertools import chain
HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


class TabAnalysis(QWidget):

    def __init__(self, parent: QWidget,
                 gui_data_interface: GUIDataInterface):

        super().__init__()
        self.analysis_list = []
        self.parent = parent
        self.gui_data_interface = gui_data_interface
        self.manual_scorer = None  # type: Union[ManualEthologyScorer, None]

        self.media_file_name = ''
        self.media_type = ''
        self.init_UI()
        
    def init_UI(self):
        self._init_background_image()

        self._init_layout_boxes()

        self.labelStyle = """
        color: white;
        background-color: rgba(255, 255, 255, 125);
        margin-top: 2px;
        font-weight: bold;
        """
        self.makeBehaviourSummary()
        self.makeMovieFileIO()
        self.makeCommandoRow()
        self.setLayout(self.vbox)

        self.parent.tabs.currentChanged.connect(self.makeBehaviourSummary)

    def _init_layout_boxes(self):
        self.vbox = QVBoxLayout()
        self.hboxMov = QHBoxLayout()
        self.hboxConciseBehav = QHBoxLayout()
        self.hboxCommand = QHBoxLayout()
        # Comment out the following line to see desired output.
        self.vbox.addStretch()
        self.vbox.addLayout(self.hboxConciseBehav)
        self.vbox.addLayout(self.hboxMov)
        self.vbox.addLayout(self.hboxCommand)
        self.vbox.addStretch()

    def _init_background_image(self):
        self.background_image = QLabel(self)
        self.background_image.setGeometry(0, 0, self.parent.height(), self.parent.width())
        self.pixmap = QPixmap(HERE + '/pictures/gamePad.png')
        self.background_image.setPixmap(self.pixmap.scaled(
            self.background_image.size(),
            Qt.KeepAspectRatio))
        self.background_image.setScaledContents(True)
        self.background_image.resize(self.size())

    def makeBehaviourSummary(self):
        self.clearLayout(self.hboxConciseBehav)
        # ------------------------
        #      behaviour widgets
        # ------------------------
        
        self._create_step_label()
        for animalI in sorted(self.gui_data_interface.animals.keys()):
            vbox = self.makeBehavInfoBox(
                self.gui_data_interface.animals[animalI]
            )
            self.hboxConciseBehav.addLayout(vbox) 
        
        movieControlBox = self.makeMovieControlInfoBox()
        self.hboxConciseBehav.addLayout(movieControlBox) 
        self.hboxConciseBehav.addStretch()

    def _create_step_label(self):
        self.behav_stepLabel = QLabel('Step 1 Check behaviour settings: ')
        self.behav_stepLabel.resize(20, 40)
        self.behav_stepLabel.setStyleSheet(self.labelStyle)
        self.hboxConciseBehav.addWidget(self.behav_stepLabel)

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())
                
    def makeMovieFileIO(self):
        # ------------------------
        #       movie widgets
        # ------------------------

        # Create step label
        self.mov_stepLabel = QLabel('Step 2 Load Image Data: ')
        self.mov_stepLabel.resize(60, 40)
        self.mov_stepLabel.setStyleSheet(self.labelStyle)
        self.hboxMov.addWidget(self.mov_stepLabel)

        # Create info label
        self.mov_label = QLabel('Nothing loaded ...')
        self.mov_label.resize(280, 40)
        self.mov_label.setStyleSheet(self.labelStyle)
        
        # Create Button Movie loading
        self.btn_movie = QPushButton('load movie')
        argList = [['*.avi', '*.mov', '*.mp4', '*.mpg', '*.mkv'], 'movie loaded: ',
                   'failed to load movie', 'Movie', 'Single']
        self.btn_movie.clicked.connect((lambda argList: lambda: self.loadMedia(argList))(argList))
        self.hboxMov.addWidget(self.btn_movie)

        # Create Button Img Sequence loading
        self.btn_image = QPushButton('load image sequence')
        argList = [ ['*.jpg', '*.png', '*.gif'], 'image sequence loaded: ',
                    'failed to load image sequence: ', 'ImageSequence', 'Multi']
        self.btn_image.clicked.connect((lambda argList: lambda: self.loadMedia(argList))(argList))
        self.hboxMov.addWidget(self.btn_image)

        # Create Button Norpix loading
        self.btn_norpix = QPushButton('load Norpix SEQ')
        argList = [['*.seq'], 'Norpix sequence file loaded: ',
                   'failed to load Norpix sequence file', 'Norpix', 'Single']
        self.btn_norpix.clicked.connect((lambda argList: lambda: self.loadMedia(argList))(argList))
        self.hboxMov.addWidget(self.btn_norpix)
               
        self.hboxMov.addWidget(self.mov_label)
        self.hboxMov.addStretch()
        
    def makeCommandoRow(self):
        # ------------------------
        #       command widgets
        # ------------------------

        # Create step label
        self.com_stepLabel = QLabel('Step 3 Run Load Save: ')
        self.com_stepLabel.resize(60,40)
        self.com_stepLabel.setStyleSheet(self.labelStyle)
        self.hboxCommand.addWidget(self.com_stepLabel)
        
        # Create Button to run scorer
        self.com_run=QPushButton('run scorer')
        self.com_run.clicked.connect(self.runScorer)
        self.hboxCommand.addWidget(self.com_run)

        # Create Button to load existing data
        self.com_load=QPushButton('load data')
        self.com_load.clicked.connect(self.loadData)
        self.hboxCommand.addWidget(self.com_load)

        # Create Button to save data
        self.com_save=QPushButton('save data')
        self.com_save.clicked.connect(self.saveData)
        self.hboxCommand.addWidget(self.com_save)
        
        # Create Button to export data
        self.com_exportFrame=QPushButton('export single frame')
        self.com_exportFrame.clicked.connect(self.exportFrame)
        self.hboxCommand.addWidget(self.com_exportFrame)

        # Create Button to export data
        self.com_exportMovie=QPushButton('export movie ')
        self.com_exportMovie.clicked.connect(self.exportMovie)
        self.hboxCommand.addWidget(self.com_exportMovie)

        # Create Button to export data
        self.com_export=QPushButton('export data')
        self.com_export.clicked.connect(self.exportData)
        self.hboxCommand.addWidget(self.com_export)

        #Create ComboBox for export
        self.modeDict = {'choose format':'choose format','clear text':'text','pickle':'pickle','MatLab':'matLab','MS Excel':'xlsx'}
        self.comboBox = QComboBox(self)
        self.comboBox.addItems(self.modeDict.keys())
        self.hboxCommand.addWidget(self.comboBox)
        self.hboxCommand.addStretch()
        
    def close_event(self):        
        self.tabs.close_event()
        
    def makeBehavInfoBox(self, animal: Animal):
        behavBox = QVBoxLayout()
        nameLabel = QLabel(animal.name + ' (A' + str(animal.number)+')')
        nameLabel.setStyleSheet(self.labelStyle)
        behavBox.addWidget(nameLabel)
        for behav_label in sorted(animal.behaviours.keys()):
            behav = animal.behaviours[behav_label]
            hbox = QHBoxLayout()
            self._add_name_label(behav, hbox)
            self._add_icon(behav, hbox)
            self._add_keybinding_label(hbox, behav)
            behavBox.addLayout(hbox)

        return behavBox

    def _add_keybinding_label(
            self, hbox,
            behaviour: Behaviour
    ):
        binding = behaviour.key_bindings[
            self.gui_data_interface.selected_device
        ]
        if binding is None:
            keyLabel = QLabel('not assigned yet')
            keyLabel.setStyleSheet('color: #FFFFFF')
        else:
            keyLabel = QLabel(binding)
            keyLabel.setStyleSheet('color: #FFFFFF')
        hbox.addWidget(keyLabel)

    @staticmethod
    def _add_name_label(behav, hbox):
        behavLabel = QLabel(behav.name)
        behavLabel.setStyleSheet('color: ' + behav.color)
        hbox.addWidget(behavLabel)

    @staticmethod
    def _add_icon(behav, hbox):
        icon_path = behav.icon_path
        if icon_path is not None:
            imageLabel = QLabel()
            pixmap = QPixmap(icon_path)
            pixmap = pixmap.scaledToWidth(20)
            imageLabel.setStyleSheet('color: ' + behav.color)
            imageLabel.setPixmap(pixmap)
            hbox.addWidget(imageLabel)

    def makeMovieControlInfoBox(self):
        # top label
        movieBox = QVBoxLayout()
        self._add_title(movieBox)

        for movie_action in sorted(
                self.gui_data_interface.movie_bindings.keys()
        ):
            binding = self.gui_data_interface.movie_bindings[
                movie_action].key_bindings[self.gui_data_interface.selected_device]
            tempBox = QHBoxLayout()
            behavLabel = QLabel(movie_action)
            behavLabel.setStyleSheet('color: #ffffff')
            if binding is None:
                buttonLabel = QLabel("no button assigned")
                buttonLabel.setStyleSheet('color: #C0C0C0')
            else:
                buttonLabel = QLabel(binding)
                buttonLabel.setStyleSheet('color: #ffffff')
            tempBox.addWidget(behavLabel)
            tempBox.addWidget(buttonLabel)
            movieBox.addLayout(tempBox)

        return movieBox

    def _add_title(self, movieBox):
        nameLabel = QLabel('movie actions')
        nameLabel.setStyleSheet(self.labelStyle)
        movieBox.addWidget(nameLabel)

    def resizeEvent(self, event):
        self.background_image.resize(event.size())                   
    def loadMedia(self,argList):
        # build dialogue window
        dlg = QFileDialog(self)
        # if this is a single file 
        if argList[-1] == 'Single':
            dlg.setFileMode(QFileDialog.ExistingFile)
        # if we are looking for a directory of files
        else:
            dlg.setFileMode(QFileDialog.Directory)
        # set the filter                
        dlg.setNameFilters(argList[0])
        filenames = []
        # execute dialogue
        if dlg.exec_():
            filenames = dlg.selectedFiles()
        # if we are looking for a directory we also need to know the file extension
        ok = True
        if argList[-1] != 'Single':
            text, ok = QInputDialog.getText(self, 'Choose', 'Image File Extension:',text='*.jpg')
            if ok:
                filenames[0] = filenames[0]+'/'+text
        # if everything was set up correctly we save the info for later use
        if (len(filenames) > 0) and (ok is True):
            succStr = argList[1] + filenames[0]
            self.mov_label.setText(succStr)
            self.media_file_name = str(filenames[0]) # for some reason the media handler dislikes Qstrings
            self.media_type = argList[3]
        
        else:
            self.mov_label.setText(argList[2])
            
    def loadData(self):
        # load data
        filename = self.getFileName(title='Load Annotation', path=HOME, fileFilter = '*.pkl, *.pickle', mode ='load')
        if (len(filename) > 0):
            self.manual_scorer.load_data(str(filename), 'pickle')
        else:
            QMessageBox.warning(self, 'Data Loading Aborted!',
                                "Data was not loaded!",
                                QMessageBox.Ok)

    def saveData(self, irrelevant, filename='verboseMode'):
        if filename == 'verboseMode':
            filename = self.getFileName(title='Save Results', path=HOME, fileFilter = '*.txt', mode ='save')

        if filename:
            self.manual_scorer.save_data(str(filename), 'text')
            self.manual_scorer.save_data(str(filename) + '.pkl', 'pickle')
        else:
            QMessageBox.warning(self, 'Data Saving Aborted!',
                                "Data was  not saved!",
                                QMessageBox.Ok)
            
    def exportData(self, irrelevant, filename='verboseMode',):
        
        mode = str(self.comboBox.currentText())
   
        if mode == 'choose format':
            QMessageBox.warning(self, 'Data Saving Aborted!',
                                "Data was  not saved! You need to choose a format",
                                QMessageBox.Ok)     
        else:
            
            if filename == 'verboseMode':
                filename = self.getFileName(title='Save Results', path=HOME, fileFilter = self.modeDict[mode], mode ='save')
        
            if filename:
                self.manual_scorer.save_data(str(filename), self.modeDict[mode])
            else:
                QMessageBox.warning(self, 'Data Saving Aborted!',
                                    "Data was  not saved!",
                                    QMessageBox.Ok)
                
    def exportFrame(self, irrelevant, filename='verboseMode',frameNo = 'verboseMode'):
        goOn = True
        if filename == 'verboseMode':
            filename = self.getFileName(title='Save Results', path=HOME, fileFilter = '*.jpg', mode ='save')
        
        if filename:
            goOn = True
        else:
            goOn = False

        if frameNo == 'verboseMode' and goOn:
            frameNo, ok = QInputDialog.getInt(self, 'Choose', 'Frame Number:')
            if ok:       
                goOn = True
            else:
                goOn = False
        if goOn:
            self.manual_scorer.dIO.saveOverlayImage(str(filename), frameNo)
            
    def exportMovie(self,  irrelevant, dirname='verboseMode',
                    prefix='verboseMode', extension='verboseMode'):
        goOn = True
        
        if dirname == 'verboseMode':
           dirname = QFileDialog.getExistingDirectory(self, 'Frame Directory', HOME)

        if dirname:
            goOn = True
        else:
            goOn = False

        if prefix == 'verboseMode' and goOn:
            prefix , ok = QInputDialog.getText(self, 'Choose', 'Prefix for image files',
                                               QLineEdit.Normal, 'frame')
            if ok:       
                goOn = True
            else:
                goOn = False

        if extension  == 'verboseMode' and goOn:
            exts = ("png", "jpeg", "bmp", "tga")
            extension, ok = QInputDialog.getItem(self, "select file format", 
                                                       "list of formats", exts, 0, False)
            if ok:       
                goOn = True
            else:
                goOn = False

        if goOn:
            self.manual_scorer.dIO.saveOverlayMovie(dirname, prefix, extension)

    def getFileName(self,title,path,fileFilter,mode):
        if mode == 'load':
            filename = QFileDialog.getOpenFileName(self,title, path, initialFilter=fileFilter)
        elif mode == 'save':
            filename = QFileDialog.getSaveFileName(self,title, path, initialFilter=fileFilter)
        else:
            QMessageBox.warning(self, 'Unkown mode: ' + mode,
                                "Data IO stopped, in getFileName",
                                QMessageBox.Ok)
            return ''
            
        filename = filename[0]
        return filename

    def runScorer(self):
        goOn = self.checkingInputs()

        if goOn is False:
            return

        scorer = ManualEthologyScorer2(self.gui_data_interface.animals,
                                       self.gui_data_interface.movie_bindings,
                                       self.gui_data_interface.selected_device)
        self.gui_data_interface.manual_scorer = scorer
        self.manual_scorer = scorer

        self.gui_data_interface.save_state()

        try:
            self.manual_scorer.load_movie(self.media_file_name, self.media_type)
        except KeyError as ex:
            QMessageBox.warning(self, 'Unknown media type: ' + self.media_type,
                                "Specify a movie, an image sequence, or norpix sequence.\nError message: {}".format(ex),
                                QMessageBox.Ok)
            return

        _thread.start_new_thread(self.manual_scorer.go, ())

    def _is_animal_behaviour(self, key: str, animal_behaviours_as_strings: List[List[str]]) -> bool:
        return self.assignment[0][key].name in chain.from_iterable(animal_behaviours_as_strings)


    def _media_file_not_specified(self):
        return (self.media_file_name == '') or (self.media_type == '')

    def checkingInputs(self) -> bool:
        goOn = True

        # check if media file info is there
        if self._media_file_not_specified():
            QMessageBox.warning(self, 'Choose media first!',
                                "You need to choose an input media file(s)!",
                                QMessageBox.Ok)
            goOn = False

        no_icons = self.gui_data_interface.get_behaviours_without_icons()
        if no_icons:
            warnmsg = "You have to assign an Icon before the analysis "
            warnmsg += "can be started.\n"
            for ni in no_icons:
                animal = self.gui_data_interface.animals[ni.animal_number]
                warnmsg += "Animal {}, behaviour {} has no Icon assigned.\n".format(
                    animal.name,
                    ni.name
                )
            QMessageBox.warning(self, "No Icon Assigned!",
                                warnmsg,
                                QMessageBox.Ok)
            goOn = False

        no_button_assigned = self.gui_data_interface.get_scorer_actions_without_buttons_assigned()
        if len(no_button_assigned) > 0:
            msg = 'These actions have no buttons assigned:\n'
            for action in no_button_assigned:
                if isinstance(action, Behaviour):
                    animal = self.gui_data_interface.animals[action.animal_number]
                    msg += "- Animal {}, behaviour {}\n".format(animal.name, action.name)
                else:
                    msg += "- MovieAction {}\n".format(action.name)

            QMessageBox.warning(self, 'Scorer actions unassigned!',
                                msg,
                                QMessageBox.Ok)
            goOn = False
        
        return goOn
