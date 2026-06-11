import os
from typing import Dict, List, Union
import threading

import numpy as np
import pygame
from PIL import Image

from .GUI.model.animal import AnimalNumber, Animal
from .GUI.model.movie_bindings import MovieBindings
from .MediaHandler import MediaHandler
from .ethogram import Ethogram
from .user_input_control import UserInputControl2
from .resources import resource_path
from . import dataIO
from .paths import ensure_autosave_dir

this_files_directory = os.path.dirname(os.path.realpath(__file__))


class ManualEthologyScorer2:
    """Real-time video annotation engine.

    Opens a pygame window showing the video with behaviour icon
    overlays. Processes gamepad/keyboard input to toggle behaviour
    states and records them frame-by-frame into an :class:`Ethogram`.

    Supports:

    - Sidecar-based session persistence (auto-save/resume)
    - Autosave to a configurable directory
    - F1-toggleable key binding overlay
    - Visual distinction between live and recorded annotations
    """

    def __init__(self, animals: Dict[AnimalNumber, Animal],
                 movie_bindings: MovieBindings, selected_device: str,
                 autosave_settings: Union[Dict[str, Union[bool, int, str]], None] = None,
                 overlay_settings: Union[Dict[str, Union[bool, int]], None] = None):
        self.animals = animals
        self.movie_bindings = movie_bindings
        self.selected_device = selected_device

        self._icon_columns = [0, 96, 192, 288, 384, 480]
        self._icon_rows = []  # type: List[int]
        self._icon_positions = {
            an: [] for an in self.animals
        }  # type: Dict[AnimalNumber, List[Tuple[int, int]]]

        self.window = pygame.display
        self._delete_icon = None
        self.ethogram = None
        self.movie = None  # type: Union[None, MediaHandler]
        self.user_input_control = None  # type: Union[None, UserInputControl2]
        self._autosave_settings = {
            'enabled': True,
            'interval_seconds': 300,
            'directory': ''
        }
        if autosave_settings:
            self.autosave_settings = autosave_settings
        else:
            self.autosave_settings = {}
        self.overlay_settings = overlay_settings or {"dark_font": False, "font_size": 15}
        self._axis_active = {}  # type: Dict[int, str]

        self._ethogram_lock = threading.RLock()
        self.dio = dataIO.dataIO(self)

    def go(self):
        if self.movie is None:
            raise RuntimeError("Movie has to be loaded before scorer can be run!")

        # Re-initialize pygame fully (needed for second+ runs after pygame.quit)
        pygame.init()
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()

        pygame.time.Clock()
        self._seed_axis_state()

        # setup icons
        icon = self.image2surf(str(resource_path("gamethogram_64.png")))
        self._delete_icon = self.image2surf(str(resource_path("icons", "game", "del.png")))
        self.window.set_icon(icon)
        self.window.set_caption("GameThogram — " + self.movie.fileName)

        self._adjust_window_size()

        self.movie.activeFrame = -1
        self._show_overlay = True  # show key binding overlay on start

        self.dio.autosave()

        analysing = True
        while analysing:
            analysing = self._loop()
        self.dio.stop_autosave()
        self.save_sidecar()  # persist session for seamless resume
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
                if event.key == pygame.K_F1:
                    self._show_overlay = not self._show_overlay
                else:
                    input_code = event.unicode
                    self.user_input_control.handle_input(input_code)
        self.refresh_media()
        with self.ethogram.lock:
            self.ethogram.apply_states_at_frame(self.movie.frameNo)
        return True

    def _handle_event_joyhatmotion(self, event):
        value = event.dict['value']
        input_code = 'H' + str(value[0]) + str(value[1])

        if input_code == 'H00':
            return
        self.user_input_control.handle_input(input_code)

    def _seed_axis_state(self):
        """Record the initial axis positions so trigger rest values don't
        fire a spurious input on the first event."""
        self._axis_active.clear()
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            for axis in range(joy.get_numaxes()):
                value = joy.get_axis(axis)
                if value < -0.3:
                    self._axis_active[axis] = '-'
                elif value > 0.3:
                    self._axis_active[axis] = '+'

    def _handle_event_joyaxismotion(self, event):
        value = event.dict['value']
        axis = event.dict['axis']
        if value < -0.3:
            direction = '-'
        elif value > 0.3:
            direction = '+'
        else:
            self._axis_active.pop(axis, None)
            return
        if self._axis_active.get(axis) == direction:
            return
        self._axis_active[axis] = direction
        input_code = 'A' + str(axis) + direction
        try:
            self.user_input_control.handle_input(input_code)
        except KeyError:
            pass

    def load_movie(self, filename: str, media_type: str):
        pygame.init()
        # Normalise GUI labels to internal media type keys
        _type_map = {
            'movie': 'movie',
            'norpix': 'norpix',
            'image': 'image',
            'imagesequence': 'image',
        }
        media_type = _type_map.get(media_type.lower(), media_type.lower())
        if media_type not in ('movie', 'norpix', 'image'):
            raise KeyError("media_type '{}' is not supported.".format(media_type))
        self.movie = MediaHandler(filename, media_type)
        self.ethogram = Ethogram(self.animals, self.movie.length, self._ethogram_lock)
        self.user_input_control = UserInputControl2(self.animals, self.movie_bindings,
                                                    self.selected_device,
                                                    self.movie,
                                                    self.ethogram)
        # Try to restore previous session from sidecar
        self._load_sidecar()

    # ── Sidecar persistence ─────────────────────────────────────

    def _sidecar_path(self) -> str:
        """Return the sidecar file path: <video_path>.pyvisor.pkl"""
        if self.movie is None:
            return ""
        return self.movie.fileName + ".pyvisor.pkl"

    def save_sidecar(self):
        """Persist the current ethogram to a sidecar file next to the video."""
        import pickle as _pickle
        path = self._sidecar_path()
        if not path:
            return
        data = self.get_data()
        labels = self.get_labels()
        if data is False or data is None:
            return
        try:
            with open(path, 'wb') as fh:
                _pickle.dump({
                    'data': data,
                    'labels': labels,
                    'n_frames': self.movie.length,
                    'fps': self.movie._movie_fps,
                    'media_file': self.movie.fileName,
                }, fh, protocol=_pickle.HIGHEST_PROTOCOL)
            print("Sidecar saved: {}".format(path))
        except Exception as exc:
            print("Failed to save sidecar: {}".format(exc))

    def _load_sidecar(self):
        """Load a previous session's ethogram from the sidecar file."""
        import pickle as _pickle
        path = self._sidecar_path()
        if not path:
            return
        try:
            with open(path, 'rb') as fh:
                session = _pickle.load(fh)
        except FileNotFoundError:
            return
        except Exception as exc:
            print("Could not load sidecar: {}".format(exc))
            return

        saved_data = session.get('data')
        saved_labels = session.get('labels', [])
        if saved_data is None or len(saved_labels) == 0:
            return

        # Check frame count matches
        n_frames_saved = saved_data.shape[0]
        if n_frames_saved != self.movie.length:
            print("Sidecar frame count mismatch ({} vs {}), skipping.".format(
                n_frames_saved, self.movie.length))
            return

        # Build a label → column index map from the saved data
        # Saved labels are like "animal_0 : aggression"
        # We need to map to ethogram column labels like "A0_aggression"
        saved_col_map = {}
        for i, lbl in enumerate(saved_labels):
            saved_col_map[lbl] = i

        with self.ethogram.lock:
            for an in sorted(self.ethogram.animal_ethograms.keys()):
                etho = self.ethogram.animal_ethograms[an]
                animal = self.animals[an]
                for col_name in etho._table.columns:
                    if col_name.endswith('_delete'):
                        continue
                    # Reconstruct the formatted label to match saved labels
                    behav = animal.behaviours.get(col_name)
                    if behav is None:
                        continue
                    formatted = "{} : {}".format(animal.name, behav.name)
                    if formatted in saved_col_map:
                        src_col = saved_col_map[formatted]
                        etho._table[col_name] = saved_data[:, src_col].astype(bool)

        print("Restored previous session from sidecar: {}".format(path))

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
        return pygame.image.frombytes(data, size, mode)

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
        if self._show_overlay:
            self._draw_bindings_overlay()
        pygame.display.update()

    def _update_icons(self):
        with self.ethogram.lock:
            for an in self.animals:
                self._update_icons_of_animal(an)

    def _update_icons_of_animal(self, an: int):
        animal_etho = self.ethogram.animal_ethograms[an]
        live_state = set(self.ethogram.current_states[an])
        recorded = set(animal_etho.get_active_labels_at_frame(self.movie.frameNo))

        # Check for delete in the live state
        delete_label = 'A{}_delete'.format(an)
        if delete_label in live_state:
            pos = self._icon_positions[an][0] if self._icon_positions[an] else (0, 0)
            self.screen.blit(self._delete_icon, pos)
            return

        # Collect all labels to display, tracking which are live vs recorded-only
        all_labels = []
        for lbl in recorded:
            if not lbl.endswith('_delete'):
                all_labels.append(lbl)
        for lbl in live_state:
            if not lbl.endswith('_delete') and lbl not in all_labels:
                all_labels.append(lbl)

        if not all_labels:
            return

        icons = animal_etho.get_icons(all_labels)
        positions = self._icon_positions[an][:len(icons)]

        for icon_surf, pos, label in zip(icons, positions, all_labels):
            is_live = label in live_state
            is_recorded = label in recorded

            if is_live and is_recorded:
                # Both: full icon + golden ring
                self.screen.blit(icon_surf, pos)
                self._draw_golden_ring(pos, icon_surf.get_size())
            elif is_live:
                # Active only: full icon + golden ring
                self.screen.blit(icon_surf, pos)
                self._draw_golden_ring(pos, icon_surf.get_size())
            else:
                # Recorded only: semi-transparent
                tmp = icon_surf.copy()
                tmp.set_alpha(100)
                self.screen.blit(tmp, pos)

    def _draw_golden_ring(self, pos, size):
        """Draw a golden border rectangle around an icon."""
        rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        pygame.draw.rect(self.screen, (255, 215, 0), rect, 3)

    def _update_text(self):
        font_size = self.overlay_settings.get("font_size", 15)
        if self.overlay_settings.get("dark_font", False):
            color = (30, 30, 30)
        else:
            color = (255, 255, 0)
        line_height = font_size + 2
        myfont = pygame.font.SysFont(pygame.font.get_default_font(), font_size)
        label = myfont.render("frame: " + str(self.movie.frameNo), 1, color)
        label2 = myfont.render("time: " + str(self.movie.get_time()) + ' s', 1, color)
        label3 = myfont.render("replay-fps: " + str(self.movie.fps), 1, color)
        base_y = self.movie.height + 144 - 3 * line_height
        x = self.movie_window_offset + 10
        self.screen.blit(label, (x, base_y))
        self.screen.blit(label2, (x, base_y + line_height))
        self.screen.blit(label3, (x, base_y + 2 * line_height))

    def _draw_bindings_overlay(self):
        """Draw a semi-transparent overlay listing all current key bindings.

        Toggle with F1.
        """
        font = pygame.font.SysFont(pygame.font.get_default_font(), 14)
        line_h = 18
        pad = 10
        lines = []

        # Behaviour bindings per animal
        for an in sorted(self.animals.keys()):
            animal = self.animals[an]
            lines.append(("--- {} (A{}) ---".format(animal.name, an),
                          (200, 200, 255)))
            for label in sorted(animal.behaviours.keys()):
                behav = animal.behaviours[label]
                binding = behav.key_bindings[self.selected_device]
                btn_str = binding if binding else "?"
                lines.append(("  {} = {}".format(btn_str, behav.name),
                              (255, 255, 255)))

        # Movie bindings
        lines.append(("--- movie controls ---", (200, 200, 255)))
        for action_name in sorted(self.movie_bindings.keys()):
            action = self.movie_bindings[action_name]
            binding = action.key_bindings[self.selected_device]
            btn_str = binding if binding else "?"
            lines.append(("  {} = {}".format(btn_str, action_name),
                          (255, 255, 200)))

        lines.append(("", (0, 0, 0)))
        lines.append(("  [F1] toggle this overlay", (180, 180, 180)))

        # Draw semi-transparent background
        overlay_w = 280
        overlay_h = len(lines) * line_h + pad * 2
        overlay_surface = pygame.Surface((overlay_w, overlay_h))
        overlay_surface.set_alpha(180)
        overlay_surface.fill((20, 20, 40))

        x = self.screen.get_width() - overlay_w - 10
        y = 150
        self.screen.blit(overlay_surface, (x, y))

        # Render text lines
        for i, (text, color) in enumerate(lines):
            rendered = font.render(text, True, color)
            self.screen.blit(rendered, (x + pad, y + pad + i * line_h))

    @property
    def autosave_settings(self):
        return self._autosave_settings

    @autosave_settings.setter
    def autosave_settings(self, settings: Dict[str, Union[bool, int, str]]):
        self._autosave_settings.update(settings)
        self._autosave_settings['interval_seconds'] = int(
            max(1, int(self._autosave_settings.get('interval_seconds', 300)))
        )
        if not self._autosave_settings.get('directory'):
            self._autosave_settings['directory'] = str(ensure_autosave_dir())

    def get_data(self):
        if self.ethogram is None:
            return False

        with self.ethogram.lock:
            matrices = []
            for an in sorted(self.ethogram.animal_ethograms.keys()):
                etho = self.ethogram.animal_ethograms[an]
                matrix = etho.to_numpy()
                labels = [col for col in etho._table.columns]
                if matrix.size == 0:
                    continue
                # Filter out delete columns
                keep = [i for i, lbl in enumerate(labels)
                        if not lbl.endswith('_delete')]
                if keep:
                    matrices.append(matrix[:, keep])

        if not matrices:
            return False

        if len(matrices) == 1:
            return matrices[0]
        return np.hstack(matrices)

    def get_labels(self) -> List[str]:
        if self.ethogram is None:
            return []

        labels: List[str] = []
        with self.ethogram.lock:
            for an in sorted(self.ethogram.animal_ethograms.keys()):
                all_labels = self.ethogram.animal_ethograms[an].get_formatted_behaviour_labels()
                all_cols = list(self.ethogram.animal_ethograms[an]._table.columns)
                for col, lbl in zip(all_cols, all_labels):
                    if not col.endswith('_delete'):
                        labels.append(lbl)
        return labels

    def save_data(self, fpos, mode='text'):
        data = self.get_data()
        if data is False or data is None:
            return
        behav_labels = self.get_labels()

        if mode == 'text':
            self.dio.saveAsTXT(fpos, data, behav_labels)
        elif mode == 'xlsx':
            self.dio.saveAsXLSX(fpos, data, behav_labels)
        elif mode == 'matLab':
            self.dio.saveAsMat(fpos, data, behav_labels)
        elif mode == 'pickle':
            self.dio.saveAsPy(fpos, data)
        else:
            raise KeyError("Unknown mode for save_data: {}".format(mode))
