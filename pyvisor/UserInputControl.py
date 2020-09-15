# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 18:26:27 2016

@author: bgeurten
"""
import copy
class UserInputControl():
    def __init__(self,animals,movie,
                 keyBindings = [113,119,97,115,120,121,111,112,107,108,109,44,
                                116,117,32,13,8,50,49,276,275,274,273],
                 buttonBindings = ['B4','B6','H01','H0-1','H-10','H10',
                                   'B5','B7','B0','B2','B3','B1',
                                   'B8','B9','B10','B11',
                                   'A0-','A0+','A1-','A1+',
                                   'A3-','A3+','A4+','A4-'],
                 axisThresh = {'A0-':-0.3,'A0+':0.3,'A1-':-0.3,'A1+':0.3,
                               'A3-':-0.3,'A3+':0.3,'A4-':-0.3,'A4+':0.3}):        
        '''
         This function updates the status using the joypad event dictionary which 
         runs the getNewStatus function.
         Also this function logs the button press.
                  B6                                   B7
                  B4                                   B5
               _=====_                               _=====_
              / _____ \                             / _____ \
            +.-'_____'-.---------------------------.-'_____'-.+
           /   |     |  '.                       .'  |     |   \
          / ___| H2+ |___ \                     / ___| B0  |___ \
         / |             | ;  __           _   ; |             | ;
         | | H1-      H1+|   |__|B8     B9|_:> | | B3       B1 | |
         | |___       ___| ;SELECT       START ; |___       ___| ;
         |\    | H2- |    /  _     ___      _   \    | B2  |    /|
         | \   |_____|  .','" "', |___|  ,'" "', '.  |_____|  .' |
         |  '-.______.-' /  A1-  \ANALOG/  A4-  \  '-._____.-'   |
         |               |A0- A0+|------|A3- A3+|                |
         |              /\  A1+  /      \  A4+  /\               |
         |             /  '.___.'        '.___.'  \              |
         |            /     B10            B11     \             |
          \          /                              \           /
           \________/                                \_________/
                             PS2 CONTROLLER
        '''
        self.animals         = animals
        self.movie           = movie
        self.keyBindings     = keyBindings
        self.buttonBindings  = buttonBindings
        self.axisThresh      = axisThresh
        #                    0                   1                           2                       3
        #    variables= [self.animals,self.animal1.behav1.status,self.animal1.behav2.status,self.animal1.behav3.status,
        #                    4                   5                           6                       7
        #                self.animal2,self.animal2.behav1.status,self.animal2.behav2.status,self.animal2.behav3.status,
        #                    8        9          10        11
        #                mediafps,runMov,movBackWards,self.movie];
            
        #                       0         1         2         3             4
        #   variables= [self.animals, mediafps, runMov, movBackWards, self.movie];
                    
        self.padSwitch = {buttonBindings[0]  :lambda y: self.behavButtonReac(0,0,y),
                          buttonBindings[1]  :lambda y: self.behavButtonReac(0,1,y),
                          buttonBindings[2]  :lambda y: self.behavButtonReac(0,2,y),
                          buttonBindings[3]  :lambda y: self.behavButtonReac(0,3,y),
                          buttonBindings[4]  :lambda y: self.behavButtonReac(0,4,y),
                          buttonBindings[5]  :lambda y: self.behavButtonReac(0,5,y),
                          buttonBindings[6]  :lambda y: self.behavButtonReac(1,0,y),
                          buttonBindings[7]  :lambda y: self.behavButtonReac(1,1,y),
                          buttonBindings[8]  :lambda y: self.behavButtonReac(1,2,y),
                          buttonBindings[9]  :lambda y: self.behavButtonReac(1,3,y),
                          buttonBindings[10] :lambda y: self.behavButtonReac(1,4,y),
                          buttonBindings[11] :lambda y: self.behavButtonReac(1,5,y),
                          buttonBindings[12] :lambda y: self.deleteBehav(0,y),
                          buttonBindings[13] :lambda y: self.deleteBehav(1,y),
                          buttonBindings[14] :lambda y: self.toggleRunMov(y[2],y), # returnsValue
                          buttonBindings[15] :lambda y: self.stopToggle(y[2],y),# returnsValue
                          buttonBindings[16] :lambda y: self.runMovReverse(y[3],y),# returnsValue
                          buttonBindings[17] :lambda y: self.runMovForward(y[3],y),# returnsValue
                          buttonBindings[18] :lambda y: self.changeFPS(y[1],1,y),# returnsValue
                          buttonBindings[19] :lambda y: self.changeFPS(y[1],-1,y),
                          buttonBindings[20] :lambda y: self.changeFrameNo(-1,y),
                          buttonBindings[21] :lambda y: self.changeFrameNo(1,y),
                          buttonBindings[22] :lambda y: self.changeFrameNo(-10,y),
                          buttonBindings[23] :lambda y: self.changeFrameNo(10,y)}
                          
        self.keySwitch ={keyBindings[0]  :lambda y: self.behavButtonReac(0,0,y),
                          keyBindings[1]  :lambda y: self.behavButtonReac(0,1,y),
                          keyBindings[2]  :lambda y: self.behavButtonReac(0,2,y),
                          keyBindings[3]  :lambda y: self.behavButtonReac(0,3,y),
                          keyBindings[4]  :lambda y: self.behavButtonReac(0,4,y),
                          keyBindings[5]  :lambda y: self.behavButtonReac(0,5,y),
                          keyBindings[6]  :lambda y: self.behavButtonReac(1,0,y),
                          keyBindings[7]  :lambda y: self.behavButtonReac(1,1,y),
                          keyBindings[8]  :lambda y: self.behavButtonReac(1,2,y),
                          keyBindings[9]  :lambda y: self.behavButtonReac(1,3,y),
                          keyBindings[10] :lambda y: self.behavButtonReac(1,4,y),
                          keyBindings[11] :lambda y: self.behavButtonReac(1,5,y),
                          keyBindings[12] :lambda y: self.deleteBehav(0,y),
                          keyBindings[13] :lambda y: self.deleteBehav(1,y),
                          keyBindings[14] :lambda y: self.toggleRunMov(y[2],y), # returnsValue
                          keyBindings[15] :lambda y: self.stopToggle(y[2],y),# returnsValue
                          keyBindings[16] :lambda y: self.toggleMovieDir(y[3],y),# returnsValue
                          keyBindings[17] :lambda y: self.changeFPS(y[1],1,y),# returnsValue
                          keyBindings[18] :lambda y: self.changeFPS(y[1],-1,y),# returnsValue
                          keyBindings[19] :lambda y: self.changeFrameNo(-1,y),# returnsValue
                          keyBindings[20] :lambda y: self.changeFrameNo(1,y),
                          keyBindings[21] :lambda y: self.changeFrameNo(-10,y),
                          keyBindings[22] :lambda y: self.changeFrameNo(10,y)}
                          

    def setStandardKeyB(self,keyBindings = [113,119,97,115,120,121,111,112,107,108,109,44,
                                                116,117,32,13,8,50,49,276,275,274,273]):
        self.keyBindings  = keyBindings                          
        self.keySwitch ={keyBindings[0]  :lambda y: self.behavButtonReac(0,0,y),
                          keyBindings[1]  :lambda y: self.behavButtonReac(0,1,y),
                          keyBindings[2]  :lambda y: self.behavButtonReac(0,2,y),
                          keyBindings[3]  :lambda y: self.behavButtonReac(0,3,y),
                          keyBindings[4]  :lambda y: self.behavButtonReac(0,4,y),
                          keyBindings[5]  :lambda y: self.behavButtonReac(0,5,y),
                          keyBindings[6]  :lambda y: self.behavButtonReac(1,0,y),
                          keyBindings[7]  :lambda y: self.behavButtonReac(1,1,y),
                          keyBindings[8]  :lambda y: self.behavButtonReac(1,2,y),
                          keyBindings[9]  :lambda y: self.behavButtonReac(1,3,y),
                          keyBindings[10] :lambda y: self.behavButtonReac(1,4,y),
                          keyBindings[11] :lambda y: self.behavButtonReac(1,5,y),
                          keyBindings[12] :lambda y: self.deleteBehav(0,y),
                          keyBindings[13] :lambda y: self.deleteBehav(1,y),
                          keyBindings[14] :lambda y: self.toggleRunMov(y[2],y), # returnsValue
                          keyBindings[15] :lambda y: self.stopToggle(y[2],y),# returnsValue
                          keyBindings[16] :lambda y: self.toggleMovieDir(y[3],y),# returnsValue
                          keyBindings[17] :lambda y: self.changeFPS(y[1],1,y),# returnsValue
                          keyBindings[18] :lambda y: self.changeFPS(y[1],-1,y),# returnsValue
                          keyBindings[19] :lambda y: self.changeFrameNo(-1,y),# returnsValue
                          keyBindings[20] :lambda y: self.changeFrameNo(1,y),
                          keyBindings[21] :lambda y: self.changeFrameNo(-10,y),
                          keyBindings[22] :lambda y: self.changeFrameNo(10,y)}
        
    def setStandardPS2(self, buttonBindings  = ['B4','B6','H01','H0-1','H-10','H10',
                                               'B5','B7','B0','B2','B3','B1',
                                               'B8','B9','B10','B11',
                                               'A0-','A0+','A1-','A1+',
                                               'A3-','A3+','A4+','A4-'],
                             axisThresh = {'A0-':-0.3,'A0+':0.3,'A1-':-0.3,'A1+':0.3,
                                           'A3-':-0.3,'A3+':0.3,'A4-':-0.3,'A4+':0.3}):
        '''
        
                  B6                                   B7
                  B4                                   B5
               _=====_                               _=====_
              / _____ \                             / _____ \
            +.-'_____'-.---------------------------.-'_____'-.+
           /   |     |  '.                       .'  |     |   \
          / ___| H2+ |___ \                     / ___| B0  |___ \
         / |             | ;  __           _   ; |             | ;
         | | H1-      H1+|   |__|B8     B9|_:> | | B3       B1 | |
         | |___       ___| ;SELECT       START ; |___       ___| ;
         |\    | H2- |    /  _     ___      _   \    | B2  |    /|
         | \   |_____|  .','" "', |___|  ,'" "', '.  |_____|  .' |
         |  '-.______.-' /  A1-  \ANALOG/  A4-  \  '-._____.-'   |
         |               |A0- A0+|------|A3- A3+|                |
         |              /\  A1+  /      \  A4+  /\               |
         |             /  '.___.'        '.___.'  \              |
         |            /     B10            B11     \             |
          \          /                              \           /
           \________/                                \_________/
                             PS2 CONTROLLER
        '''
                           
        self.buttonBindings = buttonBindings
        self.axisThresh      = axisThresh
        
                    
        
        self.padSwitch = {buttonBindings[0]  :lambda y: self.behavButtonReac(0,0,y),
                          buttonBindings[1]  :lambda y: self.behavButtonReac(0,1,y),
                          buttonBindings[2]  :lambda y: self.behavButtonReac(0,2,y),
                          buttonBindings[3]  :lambda y: self.behavButtonReac(0,3,y),
                          buttonBindings[4]  :lambda y: self.behavButtonReac(0,4,y),
                          buttonBindings[5]  :lambda y: self.behavButtonReac(0,5,y),
                          buttonBindings[6]  :lambda y: self.behavButtonReac(1,0,y),
                          buttonBindings[7]  :lambda y: self.behavButtonReac(1,1,y),
                          buttonBindings[8]  :lambda y: self.behavButtonReac(1,2,y),
                          buttonBindings[9]  :lambda y: self.behavButtonReac(1,3,y),
                          buttonBindings[10] :lambda y: self.behavButtonReac(1,4,y),
                          buttonBindings[11] :lambda y: self.behavButtonReac(1,5,y),
                          buttonBindings[12] :lambda y: self.deleteBehav(0,y),
                          buttonBindings[13] :lambda y: self.deleteBehav(1,y),
                          buttonBindings[14] :lambda y: self.toggleRunMov(y[2],y), # returnsValue
                          buttonBindings[15] :lambda y: self.stopToggle(y[2],y),# returnsValue
                          buttonBindings[16] :lambda y: self.runMovReverse(y[3],y),# returnsValue
                          buttonBindings[17] :lambda y: self.runMovForward(y[3],y),# returnsValue
                          buttonBindings[18] :lambda y: self.changeFPS(y[1],1,y),# returnsValue
                          buttonBindings[19] :lambda y: self.changeFPS(y[1],-1,y),
                          buttonBindings[20] :lambda y: self.changeFrameNo(-1,y),
                          buttonBindings[21] :lambda y: self.changeFrameNo(1,y),
                          buttonBindings[22] :lambda y: self.changeFrameNo(-10,y),
                          buttonBindings[23] :lambda y: self.changeFrameNo(10,y)}
                          
    def setStandardXbox(self,buttonBindings  = ['B4','A2+','H01','H0-1','H-10','H10',
                                               'B5','A5+','B3','B0','B2','B1',
                                               'B6','B7','B9','B10',
                                               'A0-','A0+','A1-','A1+',
                                               'A3-','A3+','A4+','A4-',
                                               'B8'],
                                  axisThresh = {'A0-':-0.6,'A0+':0.6,'A1-':-0.6,'A1+':0.6,
                                                'A3-':-0.6,'A3+':0.6,'A4-':-0.6,'A4+':0.6,
                                                'A2-':-2,  'A2+':0.6,'A5-':-2,  'A5+':0.6}):
        """

                       AT2+                                         AT5+
                        B4                                           B5
                  ,,,,---------,_                               _,--------,,,,
                /-----```````---/`'*-,_____________________,-*'`\---``````-----\
               /     A1-                      B8                   ,---,        \
              /   , -===-- ,          B6     ( X )    B7     ,---, '-B3' ,---,   \
             /A0-||'( : )'||A0+     (◄)-|           |-(►)   'B2-' ,---, 'B1-'    \
            /    \\ ,__, //           H01                      A4- '-B0'           \
           /         A1+         ,--'`!`!`'--,              ,--===--,               \
          /  B9              H-10||  ==O==  ||H10       A3-||'( : )'||A3+            \
         /                       '--, !,!, --'             \\  ,__, //                \
        |                          ,--------------------------, A4+     B10            |
        |                      ,-'`  H0-1                     `'-,                     |
        \                   ,-'`                                  `'-,                 /
         `'----- ,,,, -----'`                                       `'----- ,,,, -----'`
        """
        
                           
        self.buttonBindings = buttonBindings
        self.axisThresh      = axisThresh
        
                    
        
        self.padSwitch = {buttonBindings[0]  :lambda y: self.behavButtonReac(0,0,y),
                          buttonBindings[1]  :lambda y: self.behavButtonReac(0,1,y),
                          buttonBindings[2]  :lambda y: self.behavButtonReac(0,2,y),
                          buttonBindings[3]  :lambda y: self.behavButtonReac(0,3,y),
                          buttonBindings[4]  :lambda y: self.behavButtonReac(0,4,y),
                          buttonBindings[5]  :lambda y: self.behavButtonReac(0,5,y),
                          buttonBindings[6]  :lambda y: self.behavButtonReac(1,0,y),
                          buttonBindings[7]  :lambda y: self.behavButtonReac(1,1,y),
                          buttonBindings[8]  :lambda y: self.behavButtonReac(1,2,y),
                          buttonBindings[9]  :lambda y: self.behavButtonReac(1,3,y),
                          buttonBindings[10] :lambda y: self.behavButtonReac(1,4,y),
                          buttonBindings[11] :lambda y: self.behavButtonReac(1,5,y),
                          buttonBindings[12] :lambda y: self.deleteBehav(0,y),
                          buttonBindings[13] :lambda y: self.deleteBehav(1,y),
                          buttonBindings[14] :lambda y: self.toggleRunMov(y[2],y), # returnsValue
                          buttonBindings[15] :lambda y: self.stopToggle(y[2],y),# returnsValue
                          buttonBindings[16] :lambda y: self.runMovReverse(y[3],y),# returnsValue
                          buttonBindings[17] :lambda y: self.runMovForward(y[3],y),# returnsValue
                          buttonBindings[18] :lambda y: self.changeFPS(y[1],1,y),# returnsValue
                          buttonBindings[19] :lambda y: self.changeFPS(y[1],-1,y),
                          buttonBindings[20] :lambda y: self.changeFrameNo(-1,y),
                          buttonBindings[21] :lambda y: self.changeFrameNo(1,y),
                          buttonBindings[22] :lambda y: self.changeFrameNo(-10,y),
                          buttonBindings[23] :lambda y: self.changeFrameNo(10,y)}
                                
        # Movie Navigation Functions #   
    def setFreePad(self,freeBindingList,axisThresh):
        # freeBindingList = list of tupels eaach tupel ('bindingString',animalNum (-1) for movie, behaviour num or string 
        self.axisThresh = axisThresh

        self.padSwitch = dict()
        for i in range(len(freeBindingList)):
            button    = copy.deepcopy(freeBindingList[i][0])
            animal    = copy.deepcopy(freeBindingList[i][1])
            behaviour = copy.deepcopy(freeBindingList[i][2])
            #if the animal is -1 this means its a movie command
            if  freeBindingList[i][1] ==-1:
                if freeBindingList[i][2]   == 'stopToggle':
                    self.padSwitch.update({button : lambda y: self.stopToggle(y[2],y) })
                elif freeBindingList[i][2] == 'changeFrameNoHigh1':
                    self.padSwitch.update({button : lambda y: self.changeFrameNo(1,y) })
                elif freeBindingList[i][2] == 'changeFrameNoLow1':
                    self.padSwitch.update({button : lambda y: self.changeFrameNo(-1,y) })
                elif freeBindingList[i][2] == 'changeFrameNoHigh10':
                    self.padSwitch.update({button : lambda y: self.changeFrameNo(10,y) })
                elif freeBindingList[i][2] == 'changeFrameNoLow10':
                    self.padSwitch.update({button : lambda y: self.changeFrameNo(-10,y) })
                elif freeBindingList[i][2] == 'runMovReverse':
                    self.padSwitch.update({ button : lambda y: self.runMovReverse(y[3],y) })
                elif freeBindingList[i][2] == 'runMovForward':
                    self.padSwitch.update({button : lambda y: self.runMovForward(y[3],y) })
                elif freeBindingList[i][2] == 'changeFPShigh':
                    self.padSwitch.update({button : lambda y: self.changeFPS(y[1],1,y) })
                elif freeBindingList[i][2] == 'changeFPSlow':
                    self.padSwitch.update({button : lambda y: self.changeFPS(y[1],-1,y) })
                elif freeBindingList[i][2] == 'toggleRunMov':
                    self.padSwitch.update({button : lambda y: self.toggleRunMov(y[2],y) })
                    
            else:
                # If the behaviour is 'delete' use special function other wise use behavreac
                if  freeBindingList[i][2]== 'delete':
                    # not sure if second lambda is needed
                    self.padSwitch.update({button : (lambda animal: lambda y: self.deleteBehav(animal,y))(animal)})
                else:        
                    self.padSwitch.update({button : (lambda animal,behaviour: lambda y: self.behavButtonReac(animal,behaviour,y))(animal,behaviour)})
        
        self.buttonBindings=self.padSwitch.keys()
        #print self.buttonBindings
    def toggleRunMov(self,runMov,vAll):
        vAll[2] = not runMov
        return vAll
        
    def runMovReverse(self,runMov,vAll):
        vAll[3] = True
        return vAll
        
    def runMovForward(self,runMov,vAll):
        vAll[3] = False
        return vAll
        
    def seek(self,runMov,vAll):
        vAll[2] = False
        vAll[4].frameNo = vAll[11].length
        return vAll
        
    def stopToggle(self,runMov,vAll):
        if (runMov == True):
            vAll[2] = False
        else:
            #now we stop the behavioural input
            for i in range(len(vAll[0])):
                for j in range(len(vAll[0][i].behaviours)):
                   vAll[0][i].behaviours[j].setBehaviour(vAll[0][i].behaviours[j].status,self.movie.get_frameNo())
        
            vAll[4].frameNo = 0
        return vAll
        
    def toggleMovieDir(self,movBackWards,vAll):
        vAll[3] = not movBackWards
        return vAll
        
        #Behaviour Recall Functions #
    def behavButtonReac(self,animalID,behaviourID,vAll):
        #shorthand
        #print 'user_input_control.behavButtonReac behavStr', 'Behav'+str(behaviourID), animalID, behaviourID
        vAll[0][animalID].setBehaviour('Behav'+str(behaviourID),self.movie.get_frameNo(),behaviourID)


        return vAll    
             
    def deleteBehav(self,animalID,vAll): 
        #shorthand
        #for i in range(len(vAll[0][animalID].behaviours)):
        vAll[0][animalID].setBehaviour('Del0',self.movie.get_frameNo(),0) 
        return vAll          
              
    def changeFrameNo(self,step,vAll):
        frameNo = self.movie.get_frameNo()+step
        if frameNo>self.movie.length:
            frameNo = self.movie.length
        elif frameNo <0:
            frameNo = 0
        self.movie.frameNo =frameNo
        vAll[2] = False
        return vAll       
             
    def changeFPS(self,mediafps,step,vAll):
        mediafps = mediafps+step
        if (mediafps >100):
            mediafps = 100
        elif (mediafps < 1):
            mediafps =1
        vAll[1] = mediafps
        return vAll      
             
    def checkPad(self,event,mediafps,runMov,movBackWards,inputCode):
        vAll= [self.animals,mediafps,runMov,movBackWards,self.movie]
        #print 'user_input_control.checkPad',inputCode, self.movie.get_frameNo()
        try:
            vAll = self.padSwitch[inputCode](vAll)
        except KeyError:
            print('user_input_control.checkPad: This key was not assigned: ',inputCode)
        
                
        #print 'user_input_control.checkPad inputcode fps movieRunning backwards',inputCode, vAll[1],vAll[2],vAll[3], self.movie.get_frameNo()
        return vAll[1],vAll[2],vAll[3] 
        
    def checkKeys(self,event,mediafps,runMov,movBackWards):
        vAll= [self.animals,mediafps,runMov,movBackWards,self.movie];

        key = event.key
        try:
            vAll = self.keySwitch[key](vAll)
        except KeyError:
            print('This key was not assigned: ',key)
        
                
        return vAll[1],vAll[2],vAll[3] 
