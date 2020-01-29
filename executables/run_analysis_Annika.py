import pymovscore.analysis.analysis_offline as analysis

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# COL0 : male   : locomotion *
# COL1 : male   : mating *
# COL2 : male   : femaleDirected 
# COL3 : male   : wingExtension 
# COL4 : male   : copAttempt
# COL5 : male   : closeInteraction 
# COL6 : male   : incorrectAction
# COL7 : female : locomotion
# COL8 : female : mating
# COL9: female : rejection
############################
# Added categories *
# COL10: male   : wingExtension incorrect
# COL11: male   : wingExtension correct
# COL12: male   : copAttempt incorrect
# COL13: male   : copAttempt correct
# COL14: male   : other female directed behaviour none(4:6) -> long distance female interaction
# COL15: male   : other close interaction behaviour none(4:5) -> short distance female interaction




startDir = '/media/gwdg-backup/BackUp/Annika_MSc/Data/smca/wtM_wtF/light/videos_wt-wt_light/txt/'
saveDir  = '/media/gwdg-backup/BackUp/Annika_MSc/Data/smca/wtM_wtF/light/videos_wt-wt_light/mat/'

# startDir = '/media/gwdg-backup/BackUp/Annika_MSc/Data/smca/dfM_dfF/light/videos_df-df_light/txt/'
# saveDir  = '/media/gwdg-backup/BackUp/Annika_MSc/Data/smca/dfM_dfF/light/videos_df-df_light/mat/'

# startDir = '/media/gwdg-backup/BackUp/Annika_MSc/Data/smca/wtM_wtF/dark/videos_wt-wt_dark/txt/'
# saveDir  = '/media/gwdg-backup/BackUp/Annika_MSc/Data/smca/wtM_wtF/dark/videos_wt-wt_dark/mat/'

# startDir = '/media/gwdg-backup/BackUp/Annika_MSc/Data/smca/dfM_dfF/dark/videos_df-df_dark/txt/'
# saveDir  = '/media/gwdg-backup/BackUp/Annika_MSc/Data/smca/dfM_dfF/dark/videos_df-df_dark/mat/'

filePos = QFileDialog.getOpenFileNames(None,'Load Data', startDir,filter = 'vc*',initialFilter = '.pkl')
filePos = filePos[0]


#filePos =  startDir + '/vc_2017_11_16__16_01_14b'
# define shorter behavioural names
behavNames = ['M_loc','M_mat', 'M_fem', 'M_wig','M_cop','M_clo','M_inc','F_loc','F_mat','F_rej','M_wiI','M_wiC','M_coI','M_coC','M_oFD','M_oCI' ]

# create analysis object
anaObj = analysis.analysisOffLine(filePos, fileType = 'txt', behavTags = behavNames, fps =25.0)
# read in data
anaObj.readData()

# compute negative modulator for wing extension and copulation attempts
anaObj.computeNegativeModulator([3,4],6)
# generate female directed behaviour that is not in close interaction
anaObj.computeInclusiveModulator(2,[3,4,5])
#generate close interaction behaviour that is not wing extension nor copulation attempts
anaObj.computeInclusiveModulator(5,[3,4])
#make sure locomotion is not paralell to the rest
anaObj.subtractBehav(0,[1,10,11,12,13,14,15])


# set analysis window
if startDir == '/media/gwdg-backup/BackUp/Annika_MSc/Data/smca/dfM_dfF/dark/videos_df-df_dark/txt/':
    start = [3000,3920,3220,3060,2375,4100,4200,3550,3660,3460,3280,3580,3160,2850,3150,3050,3050,3950,4550,2450,2850,2750,3550,2850] 
    end   = [x+7498 for x in start]
    anaObj.dataList = anaObj.setAnalysisWindow(start,end)
else:
    anaObj.dataList = anaObj.setAnalysisWindow()

#run analysisis not paralell to the rest
anaObj.subtractBehav(0,[1,10,11,12,13,14,15])
anaObj.subtractBehav(1,[10,11,12,13,14,15])

#run analysis
anaObj.runAnalysis([0,1,10,11,12,13,14,15])

# testSave
anaObj.saveDataMultiple(saveDir)
#anaObj.compressResultList(["perc","boutDurMean","frequency","transMat"])

#print len(anaObj.resultList)
#print "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
#for key, value in anaObj.resultList[0].iteritems():
#    print key,value
#    print " "
#print "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"