# -*- coding: utf-8 -*-
"""
Created on Tue May 24 17:31:07 2016

@author: bgeurten
"""

import pygame
import numpy as np
import os
from . import MediaHandler
from . import UserInputControl
from . import dataIO
from .analysis import analysis_online as analysis
from . import animalEthogram as aE
from PIL import Image

this_files_directory = os.path.dirname(os.path.realpath(__file__))


class ManualEthologyScorer():
    def __init__(self):

        self.window = pygame.display
        self.movie = []
        self.fps = 100
        self.mediafps = 25
        self.mediaForceGrayScale = True
        self.movBackWards = False
        self.mediaType = 'unknown'
        print(this_files_directory)
        self.deleteIcon = pygame.image.load(
            this_files_directory + '/../resources/icons/game/del.png')        
        
        # preallocate icon positions
        self.iconPos = [[   (0, 0), (0, 96)   ],
                        [   (96, 0), (96, 96)  ],  
                        [  (192, 0), (192, 96) ],  
                        [  (288, 0), (288, 96) ],  
                        [  (384, 0), (384, 96) ], 
                        [  (480, 0), (480, 96) ],   
                        [  (0, 288), (0, 192)  ],
                        [ (96, 288), (96, 192) ],  
                        [(192, 288), (192, 192)],  
                        [(288, 288), (288, 192)],  
                        [(384, 288), (384, 192)], 
                        [(480, 288), (480, 192)]]
                       
        self.lastFrameDrawn = 0
        self.runMov = False
 
        self.animals = []
        self.movPadding = (0,0)
        # data IO
        self.dIO = dataIO.dataIO(self)
        # analyses
        self.anaO = analysis.analysis(self,fps=25)
 



   

