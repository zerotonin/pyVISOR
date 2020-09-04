# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 09:11:10 2016

@author: bgeurten
"""
import numpy as np
import scipy as sp
import scipy.stats
import matplotlib.pyplot as plt

class analysis():
    def __init__(self,parent,fps=25):
        self.perc        = []
        self.percAll     = []
        self.boutDur     = []
        self.boutDurMean = []
        self.frequency   = []
        self.sequenceIDX = []
        self.fps         = fps
        self.parent      = parent
    
    def getFPS(self):
        self.fps = self.parent.mediafps
        
    def getDataFromScorer(self):
        '''
        This function reads in the animals structure from the Manual Ethology 
        Scorer. 
        @params animals structure a list of animalEthogram objects
        '''
        self.ethograms  = self.parent.get_data()
        self.behaviours = self.parent.get_labels()
            
    def runAnalysis(self):
        '''
        This is the main standard analysis routine
        '''
        self.getDataFromScorer()
        self.getFPS()
        self.anaBoutDur()
        self.anaFrequency()
        self.anaPercentage()
        
    
    def anaPercentage(self):
        '''
        This analysis how much % of the time a certain behaviour was exhibited
        and saves as self.percAll for each animal and the mean +/- confidence 
        interval as self.perc
        '''
        self.perc = self.ethograms.sum(0)
        n         = float(self.ethograms.shape[0])
        self.perc = self.perc/n 
        self.perc = self.perc*100

            
    def anaBoutDur(self):
        '''
        This function calculates the bout durations
        '''
        self.calcAllSequenceChanges()
        self.boutDur = list()
        self.boutDurMean = list()
        tempMean = list()
        tempList = list()
        for behavI in range(len(self.sequenceIDX)):
            behav = self.sequenceIDX[behavI]
            temp = list()
            if behav == False:
                temp.append([np.nan])
            else:
                temp.append(np.divide(np.subtract(behav[1],behav[0])+1,float(self.fps)))
            tempList.append(temp)
            tempMean.append(np.mean(temp[-1]))


        self.boutDur     = tempList
        self.boutDurMean = tempMean
        
    def anaFrequency(self):
        '''
        This function calculates the percentage of a behaviour in relation to 
        the length of the sequence
        '''
        self.calcAllSequenceChanges()
        self.frequency = list()
        totalDurS = float(self.ethograms.shape[0])/float(self.fps)
        for behav in self.sequenceIDX:     
            if behav== False:
                temp = 0
            else:
                # keep in mind that the memebers of self.sequenceIDX are tupels,
                # but we need the amount of starts
                temp = len(behav[0])/totalDurS
            self.frequency.append(temp)
    
    def mean_confidence_interval(self,data, confidence=0.95):
        '''
        This calculates the mean confidence interval
        '''
        a = 1.0*np.array(data)
        n = len(a)
        m, se = np.mean(a), scipy.stats.sem(a)
        h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
        return m, m-h, m+h
    
    def getSequenceChanges(self,index):
        '''
        This function finds the starts and ends of a behaviour which is needed 
        for a couple of analysis, such as bout duration and frequency  
        '''
        breaks = np.diff(index,axis=0)
        stops  = np.where(breaks == -1)
        starts = np.where(breaks == 1)

        #Special case there are no starts
        if len(starts[0]) == 0 and len(stops[0]) != 0:
            starts = [1]
            stops = stops[0]
            goOn = True

        #Special case there are no stops
        elif len(starts[0]) != 0 and len(stops[0]) == 0:
            stops = [len(index)-1]
            starts = starts[0]
            goOn = True

        #Special case there are no starts and stops
        elif len(starts[0]) == 0 and len(stops[0]) == 0:
            goOn = False

        # Normal stuff happening
        else:
            starts = starts[0]
            stops = stops[0]
            goOn = True
                    
        if goOn == True:
            #because of the diff starts  have to be offset by 1            
            starts =np.add(starts,1)
            # Now test if the first stop is before the first start
            if stops[0] < starts[0]:
              starts = np.insert(starts,0,0)
               
            # Test if the last start is after the the last stop
            if stops[-1] < starts[-1]:
              stops =  np.append(stops,len(index)-1)
            # return tupel of numpy arrays with starts and stops
            return (starts,stops)

        else:
            
            if index[0] == 1:
                # the behaviour is active during the whole sequence
                return ([0],[len(index)])
            else:
                # there is no behaviour so return False
                return False
        
    def calcAllSequenceChanges(self):
        '''
        This function calculates the sequence changes for all behaviours and 
        animals and saves them in self.sequenceIDX
        '''
        self.sequenceIDX = list()
        for i in range(self.ethograms.shape[1]):
            behav = self.ethograms[:,i]
            self.sequenceIDX.append(self.getSequenceChanges(behav))

    ############
    # Plotting #
    ############
    
    def plotPercentage(self,axH,fs=12):
        
        axH.bar(range(len(self.perc)),self.perc)
        #axH.ylabel('percentage',fontsize=fs)
        #axH.xlabel('animals', fontsize=fs)
        
    
    def plotBoutDur(self,axH,fs=12):
        
        #xH.boxplot(self.boutDur, 1)
        axH.bar(range(len(self.boutDurMean)),self.boutDurMean)
        #axH.ylabel('bout dur. [s]',fontsize=fs)
        #axH.xlabel('animals', fontsize=fs)
    
    def plotFrequency(self,axH,fs=12):
        print(range(len(self.frequency)))
        print(self.frequency)
        axH.bar(range(len(self.frequency)),self.frequency)
   #     axH.ylabel('frequency [Hz]',fontsize=fs)
    #    axH.xlabel('animals', fontsize=fs)
        
    
    
        
        
        
