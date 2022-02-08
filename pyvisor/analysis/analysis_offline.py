import pickle, os
import numpy as np
import scipy as sp
import scipy.io as sio 
import scipy.stats
import matplotlib.pyplot as plt
import analysis_online as anaOn
from tqdm import tqdm

class analysisOffLine:
    def __init__(self,filePos,fileType = 'pkl',behavTags = list(),fps=25,behavNum=10):
        self.filePos      = filePos
        self.origBehavNum = behavNum
        self.fileType     = fileType
        self.fps          = fps
        self.dataList     = list()
        self.behavTags    = behavTags
        if type(self.filePos) == str:
            self.fileNum = 1
        elif type(self.filePos) == list:
            self.fileNum = len(self.filePos)
        else:
            print 'Unknown filetype ' + self.fileType
    
    def readData(self):
        if self.fileNum == 1:
            self.dataList = list()
            self.dataList.append(self.readDataSingle(str(self.filePos)))
        else:
            self.dataList = list()
            for fileNameI in tqdm(xrange(0,len(self.filePos))):
                self.dataList.append(self.readDataSingle(self.filePos[fileNameI]))

    def readDataSingle(self,filePos):
        if self.fileType == 'pkl':
            filehandler = open(str(filePos),"rb")
            data = pickle.load(filehandler)
            filehandler.close()
            return data
        elif self.fileType == 'txt':
            with open(filePos) as f:
                data = np.empty((0,self.origBehavNum), int)
                for line in f:
                    if line[0] =='0' or line[0] =='1' or line[0] ==' ':
                        temp = line.split()
                        temp = np.array([int(i) for i in temp])
                        temp.shape=(1,self.origBehavNum)
                        data =  np.append(data, temp, axis=0)
            return data    
            
        else:
            print 'Unknown filetype ' + self.fileType
    
    def saveDataSingle(self,data,fPos,sType):

        if sType == "pkl":
            self.saveDataSinglePkl(data,fPos)
        elif sType == "mat":
            self.saveDataSingleMat(data,fPos)
        elif sType == "xlsx":
            self.saveDataSingleXlsx(data,fPos)
        elif sType == "txt":
            self.saveDataSingleTxt(data,fPos)
        else:
            print "Error in pyMovScore analysis_offline.py unknown save type in self.saveDataSingle"

    def saveDataSingleMat(self,data,fPos):  
        sio.savemat(fPos, data)
    
    def saveDataSinglePkl(self,data,fPos):
        with open(fPos, 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def saveDataSingleXlsx(self,data,fPos):
        pass

    def saveDataSingleTxt(self,data,fPos):
        pass

    def saveDataMultiple(self,dPos):
        for i in range(self.fileNum):
            fName = os.path.splitext(os.path.basename(self.filePos[i]))
            sPos = dPos+fName[0]+'.mat'
            self.saveDataSingle(self.resultList[i],sPos,'mat')
        
    def compressResultList(self, all_keys):
        compressList = dict()
        for k in all_keys:            
            newMat = True
            for data in self.resultList:
                if data.has_key(k) == True:
                    temp = data[k]
                    if type(temp) == list:
                        temp = np.hstack(temp)
                    if type(newMat) == bool:
                        newMat = temp
                    else:
                        newAx = len(temp.shape)
                        print newMat.shape,temp.shape,newAx
                        newMat = np.stack((newMat,temp),axis = newAx)
                        print ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
            compressList.update({k:newMat})

    def subtractBehav(self,behav,modIDX):
        '''
        
        '''
        
        # go through all data sets
        for i in range(len(self.dataList)):
            #shorthands
            data = self.dataList[i]
            # go through all behaviours that need to be modified
            for mod in modIDX:
                #calculate all correct trials
                data[:,behav] = np.subtract(data[:,behav],data[:,mod]) 
            # avod neg. values
            data =data.clip(min=0)

            #return data to list of datasets
            self.dataList[i] = data
                            
    def computeNegativeModulator(self,behIDX,modIDX):
        '''
        This function calculates a negative modulator for a behaviour. As for example column
        X includes correct and incorrect attempts of behaviour. The user defined furthermore 
        an modulator in column Y which is set to 1 for incorrect attempts. Then this function
        stacks the following two columns to the data set (X*Y) and X-(X*Y), so that the resulting
        two column included first all incorrect attempts and secondly all correct attempts.

        Columns you which to process according to the modulator should be listed in the first 
        variable as a list of indices (behIDX), the column index of the modulator should be 
        given as the second variable(modIDX) 
        '''
        
        # sort the behaviour ascending
        behIDX.sort()
        # go through all data sets
        for i in range(len(self.dataList)):
            #shorthands
            data = self.dataList[i]
            modulator = data[:,modIDX]
            # go through all behaviours that need to be modified
            for behav in behIDX:
                # calculate all incorrect trials
                temp  = np.multiply(data[:,behav],modulator)
                #calculate all correct trials
                temp2 = np.subtract(data[:,behav],temp) 
                #add both trial-lists to the data set
                data  = np.column_stack((data,temp))
                data  = np.column_stack((data,temp2))
            #return data to list of datasets
            self.dataList[i] = data

    def computeExclusiveModulator(self,behIDX,modIDX):
        '''
        This function calculates a new category index from the coincidence of at least two
        other indices. Example: category A is set to one if animal takes in food category B 
        is set to one if animal is in nest. Then this function creates a new category C 
        food consumption in nest and deletes occurences of C from A and B 

        The first category is called from behIDX, all other coinciding categories are placed
        in modIDX.

        '''
        # go through all data sets
        for i in range(len(self.dataList)):
            #shorthands
            data = self.dataList[i]
            newCat = data[:,behIDX]
            #make new category
            for mod in modIDX:
                # modifier
                tempM = data[:,mod]
                # multiply modulators
                newCat = np.multiply(newCat,tempM)
            #now delete new category from all parent categories
            modIDX.append(behIDX)
            for mod in modIDX:
                # modifier
                tempM = data[:,mod]
                # subtract new category occurence
                tempM = np.subtract(tempM,newCat)
                # negative values have to be set to zero 
                tempM = tempM.clip(min=0)
                # return value
                data[:,mod] = tempM
            #add new behaviour to data
            data  = np.column_stack((data,newCat))
            #return data to list of datasets
            self.dataList[i] = data

    def computeInclusiveModulator(self,behIDX,modIDX):
        '''
        This function subtracts all inclusive categories from a parent category. Meaning if one category
        is food and another is apples. All entries from food that are apples will be deleted. The
        apple free category is then added to the data set as a new column.

        The parent category index is defined in behIDX, where as the modulators are defined in modIDX as  
        an list of indices.

        '''
        # go through all data sets
        for i in range(len(self.dataList)):
            #shorthands
            data = self.dataList[i]
            temp = data[:,behIDX]
            for mod in modIDX:
                # modifier
                tempM = data[:,mod]
                #subtract inclusive modulators
                temp = np.subtract(temp,tempM)
            # negative values have to be set to zero 
            temp = temp.clip(min=0)
            #add new behaviour to data
            data  = np.column_stack((data,temp))
            #return data to list of datasets
            self.dataList[i] = data

    def setAnalysisWindow(self,start=750,end=8248):
        '''
        This function returns a subset frames, defined by the user in the input variables 
        start and end. 
        '''
        subset = list()
        # go through all data sets
        for dataI in tqdm(xrange(0,len(self.dataList))):
            data = self.dataList[dataI]
            # set analysis window
            if type(start) == int:
                data = data[start:end,:]
                subset.append(data)
            elif type(start) == list:
                data = data[start[dataI]:end[dataI],:]
                subset.append(data)
            else:
                print '!Error start and end in analysisOffline.setAnalysis window are neither an int nor a list type!'

             # return data to list of datasets
        return subset
    
    def createAnaOnObj(self,data):
        '''
        This function creates an analysis online object so that we can use its analysis routines.
        The only input variable to be set has to be the dataset currently used. 
        '''
        self.anaOnObj = anaOn.analysis(self,self.fps)       
        self.anaOnObj.ethograms  = data
        self.anaOnObj.behaviours = self.behavTags
    
    def runAnaOnAnalysis(self):
        '''
        This function employs the analysis_online library routines: anaBoutDur, anaFrequency and 
        anaPercentage
        '''
        self.anaOnObj.anaBoutDur()
        self.anaOnObj.anaFrequency()
        self.anaOnObj.anaPercentage()

    def retrieveAnaOnResults(self):
        '''
        This function returns a dictionary with all results of the analysis_online routines
        '''
        anaOnRes = dict()
        anaOnRes['perc']        = self.anaOnObj.perc        
        anaOnRes['boutDur']     = self.anaOnObj.boutDur     
        anaOnRes['boutDurMean'] = self.anaOnObj.boutDurMean 
        anaOnRes['frequency']   = self.anaOnObj.frequency   
        return anaOnRes

    def runAnalysis(self,transitionBehIDX):
        self.resultList = list()
        # go through all data sets
        for dataI in tqdm(xrange(0,len(self.dataList))):
            data = self.dataList[dataI]
            # create analysis online object
            self.createAnaOnObj(data)
            # run analysis online routines
            self.runAnaOnAnalysis()
            # get describitive results
            results  = self.retrieveAnaOnResults()
            #analyse transitions
            transRes = self.calculateTransProbs(data,transitionBehIDX)
            if transRes.has_key('paralellIDX'):
                print ':::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::'
                print self.filePos[dataI]
                for i in transRes['paralellIDX']:
                    print i, transRes['paralellData'][i,:],data[i]
                print ':::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::'
            #add transition analysis
            results.update(transRes)
            # save results into resultList
            self.resultList.append(results)

    def calculateTransProbs(self,data,behavIDX):
        # calculate sequence IDX
        seqIDX   = self.calculateSequenceIDX(data,behavIDX)
        if seqIDX[0] == False:
            transitions = dict()
            transitions['paralellIDX'] = seqIDX[2]
            transitions['paralellData']  = seqIDX[1]
            return transitions
        else:
            seqIDX = seqIDX[1]
            #reduce it
            temp     = self.reduceSequenceIDX(seqIDX)
            seqIDXR  = temp[0]
            stayProb = temp[1]
            #number of behaviours involved
            behavNum = len(behavIDX)
            # return variable preallocation
            transMat = np.zeros((behavNum+1,behavNum+1))
            # find all starting behaviour
            for startB in range(behavNum+1):
                # get all positions of starting behaviour in the reduced seqIDX
                startBidx = np.nonzero(seqIDXR[:-1] == startB)
                # now go exactly one step further to get the targetIndices
                targetBidx= startBidx[0]+1
                # get all target behaviours
                targetBArr = list(seqIDXR[targetBidx])
                for targetB in range(behavNum):
                    # get how often the starting behaviour ended in a particular target behaviour
                    transMat[startB,targetB]= targetBArr.count(targetB)
                
                #calculate staying probability

                #transMat[startB,startB] =  np.sum(stayProb[startBidx])
            # return tansistion probability matrix
            transitions = dict()
            transitions['seqIDX']   = seqIDX
            transitions['seqIDXR']  = seqIDXR
            transitions['stayProb'] = stayProb
            transitions['transMat'] = transMat
            return transitions
            
    def reduceSequenceIDX(self,seqIDX):
        
        
        # make difference  of the behaviour succession
        staying     = np.diff(seqIDX)
        # all non zero values indicate a change
        changeIndex = np.nonzero(staying != 0)
        # but the difference vector is one vector shorter than the original
        changeIndex =  changeIndex[0]+1
        # the first value has to be to the changes
        changeIndex = np.insert(changeIndex,0,0)
        # calculate staying time
        stayingDur = np.diff(changeIndex)
        stayingDur = np.append(stayingDur,len(seqIDX)-changeIndex[-1])
        #return tupel of sequencechanges and the corresponding staying duration
        return (seqIDX[changeIndex],stayingDur)
   
    def calculateSequenceIDX(self,data,behavIDX):
        '''
        This function generates a vector in which the sucsession of behaviours is denoted.
        If you input the behavioural indices of those behaviours used for the sucsession, be 
        aware that the sorting of those indices defines there new tags in the sucsession:
        
        EG: self.calculateSequenceIDX([7, 3, 2, 4, 5]) 
           becomes:                    1, 2, 3, 4, 5
           and hence the sucsession might look like this 0,0,,0,0,0,2,2,2,2,...,4,4,0,0,0

        Zeros mark the abscence of any of the chosen behaviours

        '''
        data = data[:,behavIDX]
        paralellB = np.sum(data,axis=1)
        if np.max(paralellB) > 1:
            paralellIndex = np.nonzero(paralellB > 1)
            return (False,data,paralellIndex)
        else:
            colTags = np.array(xrange(1,data.shape[1]+1))
            dataTag = data*colTags
            dataTag = np.sum(dataTag,axis=1)
            return (True,dataTag)
    
            

        