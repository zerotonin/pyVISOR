from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QFileDialog, QPushButton, QMessageBox, QComboBox, QInputDialog)

import pygame
import json
from pygame.locals import *
from .behavBinding import BehavBinding
import os
import copy
import collections
HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
DEVICES = {"Keyboard": HERE + "/pictures/gamePad_KB.png", 
           "Playstation": HERE + "/pictures/gamePad_PS.png",
           "X-Box": HERE + "/pictures/gamePad_XB.png",
           "Free": HERE + "/pictures/gamePad_free.png"}


class TabSimpleButtons(QWidget):

    def __init__(self, parent):
        
        self.analysis_list = [] 
        super(TabSimpleButtons, self).__init__()

        self.parent = parent
        pygame.init()
        # Initialize the joysticks
        pygame.joystick.init()
        self.init_UI()

    def init_UI(self):
        # self.item, self.ok = QInputDialog.getItem(self, "select input device", "list of devices", self.modes, 0, False)
                        
        # ============================
        # Get and Initialize Behaviour
        # ============================

        self.keys            = dict()
        self.behavAssignment = dict()
        self.animal_tabs = self.parent.get_animal_tabs()
        self.selected_device = ""
        self.deviceLayout = ""
        self.deviceNumber = -2 # -1= not selected | last  = keyboard, after that it is in the recognition order by pygame
        self.initialiseBehavAssignment()
        self.lastKeyPressed = (71, 'G')

        # ===========================
        # Joy stick initiation
        # ===========================
        
        # Get count of joysticks
        self.joysticNum = pygame.joystick.get_count()
        
        # variables
        self.hatsNum         = [None]*self.joysticNum
        self.buttonsNum      = [None]*self.joysticNum
        self.axesNum         = [None]*self.joysticNum
        self.input_device_names         = [None] * (self.joysticNum + 1)
        
        for i in range(self.joysticNum):
            self.joystick =  pygame.joystick.Joystick(i)
            self.joystick.init()
            # count the axes
            self.axesNum[i]    = self.joystick.get_numaxes()
            self.buttonsNum[i] = self.joystick.get_numbuttons()
            self.hatsNum[i]    = self.joystick.get_numhats()
            self.input_device_names[i]    = self.joystick.get_name()
        self.input_device_names[-1] = 'Keyboard'

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
        
        self.background_image.resize(self.size())


        
        # ===========================
        # layout
        # ===========================

        # Make major boxes
        self.vbox=QVBoxLayout()
        self.hboxDeviceChoice=QHBoxLayout()
        self.hboxConciseBehav=QHBoxLayout()
        self.hboxJoyStickInfo=QHBoxLayout()
        self.hboxLoadSavePreset=QHBoxLayout()
        # add layouts to central vertical box
        self.vbox.addStretch()
        self.vbox.addLayout(self.hboxDeviceChoice)
        self.vbox.addLayout(self.hboxConciseBehav)
        self.vbox.addLayout(self.hboxLoadSavePreset)
        self.vbox.addLayout(self.hboxJoyStickInfo)
        self.vbox.addStretch()
        # define styles
        self.labelStyle="""
        color: white;
        background-color: rgba(255, 255, 255, 125);
        margin-top: 2px;
        font-weight: bold;
        """
        # fill majorboxes with infos
        self.makeJoyStickInfo()
        self.makeBehaviourSummary()
        self.makeDeviceChoice()
        self.makeLoadSavePreset()
        #set layout
        self.setLayout(self.vbox)
        #set signals and slots
        self.parent.tabs.currentChanged.connect(self.makeBehaviourSummary)
        try:
            self.load_button_assignments(filename=HOME + '/.pyvisor/guidefaults_buttons.json')
        except FileNotFoundError:
            print('No preset for button bindings found')
            
    def makeLoadSavePreset(self):
        loadButton = QPushButton('load preset')
        loadButton.clicked.connect(lambda x: self.load_button_assignments())
        saveButton = QPushButton('save preset')
        saveButton.clicked.connect(lambda x: self.save_button_assignments())
        resetButton  = QPushButton('reset buttons')
        resetButton.clicked.connect(self.resetButtons)
        self.hboxLoadSavePreset.addWidget(loadButton)
        self.hboxLoadSavePreset.addWidget(saveButton)
        self.hboxLoadSavePreset.addWidget(resetButton)
        self.hboxLoadSavePreset.addStretch()
        
    def load_button_assignments(self, filename=None):
        goOn = 'On you go'

        if filename is None:
            filename = QFileDialog.getOpenFileName(self, 'Load Button Binding',
                                                   HOME, initialFilter='*.pkl')
            filename = filename[0]
        if len(filename) == 0:
            return
        
        with open(str(filename), 'rt') as filehandle:
            button_bindings = json.load(filehandle)
            for key in ['keys', 'behavAssignment']:
                button_bindings[key] = BehavBinding.from_savable_dict_to_dict_of_objects(button_bindings[key])

        if button_bindings['selected_device'] not in self.input_device_names:
            goOn = 'InputDeviceNotFound'

        listOfSuperfluousBehav = self._get_assigned_buttons_of_undefined_behaviours(button_bindings)

        # if you found any superfluous behaviours set goOn 
        if len(listOfSuperfluousBehav) != 0:
            goOn = 'SuperfluousBehav'

        # all is fine we can set the button binding
        if goOn == 'On you go':
            self.setButtonPreset(button_bindings)
            return
        if not warningFlag:
            return
        # throw warnings if warning flags say so
        # the input device was not found throw warning
        if goOn == 'InputDeviceNotFound':
            msg = 'Tried to assign buttons for '
            msg += button_bindings['selected_device']
            msg += '.\n Please connect this device to the computer and restart the program!'
            QMessageBox.warning(self, 'Wrong Input device', msg)
            return
        # create dialogue message
        msg = 'The following behaviours do not match current behavioural data: \n'
        for behav in listOfSuperfluousBehav:
            msg = msg + behav + ', '
        msg = msg[0:-3]
        msg = msg + '\n Do you still want to load this preset?'
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Information )
        msgBox.setText( "Found too many behaviours")
        msgBox.setInformativeText( msg )
        msgBox.addButton( QMessageBox.Yes )
        msgBox.addButton( QMessageBox.No )

        msgBox.setDefaultButton( QMessageBox.No ) 
        ret = msgBox.exec_()
        #handle response
        if ret == QMessageBox.Yes:
            # delete superfluous behaviours
            bAs = button_bindings['behavAssignment']
            kAs = button_bindings['keys']
            for sfKey in listOfSuperfluousBehav:
                kAsKey = bAs[sfKey].keyBinding
                del bAs[sfKey]
                del kAs[kAsKey]
            # and reassign 
            button_bindings['behavAssignment'] = bAs
            button_bindings['keys']            = kAs
            self.setButtonPreset(button_bindings)

    def _get_assigned_buttons_of_undefined_behaviours(self, button_bindings):
        listOfBehaviours = self.behavAssignment.keys()
        listOfSuperfluousBehav = list()
        for key in button_bindings['behavAssignment']:
            if key not in listOfBehaviours:
                listOfSuperfluousBehav.append(key)
        return listOfSuperfluousBehav

    def setButtonPreset(self, buttonBindingSaveDict):
        self.selected_device = buttonBindingSaveDict['selected_device'] 
        self.deviceLayout    = buttonBindingSaveDict['deviceLayout']
        self.keys            = buttonBindingSaveDict['keys']
        self.behavAssignment = buttonBindingSaveDict['behavAssignment']
        # update with current icons from animal tab
        self.update_icons()
        # the device number might change so this has to be set new if not -1
        self.deviceNumber    = self.input_device_names.index(buttonBindingSaveDict['selected_device'])
        
        self.makeJoyStickInfo()
        self.makeBehaviourSummary()

    def update_icons(self):
        for i in range(len(self.animal_tabs)):
            behav_dict = self.animal_tabs[i].behaviour_dicts
            for j in range(len(behav_dict)):
                icon_path = behav_dict[j]['icon']
                key = f'A{i}_{behav_dict[j]["name"]}'
                if key in self.behavAssignment:
                    self.behavAssignment[key].icon_path = icon_path

    def save_button_assignments(self, filename=None):
        for key in self.behavAssignment.keys():
            buttonKey = self.behavAssignment[key].keyBinding
            # check if keyBinding is the same in both dictionaries
            if buttonKey not in self.keys:
                QMessageBox.warning(self, 'Key Assignment failed!',
                                    key + " is not assigned to a key / button",
                                    QMessageBox.Ok)
                return

            bAbehav = self.behavAssignment[key].behaviour
            kAbehav = self.keys[buttonKey].behaviour

            if kAbehav != bAbehav:
                QMessageBox.warning(self, 'Behaviours Not Synchronized!',
                                    "There is an internal problem with " + bAbehav + "/" + kAbehav,
                                    QMessageBox.Ok)
                return

        button_binding_save_dict = self._create_button_binding_dict()

        if filename is None:
            filename = QFileDialog.getSaveFileName(self, 'Save Button Binding', HOME, initialFilter='*.pkl')
            filename = str(filename[0])
        if len(filename) == 0:
            return

        with open(filename, 'wt') as filehandler:
            json.dump(button_binding_save_dict, filehandler)

    def _create_button_binding_dict(self):
        d = {}
        d.update({'selected_device': self.selected_device})
        d.update({'deviceLayout': self.deviceLayout})
        d.update({'deviceNumber': self.deviceNumber})
        d.update({'keys': BehavBinding.from_object_dict_to_savable_dict(self.keys)})
        d.update({'behavAssignment': BehavBinding.from_object_dict_to_savable_dict(self.behavAssignment)})
        return d

    def makeJoyStickInfo(self):
        if (self.deviceNumber == -2):
            self.makeJoyStickInfoInitial()
        else:
            self.makeSelectedJoyStickInfo()

    def makeSelectedJoyStickInfo(self):
        self.clearLayout(self.hboxJoyStickInfo)
        vBoxDevice = QVBoxLayout()
        joyName  = QLabel(self.input_device_names[self.deviceNumber], self)
        joyName.setStyleSheet(self.labelStyle)
        vBoxDevice.addWidget(joyName)

        odKeys = collections.OrderedDict(sorted(self.keys.items()))
        try:
            for key, bBinding in odKeys.iteritems():
                hbox = self.makeBehavBindingInfo(key,bBinding)
                vBoxDevice.addLayout(hbox)
        except AttributeError:
            for key, bBinding in odKeys.items():
                hbox = self.makeBehavBindingInfo(key,bBinding)
                vBoxDevice.addLayout(hbox)
        vBoxDevice.addStretch
        self.hboxJoyStickInfo.addLayout(vBoxDevice)
        self.hboxJoyStickInfo.addStretch()
    
    def makeKeyboardInfo(self):
        vboxTemp = QVBoxLayout()
        joyName  = QLabel('Keyboard' ,self)
        joyName.setStyleSheet(self.labelStyle)
        vboxTemp.addWidget(joyName)
        if bool(self.keys):
            pass
        else:
            keyMessage  = QLabel('no keys defined' ,self)
            vboxTemp.addWidget(keyMessage)
        vboxTemp.addStretch()
        return vboxTemp
    
    def makeJoyStickInfoInitial(self):
        self.clearLayout(self.hboxJoyStickInfo)
        for joyI in range(self.joysticNum):
            vboxTemp = QVBoxLayout()
            joyName  = QLabel(self.input_device_names[joyI], self)
            joyName.setStyleSheet(self.labelStyle)
            vboxTemp.addWidget(joyName)
            for i in range(self.axesNum[joyI]):
                widget = self.makeDeviceFeatureInfo('axis + ',i,'None','None')
                vboxTemp.addLayout(widget)
                widget = self.makeDeviceFeatureInfo('axis - ',i,'None','None')
                vboxTemp.addLayout(widget)
            for i in range(self.buttonsNum[joyI]):
                widget = self.makeDeviceFeatureInfo('button',i,'None','None')
                vboxTemp.addLayout(widget)
            for i in range(self.hatsNum[joyI]):
                widget = self.makeDeviceFeatureInfo('hat h+ ',i,'None','None')
                vboxTemp.addLayout(widget)
                widget = self.makeDeviceFeatureInfo('hat h- ',i,'None','None')
                vboxTemp.addLayout(widget)
                widget = self.makeDeviceFeatureInfo('hat v+ ',i,'None','None')
                vboxTemp.addLayout(widget)
                widget = self.makeDeviceFeatureInfo('hat v- ',i,'None','None')
                vboxTemp.addLayout(widget)
            vboxTemp.addStretch()
            self.hboxJoyStickInfo.addLayout(vboxTemp)
        keyBoardWiget = self.makeKeyboardInfo()
        self.hboxJoyStickInfo.addLayout(keyBoardWiget)
        self.hboxJoyStickInfo.addStretch()    
    
    def makeBehavBindingInfo(self,key,bBinding):
        # initialise return value
        hboxTemp = QHBoxLayout()
        #make text labels
        if key != bBinding.keyBinding:
            print('Error key is not binding : ' +key + ' ' +bBinding.keyBinding)
        labelsList = list()
        labelsList.append(QLabel(key +' :',self))
        labelsList.append(QLabel('animal No ' + str(bBinding.animal),self))
        labelsList.append(QLabel(bBinding.behaviour,self))
        # test if icon is available and add if so
        if (bBinding.icon_path != 'None'):
            pass
        # set labels to transparent background
        for i in range(3):
            labelsList[i].setStyleSheet(self.labelStyle)
        # adjust behaviour color
        labelsList[2].setStyleSheet('color: '+bBinding.color) 
        # add widgets to layout !!! need to add icon when implemented
        for i in range(3):
            hboxTemp.addWidget(labelsList[i])
        #return layout
        return hboxTemp
        
    def makeDeviceFeatureInfo(self,devFeature,number,animal,behaviour):
        hboxTemp = QHBoxLayout()
        deviceText = devFeature + ' ' + str(number)
        deviceLabel  = QLabel(deviceText ,self)
        animalLabel  = QLabel(animal ,self)
        behavLabel  = QLabel(behaviour ,self)
        hboxTemp.addWidget(deviceLabel)
        hboxTemp.addWidget(animalLabel)
        hboxTemp.addWidget(behavLabel)
        return hboxTemp

    def makeDeviceChoice(self):
        self.lbl_input_assign = QLabel("select device to assign ",self)
        self.lbl_input_assign.setStyleSheet(self.labelStyle)
        self.combo_input_assign = QComboBox(self)
        for device in self.input_device_names:
            self.combo_input_assign.addItem(device)
        # add signal slot for assignment change
        self.combo_input_assign.activated[str].connect(self.set_assignDevice)
        self.hboxDeviceChoice.addWidget(self.lbl_input_assign)
        self.hboxDeviceChoice.addWidget(self.combo_input_assign)
        
        # layout
        self.lbl_input_device = QLabel("select device layout ",self)
        self.lbl_input_device.setStyleSheet(self.labelStyle)
        self.combo_input_device = QComboBox(self)
        for device in DEVICES.keys():
            self.combo_input_device.addItem(device)
        #add signal slot for background change
        self.combo_input_device.activated[str].connect(self.set_device)
        self.hboxDeviceChoice.addWidget(self.lbl_input_device)
        self.hboxDeviceChoice.addWidget(self.combo_input_device)
        self.hboxDeviceChoice.addStretch()
        
    def makeMovieInfoBox(self):
        # top label
        movieBox = QVBoxLayout()
        nameLabel = QLabel('movie actions')
        nameLabel.setStyleSheet(self.labelStyle)
        movieBox.addWidget(nameLabel)
        behavAs = collections.OrderedDict(sorted(self.behavAssignment.items()))
        try:
            item_iterator = behavAs.iteritems()
        except AttributeError:
            item_iterator = behavAs.items()
        for key,binding in item_iterator:
            if binding.animal == 'movie':
                tempBox = QHBoxLayout()
                behavLabel = QLabel(binding.behaviour)
                behavLabel.setStyleSheet('color: '+ binding.color) 
                btn_setUIC=QPushButton('assign button/key')

                buttonNow = binding
                # double lambda to get the variable out of the general scope and let each button call assignBehav
                # with its own behaviour
                btn_setUIC.clicked.connect((lambda buttonNow: lambda: self.assignBehav(buttonNow))(buttonNow))
                # now check if the behaviour is allready in behavAssignments
                buttonLabel = QLabel(binding.keyBinding)
                if binding.keyBinding == 'no button assigned':
                    buttonLabel.setStyleSheet('color: #C0C0C0') 
                else:
                    buttonLabel.setStyleSheet('color: #ffffff') 

                tempBox.addWidget(behavLabel)
                tempBox.addWidget(btn_setUIC)
                tempBox.addWidget(buttonLabel)
                movieBox.addLayout(tempBox)

        return movieBox
    
    def makeBehaviourSummary(self):
        self.clearLayout(self.hboxConciseBehav)
        # ------------------------
        #      behaviour widgets
        # ------------------------
        
        # Create step label
        self.behav_stepLabel = QLabel('Behaviours: ')
        self.behav_stepLabel.resize(20,40)
        self.behav_stepLabel.setStyleSheet(self.labelStyle)
        self.hboxConciseBehav.addWidget(self.behav_stepLabel)
        
        # here for loop!
        self.animal_tabs = self.parent.get_animal_tabs()
        for animalI in range(len(self.animal_tabs)):            
            # Create info label
            vbox = self.makeBehavInfoBox(animalI,self.animal_tabs[animalI].name,self.animal_tabs[animalI].behaviour_dicts)
            self.hboxConciseBehav.addLayout(vbox) 
        
        # add movie behaviours
        vbox = self.makeMovieInfoBox()
        self.hboxConciseBehav.addLayout(vbox) 
        self.hboxConciseBehav.addStretch()

        self.makeJoyStickInfo()

    def makeBehavInfoBox(self,animalNo,animalName,behavDict):
        # top label
        behavBox = QVBoxLayout()
        nameLabel = QLabel(animalName + ' (A' +str(animalNo) + ')')
        nameLabel.setStyleSheet(self.labelStyle)
        behavBox.addWidget(nameLabel)
        behavAs = self.slicedict(self.behavAssignment,'A'+str(animalNo)+'_')
        behavAs = self.syncronizeBehaviourTabAndBindings(animalNo,behavDict,behavAs)
        behavAs = collections.OrderedDict(sorted(behavAs.items()))

        try:
            item_iterator = behavAs.iteritems()
        except AttributeError:
            item_iterator = behavAs.items()
        
        for key,binding in item_iterator:
            tempBox = QHBoxLayout()
            behavLabel = QLabel(binding.behaviour)
            behavLabel.setStyleSheet('color: '+ binding.color) 
            btn_setUIC=QPushButton('assign button/key')

            buttonNow = binding
            # double lambda to get the variable out of the general scope and let each button call assignBehav
            # with its own behaviour
            btn_setUIC.clicked.connect((lambda buttonNow: lambda: self.assignBehav(buttonNow))(buttonNow))
            # now check if the behaviour is allready in behavAssignments
            buttonLabel = QLabel(binding.keyBinding)
            if binding.keyBinding == 'no button assigned':
                buttonLabel.setStyleSheet('color: #C0C0C0') 
            else:
                buttonLabel.setStyleSheet('color: #ffffff') 

            tempBox.addWidget(behavLabel)
            if binding.icon_path != 'None' and binding.icon_path is not None and binding.icon_path:
                imageLabel =  QLabel() 
                pixmap =  QPixmap(binding.icon_path)
                pixmap = pixmap.scaledToWidth(20)
                imageLabel.setStyleSheet('color: ' + binding.color)
                imageLabel.setPixmap(pixmap)
                tempBox.addWidget(imageLabel)
            tempBox.addWidget(btn_setUIC)
            tempBox.addWidget(buttonLabel)
            behavBox.addLayout(tempBox)

        return behavBox

    def syncronizeBehaviourTabAndBindings(self,animalNo,behavDict,behavAs):
        startPoint = len('A'+str(animalNo)+'_')
        listOfUserBehaviours = list()
        for bd in behavDict:
            listOfUserBehaviours.append(bd['name']) 
        listOfUserBehaviours.append('delete') 
        listOfAssignments = behavAs.keys()
        
        for key in listOfAssignments:
            if key[startPoint:] not in listOfUserBehaviours:
                del behavAs[key]
                buttonKey = self.behavAssignment[key].keyBinding
                del self.behavAssignment[key]

                if buttonKey != 'no button assigned':                
                    self.keys[buttonKey].behaviour = 'None'
                    self.keys[buttonKey].animal = 'None'
                    self.keys[buttonKey].color     = '#C0C0C0'
        
        for i in range(len(behavDict)):
            behav = 'A'+str(animalNo)+'_'+behavDict[i]['name']
            if behav not in listOfAssignments:
                temp = BehavBinding(animal     = animalNo,
                                    icon_path= behavDict[i]['icon'],
                                    behaviour  = behavDict[i]['name'],
                                    color      = behavDict[i]['color'],
                                    key_binding='no button assigned',
                                    UICdevice  = 'None')
                
                self.behavAssignment.update({behav:temp})
                behavAs.update({behav:temp})
        return behavAs
         
    def slicedict(self,d, s):
        try:
            return {k:v for k,v in d.iteritems() if k.startswith(s)}
        except AttributeError:
            return {k:v for k,v in d.items() if k.startswith(s)}

    def clearLayout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())
 
    def assignBehav(self,buttonBinding):
        goOn = False

        # check if device was selected
        if (self.selected_device == ""):
            QMessageBox.warning(self, 'Set device first!',
                                "You need to choose an input device first",
                                QMessageBox.Ok)
            goOn = False  
        else:
            #check if layout was selected
            if (self.deviceLayout == ""):
                QMessageBox.warning(self, 'Set layout first!',
                                    "You need to choose an input device layout first",
                                    QMessageBox.Ok)  
                goOn = False

        # Everything was setup correctly 
            else:
                #Check if this is a keyboard assignment
                if self.deviceNumber == -1:
                    text, ok = QInputDialog.getText(self, 'Press', 'Key Entry:')
                    if ok:       
                        inputCode = str(text)
                        goOn = True
                    else:
                        goOn = False
                # No this is a gamepad assignment
                else:
                    
                    inputCode = self.waitOnUICpress(self.deviceNumber)
                    goOn = True
        
        if goOn:
            #check if key allready exists
            if inputCode in self.keys.keys():           
                # get old button binding object 
                oldButtonBinding  = self.keys[inputCode]
                # we check if there was allready a behaviour attached to this button
                if oldButtonBinding.behaviour != 'None':
                    # the button binding also in the behavAssignment
                    key = self.makeAnimalBehavKey(oldButtonBinding)
                    oldBehaviourBinding = self.behavAssignment[key]
                    oldBehaviourBinding.keyBinding = 'no button assigned'
                    self.behavAssignment.update({key : oldBehaviourBinding})

                # check if a button was assigned to that behaviour
                key = self.makeAnimalBehavKey(buttonBinding)
                oldBehaviourBinding = self.behavAssignment[key]
                if oldBehaviourBinding.keyBinding != 'no button assigned':        
                    # if so delete old behaviour info
                    oldButtonBinding = self.keys[oldBehaviourBinding.keyBinding]
                    oldButtonBinding.color = '#C0C0C0'
                    oldButtonBinding.animal = 'None'
                    oldButtonBinding.behaviour = 'None'
                    self.keys.update({oldBehaviourBinding.keyBinding:oldButtonBinding})
                    

                # get behaviour and set new binding
                key = 'A'+str(buttonBinding.animal) +'_'+buttonBinding.behaviour
                newBinding      =  copy.deepcopy(self.behavAssignment[key])
                newBinding.animal     = buttonBinding.animal
                newBinding.behaviour  = buttonBinding.behaviour
                newBinding.color      = buttonBinding.color
                newBinding.keyBinding = inputCode
                # icon has to be attached here as well
                newBinding.device = self.selected_device

                #update both lists
                self.behavAssignment.update({key : newBinding})
                self.keys.update({inputCode : copy.deepcopy(newBinding)})
            else:
                
                # check if a button was assigned to that behaviour
                key = self.makeAnimalBehavKey(buttonBinding)
                oldBehaviourBinding = self.behavAssignment[key]
                if oldBehaviourBinding.keyBinding != 'no button assigned':        
                    # if so delete old behaviour info
                    oldButtonBinding = self.keys[oldBehaviourBinding.keyBinding]
                    oldButtonBinding.color = '#C0C0C0'
                    oldButtonBinding.animal = 'None'
                    oldButtonBinding.behaviour = 'None'
                    self.keys.update({oldBehaviourBinding.keyBinding:oldButtonBinding})
                # get behaviour and set new binding
                key = 'A'+str(buttonBinding.animal) +'_'+buttonBinding.behaviour
                newBinding      =  copy.deepcopy(self.behavAssignment[key])
                newBinding.animal     = buttonBinding.animal
                newBinding.behaviour  = buttonBinding.behaviour
                newBinding.color      = buttonBinding.color
                newBinding.keyBinding = inputCode
                # icon has to be attached here as well
                newBinding.device = self.selected_device
            
            #update both lists
            self.behavAssignment.update({key : newBinding})
            self.keys.update({inputCode : copy.deepcopy(newBinding)})    
            # update GUI
            self.makeJoyStickInfo()
            self.makeBehaviourSummary()
    def keyMesgUpdate(self):
        pass

    def waitOnUICpress(self, mode):
        waitingForEvent = True
        pygame.event.clear()  
        while waitingForEvent:
            for event in pygame.event.get():  
                if (event.type == pygame.JOYBUTTONDOWN) :          
                    waitingForEvent = False  
                    inputCode ='B' + str(event.button)              
                    return inputCode
                if (event.type == pygame.JOYAXISMOTION):
                    value = event.dict['value']
                    axis  = event.dict['axis']
                    if abs(value) > 0.75:
                        if value > 0:                            
                            inputCode = 'A'+str(axis)+'+'
                        else:        
                            inputCode = 'A'+str(axis)+'-'
                            
                        waitingForEvent = False
                        return inputCode
                if (event.type == pygame.JOYHATMOTION):
                    value = event.dict['value']
                    inputCode = 'H'+str(value[0])+str(value[1])
                    waitingForEvent = False
                    return inputCode
                        

        # event = pygame.event.wait()
        # if event.type == KEYDOWN:
        #     return event.key
    
    def set_assignDevice(self, device):
        
        self.selected_device = str(device)
        if device == 'Keyboard':
            self.deviceNumber    = -1
            self.selected_device = device
        else:       
            self.deviceNumber = self.input_device_names.index(device)
            self.joystick =  pygame.joystick.Joystick(self.deviceNumber )
            self.joystick.init()
            self.makeJoyStickInfo()
        self.makeBehaviourSummary()
        
    def set_device(self, device):
        if (self.selected_device == ""):
            QMessageBox.warning(self, 'Set device first!',
                                            "You need to choose an input device first",
                                            QMessageBox.Ok)  
        else:
            # This needs to be questioned before doing
            self.deviceLayout    = str(device)
            self.initializeKeys(device)
            #
            self.pixmap = QPixmap(DEVICES[str(device)])
            self.background_image.setPixmap(self.pixmap.scaled(self.background_image.size(),Qt.KeepAspectRatio))
            self.background_image.setScaledContents(True)
            self.makeJoyStickInfo()
            self.makeBehaviourSummary()

    def initializeKeys(self,device):
        
        self.keys.clear()
        
        if (device== "X-Box"):           

            #                 AT2+                                         AT5+
            #                  B4                                           B5
            #            ,,,,---------,_                               _,--------,,,,
            #          /-----```````---/`'*-,_____________________,-*'`\---``````-----\
            #         /     A1-                      B8                   ,---,        \
            #        /   , -===-- ,          B6     ( X )    B7     ,---, '-B3' ,---,   \
            #       /A0-||'( : )'||A0+     (<)-|           |-(>)   'B2-' ,---, 'B1-'    \
            #      /    \\ ,__, //           H01                      A4- '-B0'           \
            #     /         A1+         ,--'`!`!`'--,              ,--===--,               \
            #    /  B9              H-10||  ==O==  ||H10       A3-||'( : )'||A3+            \
            #   /                       '--, !,!, --'             \\  ,__, //                \
            #  |                          ,--------------------------, A4+     B10            |
            #  |                      ,-'`  H0-1                     `'-,                     |
            #  \                   ,-'`                                  `'-,                 /
            #   `'----- ,,,, -----'`                                       `'----- ,,,, -----'`
            


            self.keys = {"B0"   : BehavBinding(device = self.selected_device, key_binding="B0", color ='#C0C0C0'),
                         "B1"   : BehavBinding(device = self.selected_device, key_binding="B1", color ='#C0C0C0'),
                         "B2"   : BehavBinding(device = self.selected_device, key_binding="B2", color ='#C0C0C0'),
                         "B3"   : BehavBinding(device = self.selected_device, key_binding="B3", color ='#C0C0C0'),
                         "B4"   : BehavBinding(device = self.selected_device, key_binding="B4", color ='#C0C0C0'),
                         "B5"   : BehavBinding(device = self.selected_device, key_binding="B5", color ='#C0C0C0'),
                         "B5"   : BehavBinding(device = self.selected_device, key_binding="B5", color ='#C0C0C0'),
                         "B6"   : BehavBinding(device = self.selected_device, key_binding="B6", color ='#C0C0C0'),
                         "B7"   : BehavBinding(device = self.selected_device, key_binding="B7", color ='#C0C0C0'),
                         "B8"   : BehavBinding(device = self.selected_device, key_binding="B8", color ='#C0C0C0'),
                         "A2+"  : BehavBinding(device = self.selected_device, key_binding="A2+", color ='#C0C0C0'),
                         "A5+"  : BehavBinding(device = self.selected_device, key_binding="A5+", color ='#C0C0C0'),
                         "A2-"  : BehavBinding(device = self.selected_device, key_binding="A2-", color ='#C0C0C0'),
                         "A5-"  : BehavBinding(device = self.selected_device, key_binding="A5-", color ='#C0C0C0'),
                         "H01"  : BehavBinding(device = self.selected_device, key_binding="H01", color ='#C0C0C0'),
                         "H0-1" : BehavBinding(device = self.selected_device, key_binding="H0-1", color ='#C0C0C0'),
                         "H-10" : BehavBinding(device = self.selected_device, key_binding="H-10", color ='#C0C0C0'),
                         "H10"  : BehavBinding(device = self.selected_device, key_binding="H10", color ='#C0C0C0')}

            standardKeys = ["B9", "B10","A0+", "A0-","A1-", "A1+","A3+","A3-","A4-","A4+"]  
            movieBehavs  = ["toggleRunMov","stopToggle","runMovForward","runMovReverse",
                            "changeFPShigh","changeFPSlow","changeFrameNoHigh1","changeFrameNoLow1",
                            "changeFrameNoHigh10","changeFrameNoLow10"]   

            self.fillStandardKeys(standardKeys,movieBehavs)           

                         
            
        elif (device == "Playstation"):
            
            #           B6                                   B7
            #           B4                                   B5
            #        _=====_                               _=====_
            #       / _____ \                             / _____ \
            #     +.-'_____'-.---------------------------.-'_____'-.+
            #    /   |     |  '.                       .'  |     |   \
            #   / ___| H2+ |___ \                     / ___| B0  |___ \
            #  / |             | ;  __           _   ; |             | ;
            #  | | H1-      H1+|   |__|B8     B9|_:> | | B3       B1 | |
            #  | |___       ___| ;SELECT       START ; |___       ___| ;
            #  |\    | H2- |    /  _     ___      _   \    | B2  |    /|
            #  | \   |_____|  .','" "', |___|  ,'" "', '.  |_____|  .' |
            #  |  '-.______.-' /  A1-  \ANALOG/  A4-  \  '-._____.-'   |
            #  |               |A0- A0+|------|A3- A3+|                |
            #  |              /\  A1+  /      \  A4+  /\               |
            #  |             /  '.___.'        '.___.'  \              |
            #  |            /     B10            B11     \             |
            #   \          /                              \           /
            #    \________/                                \_________/
                                #  PS2 CONTROLLER

            self.keys = {"B0"   : BehavBinding(device = self.selected_device, key_binding="B0", color ='#C0C0C0'),
                         "B1"   : BehavBinding(device = self.selected_device, key_binding="B1", color ='#C0C0C0'),
                         "B2"   : BehavBinding(device = self.selected_device, key_binding="B2", color ='#C0C0C0'),
                         "B3"   : BehavBinding(device = self.selected_device, key_binding="B3", color ='#C0C0C0'),
                         "B4"   : BehavBinding(device = self.selected_device, key_binding="B4", color ='#C0C0C0'),
                         "B5"   : BehavBinding(device = self.selected_device, key_binding="B5", color ='#C0C0C0'),
                         "B5"   : BehavBinding(device = self.selected_device, key_binding="B5", color ='#C0C0C0'),
                         "B6"   : BehavBinding(device = self.selected_device, key_binding="B6", color ='#C0C0C0'),
                         "B7"   : BehavBinding(device = self.selected_device, key_binding="B7", color ='#C0C0C0'),
                         "B8"   : BehavBinding(device = self.selected_device, key_binding="B8", color ='#C0C0C0'),
                         "B9"   : BehavBinding(device = self.selected_device, key_binding="B9", color ='#C0C0C0'),
                         "H01"  : BehavBinding(device = self.selected_device, key_binding="H01", color ='#C0C0C0'),
                         "H0-1" : BehavBinding(device = self.selected_device, key_binding="H0-1", color ='#C0C0C0'),
                         "H-10" : BehavBinding(device = self.selected_device, key_binding="H-10", color ='#C0C0C0'),
                         "H10"  : BehavBinding(device = self.selected_device, key_binding="H10", color ='#C0C0C0')}


            standardKeys = ["B10", "B11","A0+", "A0-","A1-", "A1+","A3+","A3-","A4-","A4+"]  
            movieBehavs  = ["toggleRunMov","stopToggle","runMovForward","runMovReverse",
                            "changeFPShigh","changeFPSlow","changeFrameNoHigh1","changeFrameNoLow1",
                            "changeFrameNoHigh10","changeFrameNoLow10"]   

            self.fillStandardKeys(standardKeys,movieBehavs) 

        elif (device == "Keyboard"):
            pass    

    def fillStandardKeys(self,standardKeys,movieBehavs):
        '''
        This function adds the standard movie behaviour functions to the self.keys dict,
        using preset keys        
        '''
        
        for i in range(len(standardKeys)):
            self.behavAssignment['Amovie_'+movieBehavs[i]].device = self.selected_device
            self.behavAssignment['Amovie_'+movieBehavs[i]].keyBinding = standardKeys[i]
            temp = copy.deepcopy( self.behavAssignment['Amovie_'+movieBehavs[i]])
            temp.device = self.selected_device
            temp.keyBinding = standardKeys[i]
            self.keys.update({standardKeys[i]:temp})

            # idx = self.IndexOfDictList(self.bindingList,'behaviour',movieBehavs[i])
            # self.bindingList[idx].update('keyBinding':standardKeys[i])
            # self.bindingList[idx].update('device': self.selected_device)

    def makeAnimalBehavKey(self,obj):
         return 'A' + str(obj.animal) + '_' + obj.behaviour
    def initialiseBehavAssignment(self):
        self.behavAssignment.clear()

        for animalI in range(len(self.animal_tabs)):
            behavDict = self.animal_tabs[animalI].behaviour_dicts
            
            # add all behaviours
            for i in range(len(behavDict)):
                temp = BehavBinding(animal = animalI,
                                    icon_path= behavDict[i]['icon'],
                                    behaviour = behavDict[i]['name'],
                                    color = behavDict[i]['color'],
                                    key_binding='no button assigned',
                                    device = 'None')

                self.behavAssignment.update({'A'+str(animalI)+'_'+behavDict[i]['name']:temp})
                # self.bindingList.append({animal    : animalI,
                #                         icon_path    :'None',
                #                         behaviour  : behavDict[i]['name'],
                #                         color      : behavDict[i]['color'],
                #                         keyBinding : 'no button assigned',
                #                         device  : 'None'})
            # add delete function
            temp = BehavBinding(animal=animalI,
                                icon_path='None',
                                behaviour='delete',
                                color='#ffffff',
                                key_binding='no button assigned',
                                device='None')
            
            # self.bindingList.append({animal    : animalI,
            #                         icon_path    : 'None',
            #                         behaviour  : 'delete',
            #                         color      : '#ffffff',
            #                         keyBinding : 'no button assigned',
            #                         device  : 'None'})
            self.behavAssignment.update({'A'+str(animalI)+'_delete':temp})
            
        # add movie behaviours    
        movieBehavs = ['toggleRunMov', 'stopToggle'   , 'runMovReverse'    , 'runMovForward',
                       'changeFPSlow', 'changeFPShigh', 'changeFrameNoLow1', 
                       'changeFrameNoHigh1', 'changeFrameNoLow10', 'changeFrameNoHigh10']
        for behavI in movieBehavs:
            temp = BehavBinding(animal='movie',
                                color='#ffffff',
                                icon_path='None',
                                behaviour=behavI,
                                key_binding='no button assigned',
                                device='None')
            # self.bindingList.append({animal    : animalI,
            #                         icon_path    :'None',
            #                         behaviour  : behavDict[i]['name'],
            #                         color      : behavDict[i]['color'],
            #                         keyBinding : 'no button assigned',
            #                         device  : 'None'})
            self.behavAssignment.update({"Amovie_"+behavI:temp})

    def close_event(self):
        self.save_button_assignments(filename =HOME + '/.pyvisor/guidefaults_buttons.json')

    def resizeEvent(self, event):
        self.background_image.resize(event.size())
        
    def getAssignments(self):
        return (self.keys, self.behavAssignment)
    
    def getSelectedLayout(self):
        return self.deviceLayout
    def resetButtons(self):
        # ============================
        # Get and Initialize Behaviour
        # ============================

        self.keys            = dict()
        self.behavAssignment = dict()
        self.animal_tabs = self.parent.get_animal_tabs()
        self.selected_device = ""
        self.deviceLayout = ""
        self.deviceNumber =-2 # -1= not selected | last  = keyboard, after that it is in the recognition order by pygame
        self.initialiseBehavAssignment()
        self.lastKeyPressed = (71,'G')

        # ===========================
        # Joy stick initiation
        # ===========================
        
        # Get count of joysticks
        self.joysticNum = pygame.joystick.get_count()
        
        # variables
        self.hatsNum         = [None]*self.joysticNum
        self.buttonsNum      = [None]*self.joysticNum
        self.axesNum         = [None]*self.joysticNum
        self.input_device_names         = [None] * (self.joysticNum + 1)
        
        for i in range(self.joysticNum):
            self.joystick =  pygame.joystick.Joystick(i)
            self.joystick.init()
            # count the axes
            self.axesNum[i]    = self.joystick.get_numaxes()
            self.buttonsNum[i] = self.joystick.get_numbuttons()
            self.hatsNum[i]    = self.joystick.get_numhats()
            self.input_device_names[i]    = self.joystick.get_name()
        self.input_device_names[-1] = 'Keyboard'

        self.makeBehaviourSummary()