###############################################################################
#                               MEDIA CONTROL                                 #
###############################################################################
    def setIconPositions(self):
        
        if (self.mediaType == 'unknown'):
            print('you first have to load a medium')
        else:
            xPos     = [0, 96, 192, 288, 384, 480]    
            yPos     = [0, 96, self.screen.get_height()-96, self.screen.get_height()-144]
                
            self.iconPos = [[(xPos[0],yPos[0]),(xPos[0],yPos[1])],
                            [(xPos[1],yPos[0]),(xPos[1],yPos[1])],
                            [(xPos[2],yPos[0]),(xPos[2],yPos[1])],
                            [(xPos[3],yPos[0]),(xPos[3],yPos[1])],
                            [(xPos[4],yPos[0]),(xPos[4],yPos[1])],
                            [(xPos[5],yPos[0]),(xPos[5],yPos[1])],
                            [(xPos[0],yPos[2]),(xPos[0],yPos[3])],
                            [(xPos[1],yPos[2]),(xPos[1],yPos[3])],
                            [(xPos[2],yPos[2]),(xPos[2],yPos[3])],
                            [(xPos[3],yPos[2]),(xPos[3],yPos[3])],
                            [(xPos[4],yPos[2]),(xPos[4],yPos[3])],
                            [(xPos[5],yPos[2]),(xPos[5],yPos[3])]]
            print(self.iconPos)
                            
    def updateIconsPerAnimal(self,animal):
        '''
        Updates the display depending on the status variable. 
        '''
         
        for i in range(len(animal.behaviours)):
            try:
                # Status of the animal
                status = animal.behaviours[i].status
                if (status == 1):
                    self.screen.blit(animal.behaviours[i].icon,animal.behaviours[i].iconPos[0])
                elif(status == -1):
                    #check if all behaviours in this disjunctionlist are -1
                    stati = list()
                    for dBI in animal.behaviours:
                        stati.append(dBI.status)
                    # if all stati are -1 this is a real deletion
                    if (sum(stati) == len(stati)*-1):
                        self.screen.blit(self.deleteIcon,animal.behaviours[i].iconPos[0])
                    
                # ethogram for behaviour 1
                if (animal.behaviours[i].ethogram[self.movie.get_frameNo()] == 1):
                    self.screen.blit(animal.behaviours[i].iconT,animal.behaviours[i].iconPos[1])
            except IndexError:
                #print 'overshoot'
                self.movie.frameNo = self.movie.length
         
    def updateIcons(self):
        # plot icons
        for i in range(len(self.animals)):
            self.updateIconsPerAnimal(self.animals[i])
             
        #plot text
        myfont = pygame.font.SysFont(pygame.font.get_default_font(), 15)
        label  = myfont.render("frame: " +str(self.movie.frameNo), 1, (255,255,0))
        label2 = myfont.render("time: " +str(self.movie.get_time()) + ' s', 1, (255,255,0))
        label3 = myfont.render("replay-fps: " +str(self.mediafps), 1, (255,255,0))
        self.screen.blit(label,  (self.MovieWinOffSet+10,self.movie.height-45+144))
        self.screen.blit(label2, (self.MovieWinOffSet+10,self.movie.height-30+144))
        self.screen.blit(label3, (self.MovieWinOffSet+10,self.movie.height-15+144))

    def loadMovie(self,filename):
        pygame.init()
        self.mediaType = 'movie'
        self.movie   = MediaHandler.MediaHandler(filename,'movie')
        
        if (self.fps < self.movie.fps):
            print('The original movie was recorded faster than the refresh rate')
            print('of this tool, so its framerate was reduced to the tools refresh rate')
            self.mediafps = self.fps
        else:
            self.mediafps = self.movie.fps
            
        for i in range(len(self.animals)):
            self.animals[i].resetEthogram(self.movie.length)
            
    def loadNorPixSeq(self,filename):
        pygame.init()
        self.mediaType = 'norpix'
        self.movie   = MediaHandler.MediaHandler(filename,'norpix')
        
        if (self.fps < self.movie.fps):
            print('The original movie was recorded faster than the refresh rate')
            print('of this tool, so its framerate was reduced to the tools refresh rate')
            self.mediafps = self.fps
        else:
            self.mediafps = self.movie.fps
            
        for i in range(len(self.animals)):
            self.animals[i].resetEthogram(self.movie.length)

    def loadImageSequence(self,fileInfo):
        pygame.init()
        self.mediaType = 'image'
        self.movie   = MediaHandler.MediaHandler(fileInfo,'image')
        self.mediafps = self.movie.fps
        
        for i in range(len(self.animals)):
            self.animals[i].resetEthogram(self.movie.length)
        
    def refreshMedia(self,clock):
 
        # check if the movie is running (boolean Value self.runMov)
        # if so check if a new frame has to be plotted
        periode  = 1.0/self.mediafps*1000.0
        timeDiff = pygame.time.get_ticks()-self.lastFrameDrawn
        #print periode ,timeDiff
        if (timeDiff>periode)  and (self.runMov == True):
            # if you have to refresh check if you run backwards
            if (self.movBackWards == False):
                frameNo = self.movie.get_frameNo()+1
            else:
                frameNo = self.movie.get_frameNo()-1
            # check that the frame number is not to high or low
            if (frameNo > self.movie.length -2):
                
                self.runMov =False
                #now we stop the behavioural input
                for i in range(len(self.animals)):
                    for j in range(len(self.animals[i].behaviours)):
                        self.animals[i].behaviours[j].setBehaviour(self.animals[i].behaviours[j].status,frameNo)
                        
            elif (frameNo < 0):
                self.runMov =False
            self.lastFrameDrawn = pygame.time.get_ticks()
                
        else:
            frameNo = self.movie.get_frameNo()
        frame = self.movie.getFrame(frameNo)

        if self.mediaForceGrayScale is True:
            frame = Image.fromarray(frame)
            frame = frame.convert('RGB')
            
            
        
        movie_screen=pygame.surfarray.make_surface(np.rot90(frame))
    
        

        #update the movie
        self.screen.fill((0,0,0))
        self.screen.blit(movie_screen,(self.MovieWinOffSet,144))
        self.updateIcons()
        pygame.display.update()
        
