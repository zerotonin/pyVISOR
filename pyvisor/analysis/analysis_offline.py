"""Offline analysis utilities for previously saved ethogram data.

Ported to Python 3.
"""
import pickle
import os
import numpy as np
import scipy.io as sio
from pyvisor.analysis import analysis_online as anaOn


class analysisOffLine:
    def __init__(self, filePos, fileType='pkl', behavTags=None, fps=25, behavNum=10):
        self.filePos = filePos
        self.origBehavNum = behavNum
        self.fileType = fileType
        self.fps = fps
        self.dataList = []
        self.behavTags = behavTags if behavTags is not None else []
        self.resultList = []
        if isinstance(self.filePos, str):
            self.fileNum = 1
        elif isinstance(self.filePos, list):
            self.fileNum = len(self.filePos)
        else:
            print('Unknown filetype ' + self.fileType)

    def readData(self):
        self.dataList = []
        if self.fileNum == 1:
            self.dataList.append(self.readDataSingle(str(self.filePos)))
        else:
            for fileNameI in range(len(self.filePos)):
                self.dataList.append(self.readDataSingle(self.filePos[fileNameI]))

    def readDataSingle(self, filePos):
        if self.fileType == 'pkl':
            with open(str(filePos), "rb") as fh:
                data = pickle.load(fh)
            return data
        elif self.fileType == 'txt':
            with open(filePos) as f:
                data = np.empty((0, self.origBehavNum), int)
                for line in f:
                    if line[0] in ('0', '1', ' '):
                        temp = line.split()
                        temp = np.array([int(i) for i in temp])
                        temp.shape = (1, self.origBehavNum)
                        data = np.append(data, temp, axis=0)
            return data
        else:
            print('Unknown filetype ' + self.fileType)
            return None

    # ---- save helpers ----

    def saveDataSingle(self, data, fPos, sType):
        dispatch = {
            "pkl": self.saveDataSinglePkl,
            "mat": self.saveDataSingleMat,
            "xlsx": self.saveDataSingleXlsx,
            "txt": self.saveDataSingleTxt,
        }
        fn = dispatch.get(sType)
        if fn is None:
            print("Error: unknown save type '{}' in saveDataSingle".format(sType))
            return
        fn(data, fPos)

    def saveDataSingleMat(self, data, fPos):
        sio.savemat(fPos, data)

    def saveDataSinglePkl(self, data, fPos):
        with open(fPos, 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def saveDataSingleXlsx(self, data, fPos):
        pass

    def saveDataSingleTxt(self, data, fPos):
        pass

    def saveDataMultiple(self, dPos):
        for i in range(self.fileNum):
            fName = os.path.splitext(os.path.basename(self.filePos[i]))
            sPos = dPos + fName[0] + '.mat'
            self.saveDataSingle(self.resultList[i], sPos, 'mat')

    # ---- data manipulation ----

    def subtractBehav(self, behav, modIDX):
        for i in range(len(self.dataList)):
            data = self.dataList[i]
            for mod in modIDX:
                data[:, behav] = np.subtract(data[:, behav], data[:, mod])
            data = data.clip(min=0)
            self.dataList[i] = data

    def computeNegativeModulator(self, behIDX, modIDX):
        behIDX.sort()
        for i in range(len(self.dataList)):
            data = self.dataList[i]
            modulator = data[:, modIDX]
            for behav in behIDX:
                temp = np.multiply(data[:, behav], modulator)
                temp2 = np.subtract(data[:, behav], temp)
                data = np.column_stack((data, temp))
                data = np.column_stack((data, temp2))
            self.dataList[i] = data

    def computeExclusiveModulator(self, behIDX, modIDX):
        for i in range(len(self.dataList)):
            data = self.dataList[i]
            newCat = data[:, behIDX]
            for mod in modIDX:
                newCat = np.multiply(newCat, data[:, mod])
            modIDX.append(behIDX)
            for mod in modIDX:
                tempM = np.subtract(data[:, mod], newCat).clip(min=0)
                data[:, mod] = tempM
            data = np.column_stack((data, newCat))
            self.dataList[i] = data

    def computeInclusiveModulator(self, behIDX, modIDX):
        for i in range(len(self.dataList)):
            data = self.dataList[i]
            temp = data[:, behIDX]
            for mod in modIDX:
                temp = np.subtract(temp, data[:, mod])
            temp = temp.clip(min=0)
            data = np.column_stack((data, temp))
            self.dataList[i] = data

    def setAnalysisWindow(self, start=750, end=8248):
        subset = []
        for dataI in range(len(self.dataList)):
            data = self.dataList[dataI]
            if isinstance(start, int):
                subset.append(data[start:end, :])
            elif isinstance(start, list):
                subset.append(data[start[dataI]:end[dataI], :])
            else:
                print('Error: start/end must be int or list')
        return subset

    # ---- analysis wrappers ----

    def createAnaOnObj(self, data):
        self.anaOnObj = anaOn.analysis(self, self.fps)
        self.anaOnObj.ethograms = data
        self.anaOnObj.behaviours = self.behavTags

    def runAnaOnAnalysis(self):
        self.anaOnObj.anaBoutDur()
        self.anaOnObj.anaFrequency()
        self.anaOnObj.anaPercentage()

    def retrieveAnaOnResults(self):
        return {
            'perc': self.anaOnObj.perc,
            'boutDur': self.anaOnObj.boutDur,
            'boutDurMean': self.anaOnObj.boutDurMean,
            'frequency': self.anaOnObj.frequency,
        }

    def runAnalysis(self, transitionBehIDX):
        self.resultList = []
        for dataI in range(len(self.dataList)):
            data = self.dataList[dataI]
            self.createAnaOnObj(data)
            self.runAnaOnAnalysis()
            results = self.retrieveAnaOnResults()
            transRes = self.calculateTransProbs(data, transitionBehIDX)
            if 'paralellIDX' in transRes:
                print('=' * 60)
                print(self.filePos[dataI])
                for idx in transRes['paralellIDX']:
                    print(idx, transRes['paralellData'][idx, :], data[idx])
                print('=' * 60)
            results.update(transRes)
            self.resultList.append(results)

    # ---- transition analysis ----

    def calculateTransProbs(self, data, behavIDX):
        seqIDX = self.calculateSequenceIDX(data, behavIDX)
        if seqIDX[0] is False:
            return {
                'paralellIDX': seqIDX[2],
                'paralellData': seqIDX[1],
            }
        seqIDX = seqIDX[1]
        seqIDXR, stayProb = self.reduceSequenceIDX(seqIDX)
        behavNum = len(behavIDX)
        transMat = np.zeros((behavNum + 1, behavNum + 1))
        for startB in range(behavNum + 1):
            startBidx = np.nonzero(seqIDXR[:-1] == startB)
            targetBidx = startBidx[0] + 1
            targetBArr = list(seqIDXR[targetBidx])
            for targetB in range(behavNum):
                transMat[startB, targetB] = targetBArr.count(targetB)
        return {
            'seqIDX': seqIDX,
            'seqIDXR': seqIDXR,
            'stayProb': stayProb,
            'transMat': transMat,
        }

    def reduceSequenceIDX(self, seqIDX):
        staying = np.diff(seqIDX)
        changeIndex = np.nonzero(staying != 0)[0] + 1
        changeIndex = np.insert(changeIndex, 0, 0)
        stayingDur = np.diff(changeIndex)
        stayingDur = np.append(stayingDur, len(seqIDX) - changeIndex[-1])
        return seqIDX[changeIndex], stayingDur

    def calculateSequenceIDX(self, data, behavIDX):
        data = data[:, behavIDX]
        parallelB = np.sum(data, axis=1)
        if np.max(parallelB) > 1:
            parallelIndex = np.nonzero(parallelB > 1)
            return (False, data, parallelIndex)
        colTags = np.arange(1, data.shape[1] + 1)
        dataTag = np.sum(data * colTags, axis=1)
        return (True, dataTag)
