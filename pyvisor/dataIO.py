# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 13:42:07 2016

@author: bgeurten
"""
import numpy as np
import scipy.io as sio
from time import sleep
import threading
from datetime import datetime
#import pandas as pd
import pickle, xlsxwriter, pygame,os

class dataIO:
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
    
    def saveOverlayMovie(self,dPos,prefix = 'frame',extension = 'png'):
        # shortHand
        movLen   = self.parent.movie.length
        digitNum = len(str(movLen))
        # get rid of qStrings as pygame.image.save cannot use it
        dPos   = str(dPos)
        prefix = str(prefix)
        extension = str(extension)
        # stop movie
        origRunMovFlag = self.parent.runMov
        origRefreshMediaFlag = self.parent.refreshMediaFlag
        for i in range(movLen-1):
            fName = prefix + '_' + str(i).zfill(digitNum) + '.' + extension
            fPos = os.path.join(dPos,fName)
            # get frame from media
            frame = self.parent.movie.getFrame(i)
            # draw frame to screen
            movie_screen=pygame.surfarray.make_surface(np.rot90(frame))
            #update the movie
            self.parent.screen.blit(movie_screen,(0,0))
            # update icons
            self.parent.updateIcons()
            pygame.display.update()
            #save image
            image = self.parent.window.get_surface()
            print(fPos)
            pygame.image.save(image, str(fPos))
            sleep(0.1)


        # restore original flag status
        self.parent.runMov = origRunMovFlag
        self.parent.refreshMediaFlag = origRefreshMediaFlag

    def saveOverlayImage(self,fPos,targetFrame =37):
        # This function saves a single frame
        # stop movie
        origRunMovFlag = self.parent.runMov
        origRefreshMediaFlag = self.parent.refreshMediaFlag

        self.parent.runMov = False
        self.parent.refreshMediaFlag = False
        # get frame from media
        frame = self.parent.movie.getFrame(targetFrame)
        # draw frame to screen
        movie_screen=pygame.surfarray.make_surface(np.rot90(frame))
        #update the movie
        self.parent.screen.blit(movie_screen,(0,0))
        # update icons
        self.parent.updateIcons()
        pygame.display.update()
        #save image
        image = self.parent.window.get_surface()
        pygame.image.save(image, str(fPos))
        # restore original flag status
        self.parent.runMov = origRunMovFlag
        self.parent.refreshMediaFlag = origRefreshMediaFlag

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
