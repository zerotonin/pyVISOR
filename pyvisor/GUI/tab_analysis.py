from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QComboBox, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QInputDialog, QMessageBox)
import pyvisor.icon as ic
import pyvisor.ManualEthologyScorer as MES
import os
import collections

from pyvisor.GUI.model.animal import Animal

try:
    import thread as _thread
except ImportError:
    import _thread
from itertools import chain
HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


class TabAnalysis(QWidget):

    def __init__(self, parent):
        
        self.analysis_list = [] 
        super().__init__()

        self.parent = parent

        self.init_UI()
        self.sco = MES.ManualEthologyScorer()
        
    def init_UI(self):
        
        # ===========================
        # background image 
        # ===========================
        self.background_image = QLabel(self)
        self.background_image.setGeometry(0, 0, self.parent.height(), self.parent.width())
        self.pixmap = QPixmap(HERE + '/pictures/gamePad.png')
        self.background_image.setPixmap(self.pixmap.scaled(
            self.background_image.size(),
            Qt.KeepAspectRatio))
        self.background_image.setScaledContents(True)
        self.MediaFileName = ''
        self.MediaType = ''
        self.background_image.resize(self.size())
        
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
        
    def makeBehaviourSummary(self):
        self.clearLayout(self.hboxConciseBehav)
        # ------------------------
        #      behaviour widgets
        # ------------------------
        
        # Create step label
        self.behav_stepLabel = QLabel('Step 1 Check behaviour settings: ')
        self.behav_stepLabel.resize(20, 40)
        self.behav_stepLabel.setStyleSheet(self.labelStyle)
        self.hboxConciseBehav.addWidget(self.behav_stepLabel)
        # get data from other tabs
        self.animal_tabs = self.parent.get_animal_tabs()
        self.assignment = self.parent.get_assignments()
        self.UIC_layout = self.parent.get_UIC_layout()
        # here for loop!
        for animalI in range(len(self.animal_tabs)):     
            # Create info label
            vbox = self.makeBehavInfoBox(animalI, self.animal_tabs[animalI].name,
                                         self.animal_tabs[animalI].behaviour_dicts,
                                         self.assignment[1]) # 1 is here for the behaviour assigments / zero would be keys
            self.hboxConciseBehav.addLayout(vbox) 
        
        movieControlBox = self.makeMovieControlInfoBox(self.assignment[1])
        self.hboxConciseBehav.addLayout(movieControlBox) 
        self.hboxConciseBehav.addStretch()
        
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
        
    def makeBehavInfoBox(self, animalNo, animalName, behavDict, assignment: Animal):
        behavBox = QVBoxLayout()
        nameLabel = QLabel(animalName+ ' (A' +str(animalNo)+')')
        nameLabel.setStyleSheet(self.labelStyle)
        behavBox.addWidget(nameLabel)
        for i in range(len(behavDict)):
            
            hbox = QHBoxLayout()
            behavLabel = QLabel(behavDict[i]['name'])
            behavLabel.setStyleSheet('color: '+behavDict[i]['color']) 
            hbox.addWidget(behavLabel)

            icon_path = behavDict[i]['icon']
            if icon_path != 'None' and icon_path is not None and icon_path:
                imageLabel = QLabel()
                pixmap =  QPixmap(behavDict[i]['icon'])
                pixmap = pixmap.scaledToWidth(20)
                imageLabel.setStyleSheet('color: ' + behavDict[i]['color'])
                imageLabel.setPixmap(pixmap) 
                hbox.addWidget(imageLabel)
            
            key = 'A'+str(animalNo) + '_' + behavDict[i]['name']
            if key in assignment.keys():
                deviceLabel = QLabel(assignment[key].device)
                deviceLabel.setStyleSheet('color: #C0C0C0') 
                keyLabel = QLabel(assignment[key].key_bindings)
                keyLabel.setStyleSheet('color: #FFFFFF') 
                
            else:
                deviceLabel = QLabel('not assigned yet')
                deviceLabel.setStyleSheet('color: #C0C0C0') 
                keyLabel = QLabel('not assigned yet')
                keyLabel.setStyleSheet('color: #FFFFFF') 
                    
            hbox.addWidget(deviceLabel)
            hbox.addWidget(keyLabel)

            behavBox.addLayout(hbox)

        return behavBox
    
    def makeMovieControlInfoBox(self, behavAssignment):
        # top label
        movieBox = QVBoxLayout()
        nameLabel = QLabel('movie actions')
        nameLabel.setStyleSheet(self.labelStyle)
        movieBox.addWidget(nameLabel)
        behavAs = collections.OrderedDict(sorted(behavAssignment.items()))
        try:
            item_iterator = behavAs.iteritems()
        except AttributeError:
            item_iterator = behavAs.items()
        
        for key, binding in item_iterator:
            if binding.animal == 'movie':
                tempBox = QHBoxLayout()
                behavLabel = QLabel(binding.name)
                behavLabel.setStyleSheet('color: '+ binding.color) 
                deviceLabel = QLabel(binding.device)
                deviceLabel.setStyleSheet('color: #C0C0C0') 
                buttonLabel = QLabel(binding.key_bindings)
                if binding.key_bindings == 'no button assigned':
                    buttonLabel.setStyleSheet('color: #C0C0C0') 
                else:
                    buttonLabel.setStyleSheet('color: #ffffff') 

                tempBox.addWidget(behavLabel)
                tempBox.addWidget(deviceLabel)
                tempBox.addWidget(buttonLabel)
                movieBox.addLayout(tempBox)

        return movieBox
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
            self.sco.load_data(str(filename), 'pickle')
        else:
            QMessageBox.warning(self, 'Data Loading Aborted!',
                                "Data was not loaded!",
                                QMessageBox.Ok)

    def saveData(self, irrelevant, filename='verboseMode'):
        if filename == 'verboseMode':
            filename = self.getFileName(title='Save Results', path=HOME, fileFilter = '*.txt', mode ='save')

        if filename:
            self.sco.save_data(str(filename),'text')
            self.sco.save_data(str(filename)+'.pkl','pickle')
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
                self.sco.save_data(str(filename),self.modeDict[mode])
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
            self.sco.dIO.saveOverlayImage(str(filename),frameNo)
            
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
            self.sco.dIO.saveOverlayMovie(dirname, prefix, extension)

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
        self.sco = MES.ManualEthologyScorer()

        number_of_behaviours, number_of_unique_disjunctive_behaviours = self._get_animal_configurations(button_list,
                                                                                                        icon_list)

        self.animal_handler.save_state()

        # load media
        if self.MediaType == 'Movie':
            self.sco.loadMovie(self.MediaFileName)

        elif self.MediaType == 'ImageSequence':
            self.sco.loadImageSequence(self.MediaFileName)

        elif self.MediaType == 'Norpix':
            self.sco.loadNorPixSeq(self.MediaFileName)

        else:
            QMessageBox.warning(self, 'Unknown media type: ' + self.MediaType,
                                "Specify a movie, an image sequence, or norpix sequence.",
                                QMessageBox.Ok)
            return

        icon_obj_list = self._make_icons(icon_list)

        self._assign_icon_positions(number_of_behaviours, icon_obj_list, number_of_unique_disjunctive_behaviours)

        self.gui_device_name_to_scorer_device_name()
        self.UIC_switch_writer()

        _thread.start_new_thread(self.sco.go, ())

    def _assign_icon_positions(self, behav_NumList, iconObjList, uniqueDJB_NumList):
        # All Icon Positions are set one after the other / this needs to be user definable
        counterStart = 0
        counterStart2 = 0
        for animalI in range(len(self.animal_tabs)):
            counterStop = counterStart + uniqueDJB_NumList[animalI]
            counterStop2 = counterStart2 + behav_NumList[animalI]
            # the following line has to be changed
            self.sco.animals[animalI].assignIconPos2UniqueDJB(self.sco.iconPos[counterStart:counterStop])
            self.sco.animals[animalI].assignIcons(iconObjList[counterStart2:counterStop2],
                                                  ['simple'] * (behav_NumList[animalI]))
            counterStart = counterStop
            counterStart2 = counterStop2

    def _make_icons(self, iconList):
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
        uniqueDJB_NumList = list()
        behav_NumList = list()
        self.behavIterationList = list()
        for animalI in range(len(self.animal_tabs)):
            behavList, disjuncList = self._get_behaviours_and_disjunctions(animalI, buttonList, iconList)

            # add animal to self.scorer object
            self.sco.addAnimal(self.animal_tabs[animalI].name,  # animal label
                               100,  # ethogram length
                               behavList,  # behaviour labels
                               [0] * len(behavList),  # beginning status
                               disjuncList)  # disjunction list first 4 or disjunct to each other as are the last two

            # as list are mutable they cannot be hashed with set
            # therefore we have to do this
            uniqueDJB_NumList.append(len(set(tuple(row) for row in disjuncList)))
            behav_NumList.append(len(behavList))
        return behav_NumList, uniqueDJB_NumList

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
            buttonList.append(behav_binding.key_bindings)
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
            print('animal:', self.assignment[0][key].animal)
            if self.assignment[0][key].animal == 'movie':
                animal = -1
            elif self.assignment[0][key].animal == 'None':
                continue
            else:
                animal = self.assignment[0][key].animal

            behav = self.assignment[0][key].name  # is a str
            if self._is_animal_behaviour(key, animal_behaviours_as_strings):
                # is an int
                behav = animal_behaviours_as_strings[self.assignment[0][key].animal].index(behav)

            free_binding_list.append((self.assignment[0][key].key_bindings, animal, behav))

        self.sco.setUIC('Free', buttonBindings=self.assignment[0].keys(),
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
            
    def checkingInputs(self):
        #initialise return variable
        goOn = True

        # check if media file info is there
        if (self.MediaFileName == '') or (self.MediaType == ''):
            QMessageBox.warning(self, 'Choose media first!',
                                "You need to choose an input media file(s)!",
                                QMessageBox.Ok)
            goOn = False
        
        # check behaviour assignment
        listOfUnassignedBehaviour = list()
        no_icons = []
        for animalI in range(len(self.animal_tabs)):
            behavDict = self.animal_tabs[animalI].behaviour_dicts
            for i in range(len(behavDict)):
                key = 'A'+str(animalI) + '_' + behavDict[i]['name']
                if key not in self.assignment[1].keys():
                    listOfUnassignedBehaviour.append(key)
                else:
                    if self.assignment[1][key].key_bindings == 'no button assigned':
                        listOfUnassignedBehaviour.append(key)

                behav_binding = self.assignment[1][key]
                icon_path = behav_binding.icon_path
                if len(icon_path) == 0:
                    no_icons.append((behav_binding.animal, behav_binding.name))

        if len(no_icons) > 0:            
            warnmsg = "You have to assign an icon before the analysis "
            warnmsg += "can be started.\n"
            for ni in no_icons:
                warnmsg += f"Animal {ni[0]}, behaviour {ni[1]} has no icon assigned.\n"
            QMessageBox.warning(self, "No Icon Assigned!",
                                warnmsg,
                                QMessageBox.Ok)
            goOn = False

        if len(listOfUnassignedBehaviour) > 0:
            msg = 'There are unassigned behaviours:\n'
            for behav in listOfUnassignedBehaviour:
                msg = msg + behav + '\n'

            QMessageBox.warning(self, 'Cannot proceed!',
                                msg,
                                QMessageBox.Ok)
            goOn = False
        
        # check movie control inputs
        listOfUnassignedBehaviour = list()

        try:
            item_iterator = self.assignment[1].iteritems()
        except AttributeError:
            item_iterator = self.assignment[1].items()
        
        for key, binding in item_iterator:
            if binding.animal == 'movie':
                if binding.key_bindings == 'no button assigned':
                    listOfUnassignedBehaviour.append(binding.name)

        if len(listOfUnassignedBehaviour) > 0:
            msg = 'There are unassigned movie controls:\n'
            for behav in listOfUnassignedBehaviour:
                msg = msg + behav + '\n'

            QMessageBox.warning(self, 'Cannot proceed!',
                                msg,
                                QMessageBox.Ok)
            goOn = False

        return goOn
