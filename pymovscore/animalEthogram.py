# -*- coding: utf-8 -*-
"""
Created on Tue May 31 16:54:05 2016

@author: bgeurten
"""

from . import disjunctiveBehaviour as dB
import numpy as np

class animalEthogram():
    def __init__(self,animalName,ethogram,behavLabels,status ,disjunctionList):
        self.behaviours = []
        self.animalName = animalName

        # if the ethogram is a single integer number the system believes the ethogram to be empty and of the length of the number
        if (type(ethogram) == int):
            for i in range(len(behavLabels)):
                obj = dB.disjunctiveBehaviour(np.zeros((ethogram,1),int),status[i],behavLabels[i])
                self.behaviours.append(obj)
                
        # if ethogram is a matrix then old data is loaded and set into the system
        elif(type(ethogram) == np.ndarray):
            pass

        else:
            pass
        # save behaviour labels
        self.behavLabelList = behavLabels
        
        # set disjunctionList
        self.disjunctionList =disjunctionList
        
        #add unique disjunct behaviour goup List
        self.uniqueDJList = self.get_unique_disjunct_list(self.disjunctionList)    
        
        self.Switch = {}
        for i in range(len(behavLabels)):
            self.Switch['Behav' + str(i)]  = self.setLambda(i,1)
            self.Switch['Idle' +  str(i)]  = self.setLambda(i,0)
            self.Switch['Del' +   str(i)]  = self.setLambda(i,-1)
        
        
    def assign_icon_position_to_unique_behaviour(self,iconPosList):
        uniqueDJL = self.uniqueDJList
        uniqueDJL.sort(key = len)
        uniqueDJL = reversed(uniqueDJL)
        for djl in uniqueDJL:
            newPos = iconPosList.pop()            
            for behav in djl:
                self.behaviours[behav].iconPos = newPos
                
                
    def assign_icons(self, iconList,modi):
        for i in range(len(self.behaviours)):
            self.behaviours[i].setIcon(iconList[i],modi[i])
    
    def set_behaviour(self, newB,frameNo,behavI):
        # get the number of disjunctive behaviours to the active behaviour
        #print self.disjunctionList
        numberOfDisjunctions = len(self.disjunctionList[behavI])
        # there are no disjunctive behaviours
        if (numberOfDisjunctions==1):
            #set active behaviour
            self.Switch[newB](frameNo)
        #there are disjunctive behaviours
        else:
            #check what kind of behaviour this is
            # Deletion
            #print self.disjunctionList[behavI]
            if (newB[0] =='D'):
                for j in self.disjunctionList[behavI]:
                    self.Switch['Del' +str(j)](frameNo)
            #Behaviour
            elif (newB[0] =='B'):
                #set disjunctive behaviour
                if (self.behaviours[behavI].status ==1):
                    for j in self.disjunctionList[behavI]:
                        if (j != behavI):
                            self.Switch['Idle' +str(j)](frameNo)
                else:
                    for j in self.disjunctionList[behavI]:
                        if (j != behavI):
                            self.Switch['Del' +str(j)](frameNo)
                 #set active behaviour       
                self.Switch[newB](frameNo)
            #Idle
            else:
                self.Switch[newB](frameNo)
                
    def reset_ethogram(self,frameLen):
        for i in range(len(self.behaviours)):           
            self.behaviours[i].ethogram =  np.zeros((frameLen,1),int)
            
    def get_ethogram(self):
        if (len(self.behaviours) == 1):
            return self.behaviours[0].ethogram
        else:
            temp = self.behaviours[0].ethogram
            for i in range(1,len(self.behaviours)):
                temp = np.hstack((temp,self.behaviours[i].ethogram))
            
        return temp
            
    def setLambda(self,iterator, behaviour):
            return lambda y: self.behaviours[iterator].setBehaviour(behaviour,y)
    
    def get_unique_disjunct_list(self,disjuncList):
        output = []
        seen = list()
        for item in disjuncList:
            if not item in seen:
                output.append(item)
                seen.append(item)
        return output
        
    
