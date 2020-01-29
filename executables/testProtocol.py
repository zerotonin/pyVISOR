# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 12:52:32 2016

@author: bgeurten
"""
import numpy as np
import animalEthogram
reload(animalEthogram)
a = animalEthogram.animalEthogram(100,
                                  ['A1 B0','A1 B1','A1 B2','A1 B3','A1 B4','A1 B5'], 
                                  [0,0,0,0,0,0],
                                  [[0,1,2],[0,1,2],[0,1,2],[3],[4,5] ,[4,5]])
a.setBehaviour('Behav3',9,3)
a.setBehaviour('Behav3',16,3)

a.setBehaviour('Behav3',6,3)
a.setBehaviour('Idle3',1,3)

a.setBehaviour('Del3',12,3)
a.setBehaviour('Del3',14,3)

a.setBehaviour('Behav1',0,1)
a.setBehaviour('Behav2',12,2)
a.setBehaviour('Behav2',7,2)
a.setBehaviour('Del0',0,0)
a.setBehaviour('Del0',0,0)


e = a.getEthogram()