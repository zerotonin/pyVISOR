# -*- coding: utf-8 -*-
"""
Created on Tue May 31 16:54:05 2016

@author: bgeurten, ilyas
"""
from typing import List

import numpy as np

from .disjunct_behaviour import DisjunctBehaviour
from .GUI.model.animal import Animal


class AnimalEthogram:

    def __init__(self, animal: Animal, ethogram_length: int):
        self.animal = animal

        self.disjunct_behaviours = []  # type: List[DisjunctBehaviour]
        '''
        if isinstance(ethogram_length , int):
            
        '''
        for behav_label in self.animal.behaviours:
            db = DisjunctBehaviour(np.zeros((ethogram_length, 1), int),
                                   label=behav_label)
            self.disjunct_behaviours.append(db)

        '''
        This was simply a set of the disjunction list, i.e. a list of unique items
        in the disjunction list.
        self.uniqueDJList = self.getUniqueDJList(self.disjunctionList)
        '''

        self.Switch = {}
        for i in range(len(self.disjunct_behaviours)):
            self.Switch['Behav' + str(i)] = self.setLambda(i, 1)
            self.Switch['Idle' + str(i)] = self.setLambda(i, 0)
            self.Switch['Del' + str(i)] = self.setLambda(i, -1)

    def assignIconPos2UniqueDJB(self, iconPosList):
        uniqueDJL = self.uniqueDJList
        uniqueDJL.sort(key=len)
        uniqueDJL = reversed(uniqueDJL)
        for djl in uniqueDJL:
            newPos = iconPosList.pop()
            for behav in djl:
                self.behaviours[behav].icon_path = newPos

    def assignIcons(self, iconList, modi):
        for i in range(len(self.behaviours)):
            self.behaviours[i].setIcon(iconList[i], modi[i])

    def setBehaviour(self, newB, frameNo, behavI):
        # get the number of disjunctive behaviours to the active behaviour
        # print self.disjunctionList
        numberOfDisjunctions = len(self.disjunctionList[behavI])
        # there are no disjunctive behaviours
        if (numberOfDisjunctions == 1):
            # set active behaviour
            self.Switch[newB](frameNo)
        # there are disjunctive behaviours
        else:
            # check what kind of behaviour this is
            # Deletion
            # print self.disjunctionList[behavI]
            if (newB[0] == 'D'):
                for j in self.disjunctionList[behavI]:
                    self.Switch['Del' + str(j)](frameNo)
            # Behaviour
            elif (newB[0] == 'B'):
                # set disjunctive behaviour
                if (self.behaviours[behavI].status == 1):
                    for j in self.disjunctionList[behavI]:
                        if (j != behavI):
                            self.Switch['Idle' + str(j)](frameNo)
                else:
                    for j in self.disjunctionList[behavI]:
                        if (j != behavI):
                            self.Switch['Del' + str(j)](frameNo)
                # set active behaviour
                self.Switch[newB](frameNo)
            # Idle
            else:
                self.Switch[newB](frameNo)

    def resetEthogram(self, frameLen):
        for i in range(len(self.behaviours)):
            self.behaviours[i].ethogram = np.zeros((frameLen, 1), int)

    def getEthogram(self):
        if len(self.behaviours) == 0:
            return None
        if (len(self.behaviours) == 1):
            return self.behaviours[0].ethogram
        else:
            temp = self.behaviours[0].ethogram
            for i in range(1, len(self.behaviours)):
                temp = np.hstack((temp, self.behaviours[i].ethogram))

        return temp

    def setLambda(self, iterator, behaviour):
        return lambda y: self.disjunct_behaviours[iterator].setBehaviour(behaviour, y)

    @staticmethod
    def getUniqueDJList(disjoint_list):
        output = []
        seen = []
        for item in disjoint_list:
            if item in seen:
                continue
            output.append(item)
            seen.append(item)
        return output
