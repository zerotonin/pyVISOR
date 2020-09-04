from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np
import styles, pygame, pickle
from pygame.locals import *
import behavBinding
import os, copy, collections
HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
bGround = HERE +"pictures/head.png"
DEVICES = {"Keyboard":    [ HERE + "/pictures/gamePad_KB_left.png"  , HERE + "/pictures/gamePad_KB_right.png"  ], 
           "Playstation": [ HERE + "/pictures/gamePad_PS_left.png"  , HERE + "/pictures/gamePad_PS_right.png"  ],
           "X-Box":       [ HERE + "/pictures/gamePad_XB_left.png"  , HERE + "/pictures/gamePad_XB_right.png"  ],
           "Free":        [ HERE + "/pictures/gamePad_free_left.png", HERE + "/pictures/gamePad_free_left.png" ]}
class TabSimpleButtons(QWidget):
    
    def __init__(self,parent):
        
        self.analysis_list = [] 
        super(TabSimpleButtons,self).__init__()

        self.parent=parent
        pygame.init()
        # Initialize the joysticks
        pygame.joystick.init()
        self.init_UI()