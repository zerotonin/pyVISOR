# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 13:42:07 2016

@author: bgeurten
"""
import numpy as np
import scipy.io as sio
import threading
from datetime import datetime
#import pandas as pd
import pickle
import xlsxwriter
import pygame
import os

class dataIO:
    """Data input/output handler for ethogram data.

    Supports saving annotations as plain text, Excel, MATLAB, and
    pickle formats. Also handles autosave with periodic background
    snapshots and overlay frame/video export.
    """
    def __init__(self,parent):
        self.autoSavePath = ''
        self.saveFpos     = ''
        self.loadFpos     = ''
        self.parent = parent
        self._autosave_thread = None
        self._autosave_stop_event = threading.Event()
        self._autosave_lock = threading.Lock()
        self._autosave_config = {
            'enabled': False,
            'interval': 300,
            'output_path': ''
        }

    def autosave(self):
        """Start, update, or stop the autosave worker.

        Autosave parameters are provided by the parent scorer via the
        ``autosave_settings`` attribute.  The expected schema is::

            {
                "enabled": bool,
                "interval_seconds": int,
                "directory": str,
            }

        The worker writes ``autosave_latest.pkl`` and
        ``autosave_latest.txt`` into the configured directory at the given
        interval.  When autosave is disabled any existing worker is shut
        down gracefully.
        """

        settings = getattr(self.parent, 'autosave_settings', None)
        if settings is None:
            return

        enabled = bool(settings.get('enabled', False))
        interval = int(settings.get('interval_seconds', 300))
        output_path = settings.get('directory', '') or ''

        snapshot_now = False
        with self._autosave_lock:
            self._autosave_config.update({
                'enabled': enabled,
                'interval': max(1, interval),
                'output_path': output_path
            })

            if not enabled:
                self._stop_autosave_locked()
                return

            if not self._autosave_thread or not self._autosave_thread.is_alive():
                self._autosave_stop_event.clear()
                self._autosave_thread = threading.Thread(target=self._autosave_worker,
                                                          name='pyvisor-autosave',
                                                          daemon=True)
                self._autosave_thread.start()
            else:
                snapshot_now = True

        if snapshot_now:
            self._write_autosave_snapshot()

    def stop_autosave(self):
        with self._autosave_lock:
            self._autosave_config['enabled'] = False
            self._stop_autosave_locked()

    def _stop_autosave_locked(self):
        if self._autosave_thread and self._autosave_thread.is_alive():
            self._autosave_stop_event.set()
            self._autosave_thread.join(timeout=1.0)
        self._autosave_thread = None
        self._autosave_stop_event = threading.Event()

    def _autosave_worker(self):
        # Perform an immediate snapshot followed by periodic updates.
        while True:
            try:
                self._write_autosave_snapshot()
            except Exception as exc:  # pragma: no cover - log and continue
                print('Autosave failed: {}'.format(exc))

            interval = self._autosave_config.get('interval', 300)
            if self._autosave_stop_event.wait(interval):
                break

    def _write_autosave_snapshot(self):
        with self._autosave_lock:
            if not self._autosave_config.get('enabled', False):
                return
            directory = self._autosave_config.get('output_path')
            if not directory:
                return

            os.makedirs(directory, exist_ok=True)

            data = self.parent.get_data()
            if data is False or data is None:
                return

            labels = []
            if hasattr(self.parent, 'get_labels'):
                labels = self.parent.get_labels() or []

            timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
            base_path = os.path.join(directory, 'autosave_latest')
            timestamp_base = os.path.join(directory, f'autosave_{timestamp}')

            self.saveAsPy(base_path + '.pkl', data)
            self.saveAsTXT(base_path + '.txt', data, labels)

            # Keep a timestamped copy to make it easy to revisit older states.
            self.saveAsPy(timestamp_base + '.pkl', data)
    
    def saveAsTXT(self,fpos,data,behavLabels):
        headStr = ''
        for i in range(len(behavLabels)):                
            headStr = headStr + 'COL' + str(i+1) + ': '+  str(behavLabels[i]) + '\n'             
        np.savetxt(fpos,data,fmt='%2i',header= headStr)
    
    def saveAsMat(self,fpos,data,behavLabels):
        info = ''
        for i in range(len(behavLabels)):                
            info = info + 'COL' + str(i+1) + ': ' + str(behavLabels[i]) + '\n'         
        sio.savemat(fpos, {'data':data,'info':info})
        
    def saveAsXLSX(self,fpos,data,behavLabels):            
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(fpos)
        worksheet = workbook.add_worksheet()

        

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0
        
        # Iterate over the data and write it out row by row.
        for label in (behavLabels):
            worksheet.write(row, col, label)
            col += 1
        for rowI in range(data.shape[0]):
            for colI in range( data.shape[1]):
                worksheet.write(rowI+1,colI,data[rowI,colI])

        workbook.close()
    
    def saveOverlayMovie(self, fPos, prefix='frame', extension='mp4'):
        """Export the scored video as an actual video file with icon overlays.

        If *extension* is 'mp4' or 'avi', a proper video file is written
        using PyAV.  For image formats ('png', 'jpeg', 'bmp', 'tga') a
        numbered image sequence is written instead.
        """
        scorer = self.parent
        if not hasattr(scorer, 'screen') or scorer.screen is None:
            print("saveOverlayMovie: scorer screen not available")
            return

        movLen = scorer.movie.length
        fPos = str(fPos)
        prefix = str(prefix)
        extension = str(extension)

        is_video = extension.lower() in ('mp4', 'avi', 'mkv', 'mov')

        if is_video:
            self._export_as_video(scorer, fPos, prefix, extension, movLen)
        else:
            self._export_as_image_sequence(scorer, fPos, prefix, extension, movLen)

    def _export_as_video(self, scorer, dPos, prefix, extension, movLen):
        """Write an mp4/avi video with overlays using PyAV."""
        try:
            import av as _av
        except ImportError:
            print("PyAV is required for video export. Install with: pip install av")
            return

        out_path = os.path.join(dPos, "{}.{}".format(prefix, extension))
        width = scorer.screen.get_width()
        height = scorer.screen.get_height()
        fps = int(scorer.movie._movie_fps)

        container = _av.open(out_path, mode='w')
        stream = container.add_stream('h264', rate=fps)
        stream.width = width
        stream.height = height
        stream.pix_fmt = 'yuv420p'

        for i in range(movLen - 1):
            surface = self._render_frame(scorer, i)
            # Convert pygame surface → numpy array (H, W, 3)
            arr = pygame.surfarray.array3d(surface)
            # pygame gives (W, H, 3) transposed — fix it
            arr = np.transpose(arr, (1, 0, 2))
            frame = _av.VideoFrame.from_ndarray(arr, format='rgb24')
            for packet in stream.encode(frame):
                container.mux(packet)
            if i % 100 == 0:
                print("Exporting frame {}/{}".format(i, movLen))

        # Flush
        for packet in stream.encode():
            container.mux(packet)
        container.close()
        print("Video exported: {}".format(out_path))

    def _export_as_image_sequence(self, scorer, dPos, prefix, extension, movLen):
        """Write numbered image files with overlays."""
        digitNum = len(str(movLen))
        for i in range(movLen - 1):
            fName = '{}_{}.{}'.format(prefix, str(i).zfill(digitNum), extension)
            fPath = os.path.join(dPos, fName)
            surface = self._render_frame(scorer, i)
            pygame.image.save(surface, str(fPath))
            if i % 100 == 0:
                print("Exporting frame {}/{}".format(i, movLen))
        print("Image sequence exported to: {}".format(dPos))

    def saveOverlayImage(self, fPos, targetFrame=37):
        """Save a single frame with behaviour icon overlays."""
        scorer = self.parent
        if not hasattr(scorer, 'screen') or scorer.screen is None:
            print("saveOverlayImage: scorer screen not available")
            return

        surface = self._render_frame(scorer, targetFrame)
        pygame.image.save(surface, str(fPos))
        print("Frame {} saved to: {}".format(targetFrame, fPos))

    @staticmethod
    def _render_frame(scorer, frame_number):
        """Render a single frame with overlays to a new surface."""
        from PIL import Image as _Image

        # Get the raw video frame
        raw = scorer.movie.getFrame(frame_number)
        raw = _Image.fromarray(raw).convert('RGB')
        movie_screen = pygame.surfarray.make_surface(np.rot90(raw))

        # Draw onto the scorer's screen
        scorer.screen.fill((0, 0, 0))
        scorer.screen.blit(movie_screen, (scorer.movie_window_offset, 144))

        # Draw icons for this frame
        if scorer.ethogram is not None:
            with scorer.ethogram.lock:
                scorer.ethogram.apply_states_at_frame(frame_number)
                scorer._update_icons()

        # Draw frame info text
        myfont = pygame.font.SysFont(pygame.font.get_default_font(), 15)
        label = myfont.render("frame: " + str(frame_number), 1, (255, 255, 0))
        label2 = myfont.render("time: {:.1f} s".format(
            frame_number / scorer.movie._movie_fps), 1, (255, 255, 0))
        scorer.screen.blit(label, (scorer.movie_window_offset + 10,
                                    scorer.movie.height - 45 + 144))
        scorer.screen.blit(label2, (scorer.movie_window_offset + 10,
                                     scorer.movie.height - 30 + 144))

        # Return a copy of the surface
        return scorer.screen.copy()

    def saveAsPy(self,fpos,data):
        with open(fpos, 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def loadTXT(self,fpos,animal1,animal2):
        # data = np.loadtxt(fpos)
        # animal1,animal2 = self.assignMatrix2animals(data,animal1,animal2)
        # return animal1,animal2
        pass
        
    def loadMAT(self,fpos,animal1,animal2):
        # matData = sio.loadmat(fpos)
        # animal1,animal2 = self.assignMatrix2animals(matData['data'],animal1,animal2)
        # return animal1,animal2
        pass
        
    def loadPickle(self,fpos,animals):
        with open(fpos, 'rb') as handle:
            data = pickle.load(handle)

        animals = self.assignMatrix2animals(data,animals)
        return animals
    
    def loadXLSX(self,fpos,animal1,animal2):
        # df = pd.read_excel('data.xlsx', sheetname='Sheet1')
        # animal1,animal2 = self.assignMatrix2animals(df.values,animal1,animal2)
        # return animal1,animal2
        pass
    
    def assignMatrix2animals(self,data,animals):
        colCounter = 0
        for animalI in range(len(animals)):
            for behavI in range(len(animals[animalI].behaviours)):
                animals[animalI].behaviours[behavI].ethogram = data[:,colCounter]
                colCounter +=1 
   
        return animals
