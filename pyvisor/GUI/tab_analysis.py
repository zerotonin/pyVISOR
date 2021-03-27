from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QComboBox, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QInputDialog, QMessageBox)
import pyvisor.icon as ic
import os

from .model.animal import Animal
from .model.behaviour import Behaviour
from .model.gui_data_interface import GUIDataInterface
from ..ManualEthologyScorer import ManualEthologyScorer

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
        self.manual_scorer = None  # type: ManualEthologyScorer

        self.init_UI()
        
    def init_UI(self):
        self._init_background_image()
        self.MediaFileName = ''
        self.MediaType = ''

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
            self.MediaFileName = str(filenames[0]) # for some reason the media handler dislikes Qstrings
            self.MediaType = argList[3]
        
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

    def compatabilityList2disjunctionList(self,disjuncList):
        # initialise variables
        compabilityList = list()
        behavList = list()
        allDisjunc = list()

        # read out complex parallel behaviour list
        for tupI in disjuncList:
            # get the succession of behaviours in one list
            behavList.append(str(tupI[0]))
            # get all unique paralell behaviours in a list of lists
            mySet = set(tupI[1])
            compabilityList.append(list(mySet))
            
        #go trough each behaviour again
        for i in range(len(behavList)):

            #initialise disunctionlist with all behaviours
            disjuncList = behavList[:]
            compList    = compabilityList[i]

            # now delete every parallel behaviour out of the disjuction list
            for j in range(len(compList)):
                if compList[j] in disjuncList:
                    disjuncList.remove(str(compList[j]))
                else:
                    print("Behaviour " + compList[j] + " was found in compatebility list but no references were found in the general behaviour list!")

            # now we make the disjunction list as list of index positions
            disjuncIndexList = list()

            for behav in disjuncList:
                disjuncIndexList.append(behavList.index(behav))

            #add everything to a list of lists again
            allDisjunc.append(disjuncIndexList)
        
        return allDisjunc
    
    def runScorer(self):
        goOn = self.checkingInputs()

        if goOn is False:
            return
        
        icon_list = list()
        button_list = list()
        self.manual_scorer = ManualEthologyScorer(self.gui_data_interface.animals,
                                                  self.gui_data_interface.movie_bindings)

        self.gui_data_interface.save_state()

        # load media
        if self.MediaType == 'Movie':
            self.manual_scorer.loadMovie(self.MediaFileName)

        elif self.MediaType == 'ImageSequence':
            self.manual_scorer.loadImageSequence(self.MediaFileName)

        elif self.MediaType == 'Norpix':
            self.manual_scorer.loadNorPixSeq(self.MediaFileName)

        else:
            QMessageBox.warning(self, 'Unknown media type: ' + self.MediaType,
                                "Specify a movie, an image sequence, or norpix sequence.",
                                QMessageBox.Ok)
            return

        icon_obj_list = self._make_icons(icon_list)

        self.gui_device_name_to_scorer_device_name()
        self.UIC_switch_writer()

        _thread.start_new_thread(self.manual_scorer.go, ())


    @staticmethod
    def _make_icons(iconList):
        iconObjList = list()
        for i in range(len(iconList)):
            # make color
            colorList = list()
            for j in [1, 3, 5]:  # colors are defined in hexcode e.g #ff32a2
                colorList.append(int(iconList[i][1][j:j + 2], 16))
            colorTupel = (colorList[0], colorList[1], colorList[2])

            # make icon
            icon = ic.icon(color=colorTupel)
            icon.readImage(iconList[i][0])
            icon.decall2icon()
            iconObjList.append(icon.icon2pygame())
        return iconObjList

    def _get_animal_configurations(self, buttonList, iconList):
        unique_disjoint_behav_NumList = list()
        behav_NumList = list()
        self.behavIterationList = list()
        for an in sorted(self.gui_data_interface.animals.keys()):
            behavList, disjuncList = self._get_behaviours_and_disjunctions(animalI, buttonList, iconList)

            # add animal to self.scorer object
            self.manual_scorer.addAnimal(self.animal_tabs[animalI].name,  # animal label
                                         100,  # ethogram_length length
                                         behavList,  # behaviour labels
                                         [0] * len(behavList),  # beginning status
                                         disjuncList)  # disjunction list first 4 or disjunct to each other as are the last two

            # as list are mutable they cannot be hashed with set
            # therefore we have to do this
            unique_disjoint_behav_NumList.append(len(set(tuple(row) for row in disjuncList)))
            behav_NumList.append(len(behavList))
        return behav_NumList, unique_disjoint_behav_NumList

    def _get_behaviours_and_disjunctions(self, animalI, buttonList, iconList):
        # initialise disjunction lists and behaviour lists
        behavList = list()
        disjuncList = list()
        # shorthand
        behavDict = self.animal_tabs[animalI].behaviour_dicts
        for i in range(len(behavDict)):
            # get key
            key = 'A' + str(animalI) + '_' + behavDict[i]['name']

            behav_binding = self.assignment[1][key]
            # fill lists
            buttonList.append(behav_binding.scorer_actions)
            behavList.append(str(behav_binding.name))
            icon_path, icon_color = (behav_binding.icon_path,
                                     behav_binding.color)
            iconList.append((icon_path, icon_color))
            # disjunction list needs to be updated because it is not implemented yet
            disjuncList.append((behavDict[i]['name'], behavDict[i]['compatible']))
            self.behavIterationList.append(key);
        disjuncList = self.compatabilityList2disjunctionList(disjuncList)
        return behavList, disjuncList

    def UIC_switch_writer(self):
        animal_behaviours_as_strings = self._get_animal_behaviours_as_strings()

        free_binding_list = list()
        for key in self.assignment[0].keys():
            print('animal:', self.assignment[0][key].animal_number)
            if self.assignment[0][key].animal_number == 'movie':
                animal = -1
            elif self.assignment[0][key].animal_number == 'None':
                continue
            else:
                animal = self.assignment[0][key].animal_number

            behav = self.assignment[0][key].name  # is a str
            if self._is_animal_behaviour(key, animal_behaviours_as_strings):
                # is an int
                behav = animal_behaviours_as_strings[self.assignment[0][key].animal_number].index(behav)

            free_binding_list.append((self.assignment[0][key].scorer_actions, animal, behav))

        self.manual_scorer.setUIC('Free', buttonBindings=self.assignment[0].keys(),
                                  freeBindingList=free_binding_list,
                                  UICdevice=self.UIC_layout)

    def _is_animal_behaviour(self, key: str, animal_behaviours_as_strings: List[List[str]]) -> bool:
        return self.assignment[0][key].name in chain.from_iterable(animal_behaviours_as_strings)

    def _get_animal_behaviours_as_strings(self):
        behavStrListList = list()
        for i in range(len(self.animal_tabs)):
            behavStrListList.append(list())
        for string in self.behavIterationList:
            idx = string.index('_')
            animalI = int(string[1:idx])
            behavStrListList[animalI].append(string[idx + 1:])
        return behavStrListList

    def gui_device_name_to_scorer_device_name(self):
        
        if self.UIC_layout == 'X-Box':
            self.UIC_layout ='XBox'
        elif self.UIC_layout == 'Playstation':
            self.UIC_layout ='PS'
        elif self.UIC_layout == 'Keyboard':
            self.UIC_layout ='Keyboard'
        elif self.UIC_layout == 'Free':
            print('Unknown UIC device in function tab_analysis.guiUICLayout2scoLayout: ' + self.UIC_layout)
        else:
            print('Unknown UIC device in function tab_analysis.guiUICLayout2scoLayout: ' + self.UIC_layout)

    def _media_file_not_specified(self):
        return (self.MediaFileName == '') or (self.MediaType == '')

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
            warnmsg = "You have to assign an icon before the analysis "
            warnmsg += "can be started.\n"
            for ni in no_icons:
                animal = self.gui_data_interface.animals[ni.animal_number]
                warnmsg += "Animal {}, behaviour {} has no icon assigned.\n".format(
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
