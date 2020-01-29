# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 13:58:46 2016

@author: bgeurten
"""

import icon as ic
import pygame
import os
reload(ic) 
this_files_directory=os.path.dirname(os.path.realpath('__file__'))
fileName = this_files_directory +'/icons/game/01.png'

myIcon = ic.icon()
myIcon.readImage(fileName)
myIcon.invertDecall()
myIcon.decall2icon()
myIcon.circle.show()