import os
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QComboBox, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QInputDialog, QMessageBox,
                             QCheckBox, QSpinBox)

from .model.animal import Animal
from .model.behaviour import Behaviour
from .model.gui_data_interface import GUIDataInterface
from ..manual_ethology_scorer_2 import ManualEthologyScorer2
from ..paths import ensure_extension as _ensure_extension
from itertools import chain
HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


class TabAnalysis(QWidget):
    """Analysis tab — video loading, scorer control, and data export.

    Provides the workflow for loading media, configuring autosave,
    running the scorer, and exporting annotated data or overlay
    frames/videos.
    """

    def __init__(self, parent: QWidget,
                 gui_data_interface: GUIDataInterface):

        super().__init__()
        self.analysis_list = []
        self.parent = parent
        self.gui_data_interface = gui_data_interface
        self.manual_scorer = None  # type: Union[ManualEthologyScorer2, None]

        self.media_file_name = ''
        self.media_type = ''
        self.init_UI()
        
    def init_UI(self):
        self._init_background_image()

        self._init_layout_boxes()

        self.labelStyle = """
        color: #d4d4d4;
        background-color: transparent;
        margin-top: 2px;
        font-weight: bold;
        """
        self.makeBehaviourSummary()
        self.makeMovieFileIO()
        self.makeAutosaveRow()
        self.makeOverlayRow()
        self.makeCommandoRow()
        self.setLayout(self.vbox)

        self.parent.tabs.currentChanged.connect(self.makeBehaviourSummary)

    def _init_layout_boxes(self):
        self.vbox = QVBoxLayout()
        self.hboxMov = QHBoxLayout()
        self.hboxAutosave = QHBoxLayout()
        self.hboxConciseBehav = QHBoxLayout()
        self.hboxOverlay = QHBoxLayout()
        self.hboxCommand = QHBoxLayout()
        self.hboxExport = QHBoxLayout()
        self.vbox.addStretch()
        self.vbox.addLayout(self.hboxConciseBehav)
        self.vbox.addLayout(self.hboxMov)
        self.vbox.addLayout(self.hboxAutosave)
        self.vbox.addLayout(self.hboxOverlay)
        self.vbox.addLayout(self.hboxCommand)
        self.vbox.addLayout(self.hboxExport)
        self.vbox.addStretch()

    def _init_background_image(self):
        pass  # replaced by global dark theme

    def makeBehaviourSummary(self):
        self.clearLayout(self.hboxConciseBehav)
        # ------------------------
        #      behaviour widgets
        # ------------------------
        
        self._create_step_label()
        for animalI in sorted(self.gui_data_interface.animals.keys()):
            vbox = self.makeBehavInfoBox(
                self.gui_data_interface.animals[animalI]
            )
            self.hboxConciseBehav.addLayout(vbox) 
        
        movieControlBox = self.makeMovieControlInfoBox()
        self.hboxConciseBehav.addLayout(movieControlBox) 
        self.hboxConciseBehav.addStretch()

    def _create_step_label(self):
        self.behav_stepLabel = QLabel('Step 1 Check behaviour settings: ')
        self.behav_stepLabel.resize(20, 40)
        self.behav_stepLabel.setStyleSheet(self.labelStyle)
        self.hboxConciseBehav.addWidget(self.behav_stepLabel)

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())
                
    def makeMovieFileIO(self):
        # ------------------------
        #       movie widgets
        # ------------------------

        # Create step label
        self.mov_stepLabel = QLabel('Step 2 Load Image Data: ')
        self.mov_stepLabel.resize(60, 40)
        self.mov_stepLabel.setStyleSheet(self.labelStyle)
        self.hboxMov.addWidget(self.mov_stepLabel)

        # Create info label
        self.mov_label = QLabel('Nothing loaded ...')
        self.mov_label.resize(280, 40)
        self.mov_label.setStyleSheet(self.labelStyle)
        
        # Create Button - load video (all supported formats in one filter)
        self.btn_movie = QPushButton('load video')
        self.btn_movie.setToolTip(
            "Open a video file.\n"
            "Supports AVI, MP4, MOV, MKV, MPG, WMV, FLV, WebM, M4V.")
        argList = [['Video files (*.avi *.mov *.mp4 *.mpg *.mkv *.wmv *.flv *.webm *.m4v)',
                     'All files (*)'],
                   'video loaded: ',
                   'failed to load video', 'Movie', 'Single']
        self.btn_movie.clicked.connect((lambda al: lambda: self.loadMedia(al))(argList))
        self.hboxMov.addWidget(self.btn_movie)

        # Create Button Img Sequence loading
        self.btn_image = QPushButton('load image sequence')
        self.btn_image.setToolTip(
            "Open a directory of numbered images.\n"
            "Supports JPEG, PNG, GIF, TIFF, BMP.")
        argList = [['Image files (*.jpg *.jpeg *.png *.gif *.tif *.tiff *.bmp)',
                     'All files (*)'],
                   'image sequence loaded: ',
                   'failed to load image sequence: ', 'ImageSequence', 'Multi']
        self.btn_image.clicked.connect((lambda argList: lambda: self.loadMedia(argList))(argList))
        self.hboxMov.addWidget(self.btn_image)

        # Create Button Norpix loading
        self.btn_norpix = QPushButton('load Norpix SEQ')
        self.btn_norpix.setToolTip("Open a Norpix .seq sequence file.")
        argList = [['Norpix files (*.seq)', 'All files (*)'],
                   'Norpix sequence file loaded: ',
                   'failed to load Norpix sequence file', 'Norpix', 'Single']
        self.btn_norpix.clicked.connect((lambda argList: lambda: self.loadMedia(argList))(argList))
        self.hboxMov.addWidget(self.btn_norpix)
               
        self.hboxMov.addWidget(self.mov_label)
        self.hboxMov.addStretch()

    def makeAutosaveRow(self):
        settings = self.gui_data_interface.autosave_settings

        self.autosave_checkbox = QCheckBox('Enable autosave')
        self.autosave_checkbox.setToolTip(
            "Periodically save annotations in the background.\n"
            "Files are written to the autosave directory.")
        self.autosave_checkbox.setChecked(settings['enabled'])
        self.autosave_checkbox.setStyleSheet(self.labelStyle)
        self.autosave_checkbox.stateChanged.connect(self._on_autosave_enabled_changed)

        self.autosave_interval_spin = QSpinBox()
        self.autosave_interval_spin.setRange(1, 240)
        minutes = max(1, int(round(settings['interval_seconds'] / 60)))
        self.autosave_interval_spin.setValue(minutes)
        self.autosave_interval_spin.setSuffix(' min')
        self.autosave_interval_spin.valueChanged.connect(self._on_autosave_interval_changed)

        self.autosave_path_edit = QLineEdit(settings['directory'])
        self.autosave_path_edit.setReadOnly(True)
        self.autosave_path_edit.setStyleSheet('color: #ffffff')

        self.autosave_browse_button = QPushButton('Browse…')
        self.autosave_browse_button.clicked.connect(self._choose_autosave_directory)

        every_label = QLabel('every')
        every_label.setStyleSheet(self.labelStyle)
        to_label = QLabel('to')
        to_label.setStyleSheet(self.labelStyle)

        self.hboxAutosave.addWidget(self.autosave_checkbox)
        self.hboxAutosave.addWidget(every_label)
        self.hboxAutosave.addWidget(self.autosave_interval_spin)
        self.hboxAutosave.addWidget(to_label)
        self.hboxAutosave.addWidget(self.autosave_path_edit)
        self.hboxAutosave.addWidget(self.autosave_browse_button)
        self.hboxAutosave.addStretch()

        self._update_autosave_widget_state(settings['enabled'])

    def _update_autosave_widget_state(self, enabled: bool):
        self.autosave_interval_spin.setEnabled(enabled)
        self.autosave_path_edit.setEnabled(enabled)
        self.autosave_browse_button.setEnabled(enabled)

    def _on_autosave_enabled_changed(self, state):
        enabled = state == Qt.Checked
        self.gui_data_interface.autosave_settings['enabled'] = enabled
        self._update_autosave_widget_state(enabled)
        self.gui_data_interface.save_state()
        self._refresh_manual_scorer_autosave()

    def _on_autosave_interval_changed(self, value: int):
        seconds = max(60, value * 60)
        self.gui_data_interface.autosave_settings['interval_seconds'] = seconds
        self.gui_data_interface.save_state()
        self._refresh_manual_scorer_autosave()

    def _choose_autosave_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Autosave Directory',
                                                     self.gui_data_interface.autosave_settings['directory'])
        if not directory:
            return
        self.gui_data_interface.autosave_settings['directory'] = directory
        self.autosave_path_edit.setText(directory)
        self.gui_data_interface.save_state()
        self._refresh_manual_scorer_autosave()

    def _refresh_manual_scorer_autosave(self):
        scorer = self.gui_data_interface.manual_scorer
        if scorer is None:
            return
        scorer.autosave_settings = self.gui_data_interface.autosave_settings
        scorer.dio.autosave()

    def makeOverlayRow(self):
        settings = self.gui_data_interface.overlay_settings

        overlay_label = QLabel('Overlay text:')
        overlay_label.setStyleSheet(self.labelStyle)
        self.hboxOverlay.addWidget(overlay_label)

        self.overlay_dark_font_checkbox = QCheckBox('Dark font')
        self.overlay_dark_font_checkbox.setToolTip(
            "Switch overlay text between light (for dark videos)\n"
            "and dark (for bright videos).")
        self.overlay_dark_font_checkbox.setChecked(settings['dark_font'])
        self.overlay_dark_font_checkbox.setStyleSheet(self.labelStyle)
        self.overlay_dark_font_checkbox.stateChanged.connect(self._on_overlay_dark_font_changed)
        self.hboxOverlay.addWidget(self.overlay_dark_font_checkbox)

        size_label = QLabel('size:')
        size_label.setStyleSheet(self.labelStyle)
        self.hboxOverlay.addWidget(size_label)

        self.overlay_font_size_spin = QSpinBox()
        self.overlay_font_size_spin.setRange(8, 48)
        self.overlay_font_size_spin.setValue(settings['font_size'])
        self.overlay_font_size_spin.setSuffix(' px')
        self.overlay_font_size_spin.valueChanged.connect(self._on_overlay_font_size_changed)
        self.hboxOverlay.addWidget(self.overlay_font_size_spin)

        self.hboxOverlay.addStretch()

    def _on_overlay_dark_font_changed(self, state):
        self.gui_data_interface.overlay_settings['dark_font'] = state == Qt.Checked
        self.gui_data_interface.save_state()
        self._refresh_scorer_overlay_settings()

    def _on_overlay_font_size_changed(self, value: int):
        self.gui_data_interface.overlay_settings['font_size'] = value
        self.gui_data_interface.save_state()
        self._refresh_scorer_overlay_settings()

    def _refresh_scorer_overlay_settings(self):
        scorer = self.gui_data_interface.manual_scorer
        if scorer is None:
            return
        scorer.overlay_settings = dict(self.gui_data_interface.overlay_settings)

    def makeCommandoRow(self):
        # ── Step 3: Run scorer ──
        self.com_stepLabel = QLabel('Step 3  Run Scorer: ')
        self.com_stepLabel.resize(60, 40)
        self.com_stepLabel.setStyleSheet(self.labelStyle)
        self.hboxCommand.addWidget(self.com_stepLabel)

        self.com_run = QPushButton('run scorer')
        self.com_run.setToolTip("Open the scorer window to annotate the loaded video.\n"
                                "Previous annotations are restored automatically\n"
                                "from the resume file if available.")
        self.com_run.clicked.connect(self.runScorer)
        self.hboxCommand.addWidget(self.com_run)
        self.hboxCommand.addStretch()

        # ── Step 4: Export data ──
        self.export_stepLabel = QLabel('Step 4  Export: ')
        self.export_stepLabel.resize(60, 40)
        self.export_stepLabel.setStyleSheet(self.labelStyle)
        self.hboxExport.addWidget(self.export_stepLabel)

        # Data format label + combo
        fmt_label = QLabel('data format:')
        fmt_label.setStyleSheet(self.labelStyle)
        self.hboxExport.addWidget(fmt_label)

        self.modeDict = {'clear text': 'text', 'pickle': 'pickle',
                         'MatLab': 'matLab', 'MS Excel': 'xlsx'}
        self.comboBox = QComboBox(self)
        self.comboBox.addItems(self.modeDict.keys())
        self.comboBox.setCurrentIndex(0)
        self.hboxExport.addWidget(self.comboBox)

        # Export data button
        self.com_export = QPushButton('export data')
        self.com_export.setToolTip("Export ethogram data in the selected format.")
        self.com_export.clicked.connect(self.exportData)
        self.hboxExport.addWidget(self.com_export)

        # Export single frame (overlay screenshot)
        self.com_exportFrame = QPushButton('export single frame')
        self.com_exportFrame.clicked.connect(self.exportFrame)
        self.com_exportFrame.setToolTip(
            'Save a single frame with behaviour icon overlays.\n'
            'Only works while the scorer is actively running.')
        self.hboxExport.addWidget(self.com_exportFrame)

        # Export movie (overlay screenshot sequence)
        self.com_exportMovie = QPushButton('export movie')
        self.com_exportMovie.clicked.connect(self.exportMovie)
        self.com_exportMovie.setToolTip(
            'Save all frames with behaviour icon overlays.\n'
            'Only works while the scorer is actively running.')
        self.hboxExport.addWidget(self.com_exportMovie)

        self.hboxExport.addStretch()
        
    def close_event(self):        
        self.tabs.close_event()
        
    def makeBehavInfoBox(self, animal: Animal):
        behavBox = QVBoxLayout()
        nameLabel = QLabel(animal.name + ' (A' + str(animal.number)+')')
        nameLabel.setStyleSheet(self.labelStyle + "font-size: 13px;")
        behavBox.addWidget(nameLabel)
        for behav_label in sorted(animal.behaviours.keys()):
            behav = animal.behaviours[behav_label]
            hbox = QHBoxLayout()
            # colour swatch
            swatch = QLabel("  ")
            swatch.setFixedSize(14, 14)
            swatch.setStyleSheet(
                "background-color: {}; border: 1px solid #888; border-radius: 2px;".format(
                    behav.color or "#666"))
            hbox.addWidget(swatch)
            self._add_name_label(behav, hbox)
            self._add_icon(behav, hbox)
            self._add_keybinding_label(hbox, behav)
            behavBox.addLayout(hbox)

        return behavBox

    def _add_keybinding_label(
            self, hbox,
            behaviour: Behaviour
    ):
        binding = behaviour.key_bindings[
            self.gui_data_interface.selected_device
        ]
        if binding is None:
            keyLabel = QLabel('not assigned yet')
            keyLabel.setStyleSheet('color: #FFFFFF')
        else:
            keyLabel = QLabel(binding)
            keyLabel.setStyleSheet('color: #FFFFFF')
        hbox.addWidget(keyLabel)

    @staticmethod
    def _add_name_label(behav, hbox):
        behavLabel = QLabel(behav.name)
        color = behav.color or '#d4d4d4'
        behavLabel.setStyleSheet('color: {}; font-weight: bold;'.format(color))
        hbox.addWidget(behavLabel)

    @staticmethod
    def _add_icon(behav, hbox):
        icon_path = behav.icon_path
        if icon_path is not None:
            imageLabel = QLabel()
            pixmap = QPixmap(icon_path)
            pixmap = pixmap.scaledToWidth(20)
            imageLabel.setStyleSheet('color: ' + behav.color)
            imageLabel.setPixmap(pixmap)
            hbox.addWidget(imageLabel)

    def makeMovieControlInfoBox(self):
        # top label
        movieBox = QVBoxLayout()
        self._add_title(movieBox)

        for movie_action in sorted(
                self.gui_data_interface.movie_bindings.keys()
        ):
            binding = self.gui_data_interface.movie_bindings[
                movie_action].key_bindings[self.gui_data_interface.selected_device]
            tempBox = QHBoxLayout()
            behavLabel = QLabel(movie_action)
            behavLabel.setStyleSheet('color: #ffffff')
            if binding is None:
                buttonLabel = QLabel("no button assigned")
                buttonLabel.setStyleSheet('color: #C0C0C0')
            else:
                buttonLabel = QLabel(binding)
                buttonLabel.setStyleSheet('color: #ffffff')
            tempBox.addWidget(behavLabel)
            tempBox.addWidget(buttonLabel)
            movieBox.addLayout(tempBox)

        return movieBox

    def _add_title(self, movieBox):
        nameLabel = QLabel('movie actions')
        nameLabel.setStyleSheet(self.labelStyle)
        movieBox.addWidget(nameLabel)

    def resizeEvent(self, event):
        pass
    def loadMedia(self,argList):
        # build dialogue window
        dlg = QFileDialog(self)
        # if this is a single file 
        if argList[-1] == 'Single':
            dlg.setFileMode(QFileDialog.ExistingFile)
        # if we are looking for a directory of files
        else:
            dlg.setFileMode(QFileDialog.Directory)
        # set the filter                
        dlg.setNameFilters(argList[0])
        filenames = []
        # execute dialogue
        if dlg.exec_():
            filenames = dlg.selectedFiles()
        # if we are looking for a directory we also need to know the file extension
        ok = True
        if argList[-1] != 'Single':
            text, ok = QInputDialog.getText(self, 'Choose', 'Image File Extension:',text='*.jpg')
            if ok:
                filenames[0] = filenames[0]+'/'+text
        # if everything was set up correctly we save the info for later use
        if (len(filenames) > 0) and (ok is True):
            succStr = argList[1] + filenames[0]
            self.mov_label.setText(succStr)
            self.media_file_name = str(filenames[0]) # for some reason the media handler dislikes Qstrings
            self.media_type = argList[3]
        
        else:
            self.mov_label.setText(argList[2])
            
    def loadData(self):
        # load data
        filename = self.getFileName(title='Load Annotation', path=HOME, fileFilter = '*.pkl, *.pickle', mode ='load')
        if (len(filename) > 0):
            self.manual_scorer.load_data(str(filename), 'pickle')
        else:
            QMessageBox.warning(self, 'Data Loading Aborted!',
                                "Data was not loaded!",
                                QMessageBox.Ok)

    def saveData(self, irrelevant, filename='verboseMode'):
        if filename == 'verboseMode':
            filename = self.getFileName(title='Save Results', path=HOME, fileFilter = '*.txt', mode ='save')

        if filename:
            self.manual_scorer.save_data(str(filename), 'text')
            self.manual_scorer.save_data(str(filename) + '.pkl', 'pickle')
        else:
            QMessageBox.warning(self, 'Data Saving Aborted!',
                                "Data was  not saved!",
                                QMessageBox.Ok)
            
    def exportData(self, irrelevant, filename='verboseMode',):
        """Export ethogram data in the selected format."""
        if self.manual_scorer is None:
            QMessageBox.warning(self, 'No data',
                                "Run the scorer first.", QMessageBox.Ok)
            return

        mode = str(self.comboBox.currentText())
        mode_key = self.modeDict[mode]

        # Map internal mode keys to Qt filter strings and extensions
        _filter_map = {
            'text':   ("Text files (*.txt)", '.txt'),
            'pickle': ("Pickle files (*.pkl)", '.pkl'),
            'matLab': ("MATLAB files (*.mat)", '.mat'),
            'xlsx':   ("Excel files (*.xlsx)", '.xlsx'),
        }
        qt_filter, ext = _filter_map.get(mode_key, ("All files (*)", ''))

        if filename == 'verboseMode':
            filename = self.getFileName(
                title='Export Data as {}'.format(mode),
                path=HOME, fileFilter=qt_filter, mode='save')

        if filename:
            # Auto-append extension if missing
            if ext and not filename.endswith(ext):
                filename += ext
            self.manual_scorer.save_data(str(filename), mode_key)
        else:
            QMessageBox.warning(self, 'Export Aborted!',
                                "Data was not exported!",
                                QMessageBox.Ok)
                
    def exportFrame(self, irrelevant, filename='verboseMode', frameNo='verboseMode'):
        """Export a single video frame with behaviour icon overlays."""
        if self.manual_scorer is None:
            QMessageBox.warning(self, 'No scorer',
                                "Run the scorer first.", QMessageBox.Ok)
            return
        if not hasattr(self.manual_scorer, 'screen'):
            QMessageBox.warning(self, 'Not available',
                                "Frame overlay export requires the scorer window "
                                "to be open.\nRun the scorer and use this while it is running.",
                                QMessageBox.Ok)
            return
        goOn = True
        if filename == 'verboseMode':
            filename = self.getFileName(
                title='Save Frame as JPEG',
                path=HOME,
                fileFilter='JPEG images (*.jpg *.jpeg);;PNG images (*.png);;All files (*)',
                mode='save')
        if not filename:
            goOn = False
        else:
            # Auto-append .jpg if no recognised extension
            if not any(filename.lower().endswith(e) for e in ('.jpg', '.jpeg', '.png', '.bmp')):
                filename += '.jpg'
        if frameNo == 'verboseMode' and goOn:
            frameNo, ok = QInputDialog.getInt(self, 'Choose', 'Frame Number:')
            if not ok:
                goOn = False
        if goOn:
            self.manual_scorer.dio.saveOverlayImage(str(filename), frameNo)

    def exportMovie(self, irrelevant, dirname='verboseMode',
                    prefix='verboseMode', extension='verboseMode'):
        if self.manual_scorer is None:
            QMessageBox.warning(self, 'No scorer',
                                "Run the scorer first.", QMessageBox.Ok)
            return
        if not hasattr(self.manual_scorer, 'screen'):
            QMessageBox.warning(self, 'Not available',
                                "Movie overlay export requires the scorer window "
                                "to be open.\nRun the scorer and use this while it is running.",
                                QMessageBox.Ok)
            return

        # Choose format
        exts = ("mp4 (video)", "avi (video)", "png (image sequence)",
                "jpeg (image sequence)")
        ext_choice, ok = QInputDialog.getItem(
            self, "Export format", "Select output format:", exts, 0, False)
        if not ok:
            return
        extension = ext_choice.split()[0]  # "mp4", "avi", "png", or "jpeg"
        is_video = extension in ('mp4', 'avi')

        if is_video:
            # For video: pick output directory, use a default prefix
            dirname = QFileDialog.getExistingDirectory(
                self, 'Output directory', HOME)
            if not dirname:
                return
            prefix, ok = QInputDialog.getText(
                self, 'Choose', 'Video filename (without extension):',
                QLineEdit.Normal, 'scored_video')
            if not ok:
                return
        else:
            # For image sequence: pick directory and prefix
            dirname = QFileDialog.getExistingDirectory(
                self, 'Output directory for frames', HOME)
            if not dirname:
                return
            prefix, ok = QInputDialog.getText(
                self, 'Choose', 'Prefix for image files',
                QLineEdit.Normal, 'frame')
            if not ok:
                return

        QMessageBox.information(
            self, "Export started",
            "Exporting in the background.\nCheck the terminal for progress.",
            QMessageBox.Ok)
        self.manual_scorer.dio.saveOverlayMovie(dirname, prefix, extension)

    def getFileName(self, title, path, fileFilter, mode):
        """Open a file dialog with a proper filter string.

        Parameters
        ----------
        title : str
            Dialog window title.
        path : str
            Starting directory.
        fileFilter : str
            Qt-style filter, e.g. ``"Text files (*.txt)"``.
        mode : str
            ``'load'`` or ``'save'``.

        Returns
        -------
        str
            Selected file path, or ``''`` if cancelled.
        """
        if mode == 'load':
            filename, _ = QFileDialog.getOpenFileName(self, title, path, fileFilter)
        elif mode == 'save':
            filename, filt = QFileDialog.getSaveFileName(self, title, path, fileFilter)
            filename = _ensure_extension(filename, filt)
        else:
            QMessageBox.warning(self, 'Unknown mode: ' + mode,
                                "Data IO stopped, in getFileName",
                                QMessageBox.Ok)
            return ''
        return filename or ''

    def runScorer(self):
        goOn = self.checkingInputs()

        if goOn is False:
            return

        scorer = ManualEthologyScorer2(self.gui_data_interface.animals,
                                       self.gui_data_interface.movie_bindings,
                                       self.gui_data_interface.selected_device,
                                       autosave_settings=dict(self.gui_data_interface.autosave_settings),
                                       overlay_settings=dict(self.gui_data_interface.overlay_settings))
        self.gui_data_interface.manual_scorer = scorer
        self.manual_scorer = scorer

        self.gui_data_interface.save_state()

        try:
            self.manual_scorer.load_movie(self.media_file_name, self.media_type)
        except KeyError as ex:
            QMessageBox.warning(self, 'Unknown media type: ' + self.media_type,
                                "Specify a movie, an image sequence, or norpix sequence.\nError message: {}".format(ex),
                                QMessageBox.Ok)
            return

        # Run scorer in a proper thread so we can detect when it finishes
        import threading
        self._scorer_thread = threading.Thread(
            target=self.manual_scorer.go, daemon=True, name='pyvisor-scorer')
        self._scorer_thread.start()

        # Poll for scorer completion
        from PyQt5.QtCore import QTimer
        self._scorer_poll_timer = QTimer(self)
        self._scorer_poll_timer.timeout.connect(self._check_scorer_finished)
        self._scorer_poll_timer.start(500)

    def _check_scorer_finished(self):
        """Called periodically to check if the scorer thread has ended."""
        if hasattr(self, '_scorer_thread') and self._scorer_thread is not None:
            if not self._scorer_thread.is_alive():
                self._scorer_poll_timer.stop()
                self._scorer_thread = None
                self._on_scorer_finished()

    def _on_scorer_finished(self):
        """Called when the scorer window is closed. Prompt to save."""
        scorer = self.gui_data_interface.manual_scorer
        if scorer is None:
            return

        data = scorer.get_data()
        if data is False or data is None:
            return

        reply = QMessageBox.question(
            self, "Scorer session ended",
            "The scoring session has ended.\n\n"
            "A resume file has been saved next to the video\n"
            "(*.pyvisor.pkl). Your annotations will be restored\n"
            "automatically the next time you run the scorer on\n"
            "the same video.\n\n"
            "Would you like to export the data now?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.exportData(None)

    def _is_animal_behaviour(self, key: str, animal_behaviours_as_strings: List[List[str]]) -> bool:
        return self.assignment[0][key].name in chain.from_iterable(animal_behaviours_as_strings)


    def _media_file_not_specified(self):
        return (self.media_file_name == '') or (self.media_type == '')

    def checkingInputs(self) -> bool:
        goOn = True

        # check if media file info is there
        if self._media_file_not_specified():
            QMessageBox.warning(self, 'Choose media first!',
                                "You need to choose an input media file(s)!",
                                QMessageBox.Ok)
            goOn = False

        no_icons = self.gui_data_interface.get_behaviours_without_icons()
        if no_icons:
            warnmsg = "You have to assign an Icon before the analysis "
            warnmsg += "can be started.\n"
            for ni in no_icons:
                animal = self.gui_data_interface.animals[ni.animal_number]
                warnmsg += "Animal {}, behaviour {} has no Icon assigned.\n".format(
                    animal.name,
                    ni.name
                )
            QMessageBox.warning(self, "No Icon Assigned!",
                                warnmsg,
                                QMessageBox.Ok)
            goOn = False

        no_button_assigned = self.gui_data_interface.get_scorer_actions_without_buttons_assigned()
        if len(no_button_assigned) > 0:
            msg = 'These actions have no buttons assigned:\n'
            for action in no_button_assigned:
                if isinstance(action, Behaviour):
                    animal = self.gui_data_interface.animals[action.animal_number]
                    msg += "- Animal {}, behaviour {}\n".format(animal.name, action.name)
                else:
                    msg += "- MovieAction {}\n".format(action.name)

            QMessageBox.warning(self, 'Scorer actions unassigned!',
                                msg,
                                QMessageBox.Ok)
            goOn = False
        
        return goOn
