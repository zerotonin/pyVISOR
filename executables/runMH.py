# -*- coding: utf-8 -*-
"""
Created on Wed May 25 08:27:37 2016

@author: bgeurten
"""
import MediaHandler
import matplotlib.pyplot as plt

%matplotlib qt

reload(MediaHandler)

mh = MediaHandler.MediaHandler('test.mpg','movie')
frame = mh.getFrame(1) 
frame2 =mh.getFrame(200)
frame3 =mh.getFrame(110)
imgplot = plt.imshow(frame)
