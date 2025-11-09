# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 13:19:47 2016

@author: bgeurten
"""


from PIL import Image, ImageDraw
import pygame
import numpy as np
import os
from pathlib import Path

from .resources import icons_root

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


class Icon:
    
    def __init__(self, size=(96, 96), color=(144, 21, 222), alpha=255):
        self.size   = size
        self.image  = []
        self.color  = color
        self.alpha  = alpha
        self.circle = []
        self.decall = []
        self.radius = int(self.size[0]/2)
        self.icon   = None
    
    def readImage(self, filename):
        self.decall = Image.open(filename).convert('RGBA')
    
    def decall2icon(self):
        self.drawCircle()
        pos = self.getDecallPos()
        size = self.getMaxDecallSize()  
        self.decall = self.decall.resize(size, Image.ANTIALIAS)
        self.circle.paste(self.decall, pos, self.decall)
        self.icon = self.circle
    
    def drawCircle(self):  
        im = Image.new('RGBA',  self.size)
        draw = ImageDraw.Draw(im)
        draw.ellipse((0, 0, im.size[0], im.size[1]), fill=self.color)
        del draw
        self.circle = im
        
    def getMaxDecallSize(self):
        # the diagonal of the biggest square in a circle is the diameter of that circle
        # D denotes the diameter and Pythogoras c² = a²+b² becomes c²=2*a² for a = b (
        # as for squares a=b)  => (2r)² = 2a² | (2r)² = a² | 4r²/2 =a² |sqrt(2r²) =a
        decallSize = int(np.sqrt(2*self.radius**2))
        return  (decallSize,decallSize)   

    def getDecallPos(self):
        X = (np.sin(np.pi/4) * -1*self.radius) + self.size[0]/2
        Y = (np.cos(np.pi/4) * -1*self.radius) + self.size[0]/2
        return (int(X),int(Y))
        
    def invertDecall(self):
        r, g, b, a = self.decall.split()
        def invert(image):
            return image.point(lambda p: 255 - p)
        r, g, b = map(invert, (r, g, b))
        self.decall = Image.merge(self.decall.mode, (r, g, b, a))
    
    def icon2pygame(self) -> pygame.image:
        raw_str = self.icon.tobytes("raw", 'RGBA')
        return pygame.image.fromstring(raw_str, self.size , 'RGBA')

    
def write_tmp_icon(path_to_icon, color):
    if path_to_icon is None:
        return ""
    if len(path_to_icon) == 0:
        return ""
    icon_path = Path(path_to_icon)
    try:
        relative_path = icon_path.relative_to(icons_root())
    except ValueError:
        folders = []
        fname = icon_path.stem
        extension = icon_path.suffix
    else:
        folders = list(relative_path.parent.parts)
        fname = relative_path.stem
        extension = relative_path.suffix
    color_str = "_%i_%i_%i" % color
    tmp_parts = folders + [fname + color_str + extension]
    tmp_str = "/".join(part for part in tmp_parts if part)
    if (os.path.isfile(HOME + '/.pyvisor/.tmp_icons/' + tmp_str)):
        return tmp_str
    current_path = HOME + '/.pyvisor/.tmp_icons'
    for folder in folders:
        current_path = current_path + "/" + folder
        if (os.path.isdir(current_path)):
            continue
        os.mkdir(current_path)
    I = Icon(color=color)
    I.readImage(str(icon_path))
    I.decall2icon()
    f = open(HOME + '/.pyvisor/.tmp_icons/' + tmp_str, 'wb')
    I.icon.save(f)
    return tmp_str