###############################################################################
#                               Behavioural Setup                           #
###############################################################################   
    def addAnimal(self,animalName,ethogram,behavLabels,status,disjuncList):   
        self.animals.append(aE.animalEthogram(animalName, # label for the animal
                                             ethogram, # ethogram length
                                             behavLabels, # behaviour labels
                                             status, # beginning status                                                   
                                             disjuncList)) # disjunction list     

    def setAnimal(self,animalName,ethogram,behavLabels,status,disjuncList,animalID):
        self.animals[animalID] = aE.animalEthogram(animalName, # label for the animal
                                                   ethogram, # ethogram length
                                                   behavLabels, # behaviour labels
                                                   status, # beginning status                                                   
                                                   disjuncList) # disjunction list
                
        self.window = pygame.display
        
 
        
        
###############################################################################
#                               User Input                                    #
############################################################################### 
    def setUIC(self,modus,buttonBindings = 0,keyBindings = 0,axisThresh = 0,freeBindingList=0,UICdevice=0):
        # intialise UIC object
        self.uic = UserInputControl.UserInputControl(self.animals,self.movie)
        # use XBox preset
        if (modus == 'XBox'):
            pygame.joystick.init()
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            if buttonBindings == 0:            
                self.uic.setStandardXbox()
            else:
                self.uic.setStandardXbox(buttonBindings = buttonBindings)
        # use PS2 like preset        
        elif (modus == 'PS'):
            pygame.joystick.init()
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            if buttonBindings == 0:            
                self.uic.setStandardPS2()
            else:
                self.uic.setStandardPS2(buttonBindings = buttonBindings)
        #use a keyboard preset
        elif (modus == 'Keyboard'):
            if buttonBindings == 0:            
                self.uic.setStandardKeyB()
            else:
                self.uic.setStandardKeyB(keyBindings = keyBindings)
        # here you have to define buttons/keys, animals and axis thresholds
        elif (modus == 'Free'):
            self.setUICFree(axisThresh,freeBindingList,UICdevice)

    def setUICFree(self,axisThresh,freeBindingList,UICdevice):
        '''
        buttonBindings list of strings
        keyBindings list of keys
        axisThreshold dictionary
        freeBindingList = list of tupels eaach tupel ('bindingString',animalNum (-1) for movie, behaviour num or string 
        '''
        # intialise UIC object
        self.uic = UserInputControl.UserInputControl(self.animals,self.movie)
        #set joypad axis threshold
        if (axisThresh == 0 and UICdevice =='Xbox') or (axisThresh == 0 and UICdevice == 'XBox'):
            axisThresh = {'A0-':-0.6,'A0+':0.6,'A1-':-0.6,'A1+':0.6,
                          'A3-':-0.6,'A3+':0.6,'A4-':-0.6,'A4+':0.6,
                          'A2-':-2,  'A2+':0.6,'A5-':-2,  'A5+':0.6}
        elif axisThresh == 0 and (UICdevice =='PS'):
            axisThresh = {'A0-':-0.3,'A0+':0.3,'A1-':-0.3,'A1+':0.3,
                          'A3-':-0.3,'A3+':0.3,'A4-':-0.3,'A4+':0.3}
        
        self.uic.setFreePad(freeBindingList,axisThresh)
        
     
    
        
