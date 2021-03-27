# -*- coding: utf-8 -*-
"""
Created on Tue May 31 16:24:06 2016

@author: bgeurten
"""

import pygame


class DisjunctBehaviour:

    def __init__(self, ethogram, status=0, label='behaviour A', lastChange=0,
                 color=0, icon=0, icon_path=0, iconSize=0):
        self.status = status
        self.lastChange = lastChange
        self.label = label
        self.ethogram = ethogram
        self.color = color
        self.icon = icon
        self.iconT = icon
        self.icon_path = icon_path
        self.iconSize = iconSize

    def setIcon(self, icon, modus):
        if modus == 'simple':
            self.icon = icon
        elif modus == 'fileName':
            self.icon = pygame.image.load(icon)

        elif modus == 'compose':
            # Create a a transparent surface in icon size
            newIm = pygame.Surface([self.iconSize, self.iconSize], pygame.SRCALPHA, 32)
            newIm = newIm.convert_alpha()
            # draw circler
            r = self.iconSize / 2.0
            pygame.circle(newIm, self.color, (r, r), r, width=0)
            # get decall from file
            decall = pygame.image.load(icon)
            # combine both
            self.icon = newIm.blit(decall, (0, 0))

        self.iconT = self.icon.copy()
        self.iconT.set_alpha(50)
        self.iconT = pygame.transform.scale(self.iconT,
                                            (int(self.iconT.get_height() / 2), int(self.iconT.get_height() / 2)))

    def assignValue(self, frameA, frameB, value):
        # This is neede because the movie can run backwards
        if (frameA > frameB):
            self.ethogram[frameB:frameA] = value
        elif (frameA < frameB):
            self.ethogram[frameA:frameB] = value

    def setBehaviour(self, newB, frameNo):

        # print ' behaviour: ' , self.label ,' | status: ', self.status, ' | newB: '

        # check if behaviour and frameNo are within limits        
        if ((newB in [-1, 0, 1]) and (frameNo < self.ethogram.shape[0]) and (frameNo > -1)):

            # if the new Behaviour is not idle but the status was idle   
            if (self.status == 0):
                # do not set anything to idle this is done by deleteing (-1)
                # start new behaviour
                # just start the new behaviour
                if (newB == -1):
                    self.ethogram[frameNo] = 0
                    self.status = -1
                    self.lastChange = frameNo
                elif (newB == 1):
                    self.ethogram[frameNo] = 1
                    self.status = 1
                    self.lastChange = frameNo
                # if the newB behaviour is zero and the status was zero there is nothing to do



            # if the new behaviour is not idle and the status is not 0:
            elif (self.status != 0):

                # the old behaviour has to end first
                if (self.status == -1):
                    # end deleting
                    self.assignValue(self.lastChange, frameNo, 0)
                else:
                    # end active behaviour
                    self.assignValue(self.lastChange, frameNo, self.status)

                # start new behaviour
                self.lastChange = frameNo
                if (newB == -1):
                    self.ethogram[frameNo] = 0
                else:
                    self.ethogram[frameNo] = newB

                # set new status
                if (newB == self.status):
                    self.status = 0
                else:
                    self.status = newB
        else:
            print('Either the behaviour is unknown or the frame number is not within bounds')
