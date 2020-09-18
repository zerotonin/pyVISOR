# -*- coding: utf-8 -*-
"""
Created on Tue May 24 19:33:50 2016

@author: bgeurten
"""

import ManualEthologyScorer as MES
import MediaHandler as MEH
import pygame
import os 
this_files_directory=os.path.dirname(os.path.realpath('__file__'))

iconList = [pygame.image.load(this_files_directory+'/heart.png'),
            pygame.image.load(this_files_directory+'/sword.png'),
            pygame.image.load(this_files_directory+'/wing.png'),
            pygame.image.load(this_files_directory+'/shoe.png'),
            pygame.image.load(this_files_directory+'/toothBrush.png'),
            pygame.image.load(this_files_directory+'/telescope.png')]
            
reload(MES)
reload(MEH)
%matplotlib qt
        

sco = MES.ManualEthologyScorer()
sco.addAnimal('male 1', #animal label
              100, # ethogram length
              ['courtship','aggression','wing ext','leg fenc','cleaning','exploration'], # behaviour labels
              [0,0,0,0,0,0,0], # beginning status
              [[0,1,2,3],[0,1,2,3],[0,1,2,3],[0,1,2,3],[4,5],[4,5]]), # disjunction list first 4 or disjunct to each other as are the last two
              
sco.addAnimal('male 2', #animal label
              100, # ethogram length
              ['courtship','aggression','wing ext','leg fenc','cleaning','exploration'], # behaviour labels
              [0,0,0,0,0,0,0], # beginning status
              [[0,1,2,3],[0,1,2,3],[0,1,2,3],[0,1,2,3],[4,5],[4,5]]), # disjunction list first 4 or disjunct to each other as are the last two
sco.loadMovie('test.mpg')#/home/bgeurten/out1.avi')#'/media/bgeurten/TOSHIBA_EXT/Mai/18_05_Mi/Vid-20160518-001.avi')
sco.setIconPositions()
sco
sco.animals[0].assignIconPos2UniqueDJB(sco.icon_path[0:2])
sco.animals[0].assignIcons( iconList,['simple']*6)
sco.animals[1].assignIconPos2UniqueDJB(sco.icon_path[6:8])
sco.animals[1].assignIcons( iconList,['simple']*6)

sco.setUIC('Keyboad') #PS,XBox
sco.setUIC('XBox') #PS,XBox
sco.go()


import ManualEthologyScorer as MES
import MediaHandler as MEH

reload(MES)
reload(MEH)
%matplotlib qt
sco = MES.ManualEthologyScorer()
sco.loadMovie('/home/bgeurten/out1.avi')#'/media/bgeurten/TOSHIBA_EXT/Mai/18_05_Mi/Vid-20160518-001.avi')
sco.setUIC('PS') #XBox
sco.go()


import ManualEthologyScorer as MES
import MediaHandler as MEH

reload(MES)
reload(MEH)
%matplotlib qt
sco = MES.ManualEthologyScorer()
sco.loadImageSequence('/home/bgeurten/frames/f*.jpg')#'/media/bgeurten/TOSHIBA_EXT/Mai/18_05_Mi/Vid-20160518-001.avi')
sco.setUIC('PS') #XBox
sco.go()






sco.save_data('./data.xlsx','xlsx')
sco.save_data('./data.txt','text')
sco.save_data('./data.obj','pickle')
sco.save_data('./data.mat','matLab')


reload(MES)
reload(MEH)
%matplotlib qt

sco2 = MES.ManualEthologyScorer()
sco2.loadMovie('test.mpg')
sco2.load_data('./data.xlsx','xlsx')
sco2.go()