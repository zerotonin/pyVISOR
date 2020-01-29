# -*- coding: utf-8 -*-
"""
Created on Tue May 24 17:31:07 2016

@author: bgeurten
"""

import pygame


FPS =60

pygame.init()
# clock and movie setup
clock   = pygame.time.Clock()
movie   = pygame.movie.Movie('test.mpg')
movSize = movie.get_size()
#setup icons
sword = pygame.image.load('sword1.png')
heart = pygame.image.load('heart1.png')
screen = pygame.display.set_mode(movSize)
movie_screen = pygame.Surface(movSize).convert()
animalPos1 = (0,0)
animalPos2 = (movSize[0]-96,0)

# intialise joy pad
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# start movie
movie.set_display(movie_screen)
movie.play()

# 
status

# during show time
playing = True
while playing:
    # handle events such as key and button presses
    for event in pygame.event.get():       
        if event.type == pygame.QUIT:
            movie.stop()
            playing = False
        if event.type == pygame.JOYBUTTONDOWN:
            button = event.button
            time  = movie.get_time()
            frame = movie.get_frame()
            print("Joystick button " + str(button) + " pressed. @ t: " +str(time)+ ' f:' +str(frame))
        if event.type == pygame.JOYBUTTONUP:
            button = event.button
            time  = movie.get_time()
            frame = movie.get_frame()
            
            print("Joystick button " + str(button) + " released. @ t: " +str(time)+ ' f:' +str(frame))
        if event.type == pygame.KEYDOWN:
            button = event.key
            time  = movie.get_time()
            frame = movie.get_frame()
            print("Key " + str(button) + " pressed. @ t: " +str(time)+ ' f:' +str(frame))
        if event.type == pygame.KEYUP:
            button = event.key
            time  = movie.get_time()
            frame = movie.get_frame()
            print("Key " + str(button) + " released. @ t: " +str(time)+ ' f:' +str(frame))
    
    #update the movie
    screen.blit(movie_screen,(0,0))
    screen.blit(heart,animalPos1)
    screen.blit(sword,animalPos2)
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()