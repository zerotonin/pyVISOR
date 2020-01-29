from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os, sys, glob
from pymovscore.GUI.main_gui import MovScoreGUI

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
sys.path.append(HERE + "/..")



def delete_files_from_folder(folder_path):
    files = glob.glob(folder_path + "/*")
    for f in files:
        if os.path.isdir(f):
            delete_files_from_folder(f)
            continue
        os.remove(f)
        
def empty_tmp_icon_folder():
    delete_files_from_folder(HOME + '/.pymovscore/.tmp_icons')

        
def main():
    import sys
    app = QApplication(sys.argv)
    gui = MovScoreGUI()
    gui.show()

    import os
    if not os.path.isdir(HOME + '/.pymovscore'):
        os.makedirs(HOME + '/.pymovscore')
    if not os.path.isdir(HOME + '/.pymovscore/.tmp_icons'):
        os.makedirs(HOME + '/.pymovscore/.tmp_icons')
    code = app.exec_()
    empty_tmp_icon_folder()
    sys.exit(code)


if __name__ == "__main__":
    main()
