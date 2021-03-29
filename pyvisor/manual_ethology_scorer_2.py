import os
from typing import Dict, List, Tuple, Union

import numpy as np
import pygame
from PIL import Image

from .GUI.model.animal import AnimalNumber, Animal
from .GUI.model.movie_bindings import MovieBindings
from .MediaHandler import MediaHandler
from .ethogram import Ethogram
from .user_input_control import UserInputControl2

this_files_directory = os.path.dirname(os.path.realpath(__file__))


class ManualEthologyScorer2:

    def __init__(self, animals: Dict[AnimalNumber, Animal],
                 movie_bindings: MovieBindings, selected_device: str):
        self.animals = animals
        self.movie_bindings = movie_bindings
        self.selected_device = selected_device

        self._icon_columns = [0, 96, 192, 288, 384, 480]
        self._icon_rows = []  # type: List[int]
        self._icon_positions = {
            an: [] for an in self.animals
        }  # type: Dict[AnimalNumber, List[Tuple[int, int]]]

        self.window = pygame.display
        self.ethogram = None
        self.movie = None  # type: Union[None, MediaHandler]
        self.user_input_control = None  # type: Union[None, UserInputControl2]

    def go(self):
        if self.movie is None:
            raise RuntimeError("Movie has to be loaded before scorer can be run!")

        pygame.time.Clock()

        # setup icons
        icon = self.image2surf(this_files_directory + "/../resources/MES.png")
        self.delete_icon = self.image2surf(this_files_directory + "/../resources/icons/game/del.png")
        self.window.set_icon(icon)
        self.window.set_caption("Manual Ethology Scorer - " + self.movie.fileName)

        self._adjust_window_size()

        self.movie.activeFrame = -1

        analysing = True
        while analysing:
            analysing = self._loop()
        pygame.quit()

    def _loop(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.JOYBUTTONDOWN:
                input_code = 'B' + str(event.button)
                self.user_input_control.handle_input(input_code)
            if event.type == pygame.JOYAXISMOTION:
                self._handle_event_joyaxismotion(event)
            if event.type == pygame.JOYHATMOTION:
                self._handle_event_joyhatmotion(event)
            if event.type == pygame.KEYDOWN:
                self.user_input_control.handle_input(event.key)
            self.refresh_media()

    def _handle_event_joyhatmotion(self, event):
        value = event.dict['value']
        input_code = 'H' + str(value[0]) + str(value[1])

        if input_code == 'H00':
            return
        self.user_input_control.handle_input(input_code)

    def _handle_event_joyaxismotion(self, event):
        value = event.dict['value']
        axis = event.dict['axis']
        input_code = 'A' + str(axis)
        try:
            if value < -0.3:
                input_code = input_code + '-'
                self.user_input_control.handle_input(input_code)
            elif value > 0.3:
                input_code += '+'
                self.user_input_control.handle_input(input_code)
        except KeyError:
            pass

    def load_movie(self, filename: str, media_type: str):
        pygame.init()
        media_type = media_type.lower()
        if media_type not in ['movie', 'norpix', 'image']:
            raise KeyError("media_type '{}' is not supported.".format(media_type))
        self.movie = MediaHandler(filename, media_type)
        self.ethogram = Ethogram(self.animals, self.movie.length)
        self.user_input_control = UserInputControl2(self.animals, self.movie_bindings,
                                                    self.selected_device,
                                                    self.movie,
                                                    self.ethogram)

    def _adjust_window_size(self):
        height = self.movie.height
        width = self.movie.width
        if width < 576:
            self.movie_window_offset = int((576 - width) / 2.0)
            width = 576
        else:
            self.movie_window_offset = 0
        height = height + 288
        self.screen = self.window.set_mode((int(width), int(height)))
        self._define_icon_positions()
        self._try_auto_assign_icon_positions()

    @staticmethod
    def image2surf(fPos):
        img = Image.open(fPos).convert('RGBA')
        mode = img.mode
        size = img.size
        data = img.tobytes()
        return pygame.image.fromstring(data, size, mode)

    def _define_icon_positions(self):
        self._icon_rows = [0, 96, self.screen.get_height() - 96, self.screen.get_height() - 144]

    def _try_auto_assign_icon_positions(self):
        if len(self.animals) > 4:
            raise RuntimeError("Automatically assigning Icon positions currently works only"
                               " for up to 4 animals.")
        for i, an in enumerate(self.animals.keys()):
            ypos = self._icon_rows[i]
            for xpos in self._icon_columns:
                self._icon_positions[an].append((ypos, xpos))

    def refresh_media(self):
        frame = self.movie.get_frame()
        movie_screen = pygame.surfarray.make_surface(np.rot90(frame))
        self.screen.fill((0, 0, 0))
        self.screen.blit(movie_screen, (self.movie_window_offset, 144))
        self._update_icons()
        self._update_text()
        pygame.display.update()

    def _update_icons(self):
        for an in self.animals:
            self._update_icons_of_animal(an)

    def _update_icons_of_animal(self, an: int):
        animal_etho = self.ethogram.animal_ethograms[an]
        state = self.ethogram.current_states[an]
        if len(state) == 0:
            return
        if 'delete' in state:
            icons = [self.delete_icon]
        else:
            icons = animal_etho.get_icons(state)
        positions = self._icon_positions[an][:len(icons)]
        blits = [t for t in zip(icons, positions)]
        self.screen.blits(blits)

    def _update_text(self):
        myfont = pygame.font.SysFont(pygame.font.get_default_font(), 15)
        label = myfont.render("frame: " + str(self.movie.frameNo), 1, (255, 255, 0))
        label2 = myfont.render("time: " + str(self.movie.get_time()) + ' s', 1, (255, 255, 0))
        label3 = myfont.render("replay-fps: " + str(self.movie.fps), 1, (255, 255, 0))
        self.screen.blit(label, (self.movie_window_offset + 10, self.movie.height - 45 + 144))
        self.screen.blit(label2, (self.movie_window_offset + 10, self.movie.height - 30 + 144))
        self.screen.blit(label3, (self.movie_window_offset + 10, self.movie.height - 15 + 144))
