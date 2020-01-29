# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 13:45:36 2016

@author: bgeurten
"""


import ManualEthologyScorer as MES
import MediaHandler as MEH
import time
reload(MES)
reload(MEH)
%matplotlib qt

num = 'koeln'
pPath = '/media/gwdg-backup/BackUp/Seals/Seehunde2/'

sco = MES.ManualEthologyScorer()
sco.loadImageSequence( pPath + num + '/*.jpg')
sco.setUIC('XBox') #XBox
start_time = time.time()
sco.go()
elapsed_time = time.time() - start_time
print str(sco.movie.length/elapsed_time) + ' analysis fps'
sco.save_data(pPath + num + '_glideData.mat','matLab')
