from PyQt5.QtWidgets import QApplication
import os
import glob
from pyvisor.GUI.main_gui import MovScoreGUI
HOME = os.path.expanduser("~")


def delete_files_from_folder(folder_path):
    files = glob.glob(folder_path + "/*")
    for f in files:
        if os.path.isdir(f):
            delete_files_from_folder(f)
            continue
        os.remove(f)

        
def empty_tmp_icon_folder():
    delete_files_from_folder(HOME + '/.pyvisor/.tmp_icons')

        
def main():
    import sys
    app = QApplication(sys.argv)
    gui = MovScoreGUI()
    gui.show()

    import os
    if not os.path.isdir(HOME + '/.pyvisor'):
        os.makedirs(HOME + '/.pyvisor')
    if not os.path.isdir(HOME + '/.pyvisor/.tmp_icons'):
        os.makedirs(HOME + '/.pyvisor/.tmp_icons')
    code = app.exec_()
    empty_tmp_icon_folder()
    sys.exit(code)


if __name__ == "__main__":
    main()
