# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 15:47:20 2016

@author: bgeurten
"""


import ManualEthologyScorer as MES
import MediaHandler as MEH
import pygame
import os 
import time
import analysis as ana
this_files_directory=os.path.dirname(os.path.realpath('__file__'))

iconList = [pygame.image.load(this_files_directory+'/icons/game/wing.png'),
            pygame.image.load(this_files_directory+'/icons/game/shoe.png'),
            pygame.image.load(this_files_directory+'/icons/game/navi.png')]
            
reload(MES)
reload(MEH)
%matplotlib qt
filename = '/media/gwdg-backup/02-16-16/15-32-41.912.seq'

sco = MES.ManualEthologyScorer()
sco.addAnimal('male 1', #animal label
              100, # ethogram_length length
              ['flipper','thrust','glide'], # behaviour labels
              [0,0,0], # beginning status
              [[0,1,2],[0,1,2],[0,1,2]])# disjunction list first 4 or disjunct to each other as are the last two
              
sco.addAnimal('male 2', #animal label
              100, # ethogram_length length
              ['flipper','thrust','glide'], # behaviour labels
              [0,0,0], # beginning status
              [[0,1,2],[0,1,2],[0,1,2]])# disjunction list first 4 or disjunct to each other as are the last two

sco.loadNorPixSeq(filename)
sco.setIconPositions()

sco.animals[0].assignIconPos2UniqueDJB(sco.icon_path[0:1])
sco.animals[0].assignIcons( iconList,['simple']*3)
sco.animals[1].assignIconPos2UniqueDJB(sco.icon_path[7:8])
sco.animals[1].assignIcons( iconList,['simple']*3)

sco.setUIC('Keyboad') #PS,XBox
sco.setUIC('XBox',buttonBindings  = ['B4','H-10','H10','X','X','X',
                                     'B5','B2','B1','X','X','X',
                                     'B6','B7','B9','B10',
                                     'A0-','A0+','A1-','A1+',
                                     'A3-','A3+','A4+','A4-',
                                      'B8']) #PS,XBox

start_time = time.time()
sco.go()
elapsed_time = time.time() - start_time
print str(sco.movie.length/elapsed_time) + ' analysis fps'
anaO = ana.analysis(sco.animals)
anaO.plotFrequency(0)