###############################################################################
#                               FLOW  CONTROL                                 #
###############################################################################
    def go(self):
        '''
        Main loop here the movie is played and the key down events are caught.
        '''
        if (np.size(self.movie) == 0):
            print('Load movie first, please!')
            return
            
        # clock and movie setup
        clock      = pygame.time.Clock()
        #movSize = self.movie.get_size()
        movSize = (self.movie.width,self.movie.height)
        #setup icons
        icon = pygame.image.load(this_files_directory+"/../resources/MES.png")
        self.window.set_icon(icon)
        self.window.set_caption("Manual Ethology Scorer - " + self.movie.fileName)
        
        #resize if needed
        height = self.movie.height
        width  = self.movie.width
        if (width < 576):
            self.MovieWinOffSet = int((576-width)/2.0)
            width = 576
        else: 
            self.MovieWinOffSet = 0
        height = height+288

        self.screen = self.window.set_mode((int(width),int(height)))
        self.setIconPositions()
        iconPosList = self.iconPos
        for animal in  self.animals:
            numUDJB = len(animal.uniqueDJList)
            animal.assignIconPos2UniqueDJB(iconPosList[0:numUDJB])
            for behaviour in animal.behaviours:
                print(behaviour.iconPos)
            iconPosList = iconPosList[numUDJB:]
        #movie_screen = pygame.Surface(movSize).convert()
      
        
        # start movie
        #self.movie.set_display(movie_screen)
        self.movie.activeFrame = -1
        # This variable is needed to  be able to save out an overlayed movie
        self.refreshMediaFlag = True
        # during show time
        analysing = True
        while analysing:
            # handle events such as key and button presses
            for event in pygame.event.get():    
                if event.type == pygame.QUIT:
                     analysing= False
                     
                if event.type == pygame.JOYBUTTONDOWN:
                    inputCode ='B' + str(event.button)                    
                    self.mediafps,self.runMov,self.movBackWards = self.uic.checkPad(event,self.mediafps,self.runMov,self.movBackWards,inputCode)
                    
                if event.type == pygame.JOYAXISMOTION:
                    value = event.dict['value']
                    axis  = event.dict['axis']
                    inputCode = 'A'+str(axis)
                    try:
                        
                        if value < self.uic.axisThresh[inputCode+'-']:
                            inputCode = inputCode+'-'
                            self.mediafps,self.runMov,self.movBackWards = self.uic.checkPad(event,self.mediafps,self.runMov,self.movBackWards,inputCode)
                        elif (value > self.uic.axisThresh[inputCode+'+']):
                            inputCode = inputCode+'+'
                            self.mediafps,self.runMov,self.movBackWards = self.uic.checkPad(event,self.mediafps,self.runMov,self.movBackWards,inputCode)    
                           
                    except KeyError:
                        print('This key was not assigned!: ',inputCode)
                if event.type == pygame.JOYHATMOTION:
                    value = event.dict['value']
                    inputCode = 'H'+str(value[0])+str(value[1])
                    
                    if (inputCode != 'H00'):
                        self.mediafps,self.runMov,self.movBackWards = self.uic.checkPad(event,self.mediafps,self.runMov,self.movBackWards,inputCode)
                    
                if event.type == pygame.KEYDOWN:
                    self.mediafps,self.runMov,self.movBackWards = self.uic.checkKeys(event,self.mediafps,self.runMov,self.movBackWards)
            
            if self.refreshMediaFlag:
                self.refreshMedia(clock)
                #save the current status to the ethogram
            clock.tick(self.fps)
        
        pygame.quit()
        
###############################################################################
#                               DATA HANDLING                                 #
###############################################################################
    def get_data(self):
        if self.animals:
            
            if (len(self.animals) == 1):
                return self.animals[0].getEthogram()
            else:
                temp  = self.animals[0].getEthogram()
                for i in range(1,len(self.animals)):
                    temp2 = self.animals[i].getEthogram()
                    temp = np.hstack((temp,temp2))
                
                return temp  
        else:
            return False

    def get_labels(self):
        
        if self.animals:
            
            if (len(self.animals) == 1):
                temp  = [self.animals[0].animalName+ ' : ' + s for s in self.animals[0].behavLabelList]
            else:
                temp  = [self.animals[0].animalName+ ' : ' + s for s in self.animals[0].behavLabelList]
                for i in range(1,len(self.animals)):
                    temp = np.hstack((temp,[self.animals[i].animalName+ ' : ' + s for s in self.animals[i].behavLabelList]))
                
            return temp
        else:
            return False
        
    def save_data(self,fpos,modus='text'):
        data        = self.get_data()
        behavLabels = self.get_labels()

        if (modus=='text'):
            self.dIO.saveAsTXT(fpos,data,behavLabels)
        elif (modus=='xlsx'):
            self.dIO.saveAsXLSX(fpos,data,behavLabels)
        elif (modus=='matLab'):
            self.dIO.saveAsMat(fpos,data,behavLabels)
        elif (modus=='pickle'):
            self.dIO.saveAsPy(fpos,data)
        else:
            print('unknownModus')
        
    def load_data(self,fpos,modus='pickle'):
       if (modus=='pickle'):
           self.animals =  self.dIO.loadPickle(fpos,self.animals)
       else:
           print('unknownModus')


