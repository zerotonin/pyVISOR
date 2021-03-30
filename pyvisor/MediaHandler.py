# -*- coding: utf-8 -*-
"""
Created on Wed May 25 08:40:38 2016

@author: bgeurten
"""
from typing import Union

import pims
import numpy as np
import pygame
from PIL import Image


class MediaHandler:

    def __init__(self, filename, mode, bufferSize=2000):
        self.activeFrame = []
        self.frameNo = 0
        self.mode = mode
        self.buffer = {}
        self.bufferLog = []
        self.bufferSize = bufferSize
        self.fileName = filename

        self._run_movie = False
        self._run_forward = True
        self.t_last_frame_drawn = 0.0

        if mode == 'movie':

            self.media = pims.open(filename)
            self.length = len(self.media) - 1
            self.height, self.width, self.colorDim = self.media.frame_shape
            self.size = (self.width, self.height)
            self.fps = 25

        elif self.mode == 'norpix':
            self.media = pims.NorpixSeq(filename)
            self.length = len(self.media) - 1
            if len(self.media.frame_shape) == 2:
                self.height, self.width = self.media.frame_shape
            else:
                self.height, self.width, self.colorDim = self.media.frame_shape

            self.size = (self.width, self.height)
            self.fps = self.media.frame_rate
        elif self.mode == 'image':
            # here the programs for image list should follow
            self.media = pims.ImageSequence(filename)
            self.length = len(self.media) - 1
            self.height, self.width, self.colorDim = self.media.frame_shape
            self.size = (self.width, self.height)
            self.fps = 25
        else:
            raise RuntimeError('MediaHandler: unknown input_device')
        self._movie_fps = self.fps


    def get_frame(self) -> np.ndarray:
        period = 1.0 / self.fps * 1000
        t = pygame.time.get_ticks()
        time_diff = t - self.t_last_frame_drawn
        frame_number = self.frameNo
        if time_diff > period and self._run_movie:
            if self._run_forward:
                frame_number += 1
                self.t_last_frame_drawn = t
            else:
                frame_number -= 1
                self.t_last_frame_drawn = t
            if frame_number > self.length - 2 or frame_number < 0:
                self._run_movie = False
        frame = self.getFrame(frame_number)
        frame = Image.fromarray(frame)
        frame = frame.convert('RGB')
        return frame



    def getFrame(self, frameNo):

        if frameNo < 0:
            frameNo = 0

        elif frameNo > self.length:
            frameNo = self.length

        # check if frame can be read from buffer    
        if frameNo in self.bufferLog:
            self.activeFrame = np.array(self.buffer[frameNo], copy=True)
            self.frameNo = frameNo
        else:

            if self.mode == 'movie':
                self.getFrameMov(frameNo)
            elif self.mode == 'norpix':
                self.getFrameNorpix(frameNo)
            elif self.mode == 'image':
                self.getFrameImage(frameNo)
            else:
                print('MediaHandler:unknown input_device')

            # delete from buffer if to large
            if len(self.bufferLog) > self.bufferSize:
                self.buffer.pop(self.bufferLog[0])
                self.bufferLog.pop(0)

            # update buffer
            self.buffer[frameNo] = np.array(self.activeFrame, copy=True)
            self.bufferLog.append(frameNo)

        return self.activeFrame

    def get_frameNo(self):
        return self.frameNo

    def getFrameMov(self, frameNo):

        self.frameNo = frameNo
        self.activeFrame = self.media.get_frame(frameNo)

    def getFrameNorpix(self, frameNo):
        self.frameNo = frameNo
        self.activeFrame = self.media.get_frame(frameNo)

    def getFrameImage(self, frameNo):
        self.frameNo = frameNo
        self.activeFrame = self.media.get_frame(frameNo)

    def get_time(self):
        return self.frameNo / self._movie_fps

    def toggle_play(self):
        self._run_movie = not self._run_movie

    def set_run_forward(self):
        self._run_forward = True

    def set_run_reverse(self):
        self._run_forward = False

    def increase_fps(self):
        self.fps += 3

    def decrease_fps(self):
        self.fps -= 3

    def set_current_frame_delta(self, delta: int):
        self.frameNo += delta

    def set_stop(self):
        self._run_movie = False
        self.frameNo = 0
