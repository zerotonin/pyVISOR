from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
sys.path.append(HERE + "/../..")

from pymovscore.GUI.icon_gallery.icon_selection_widget import IconSelectionWidget

app = QApplication(sys.argv)
gui = IconSelectionWidget(None)
gui.show()

if not os.path.isdir(HOME + '/.pymovscore/.tmp_icons'):
    os.makedirs(HOME + '/.pymovscore/.tmp_icons')

sys.exit(app.exec_())
#app.exec_()
#for ic in gui.ICONS_TO_DELETE:
#delete_tmp_icon(ic)
#sys.exit(0)
