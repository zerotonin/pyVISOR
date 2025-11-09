from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
HERE = os.path.dirname(os.path.abspath(__file__))

from .icon_gallery import IconGallery
from pyvisor.resources import icon_categories


class IconSelectionWidget(QDialog):

    def __init__(self, parent, color=(0, 0, 0)):
        super(IconSelectionWidget, self).__init__()
        self.accept = False
        self.background_color = color
        self.init_ui()

    def get_current_icon(self):
        return self.w.get_current_icon()
        
    def init_ui(self):

        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.icon_categories = [str(path) for path in icon_categories()]
        self.icon_categories_button_group = QButtonGroup(self)

        self.hbox_top_panel = QHBoxLayout()
        vbox.addLayout(self.hbox_top_panel)
                             
        vbox_categories = QVBoxLayout()
        self.hbox_top_panel.addLayout(vbox_categories)
        first = False
        items_to_pop = []
        for i in range(len(self.icon_categories)):
            cat = self.icon_categories[i]
            if os.path.isdir(cat) and not cat.split('/')[-1] == 'license':
                cat_btn = QPushButton(cat.split('/')[-1])
                cat_btn.setCheckable(True)
                if not first:
                    first = True
                    cat_btn.setChecked(True)
                cat_btn.toggled.connect(self.check_category)
                vbox_categories.addWidget(cat_btn)
                self.icon_categories_button_group.addButton(cat_btn)
            else:
                items_to_pop.append(i)
        for ind in items_to_pop:
            self.icon_categories.pop(ind)
        vbox_categories.addStretch(1)

        self.w = IconGallery(self.icon_categories[
            self.icon_categories_button_group.checkedId() * -1 - 2], self.background_color)
        self.hbox_top_panel.addWidget(self.w)

        hbox_accept_cancel = QHBoxLayout()
        vbox.addLayout(hbox_accept_cancel)
        button_accept = QPushButton("accept")
        button_cancel = QPushButton("cancel")
        hbox_accept_cancel.addStretch(1)
        hbox_accept_cancel.addWidget(button_cancel)
        hbox_accept_cancel.addWidget(button_accept)

        button_cancel.clicked.connect(self.do_cancel)
        button_accept.clicked.connect(self.do_accept)

    def check_category(self, state):
        if state:
            ind = self.icon_categories_button_group.checkedId() * -1 - 2
            self.hbox_top_panel.removeWidget(self.w)
            self.w.close()
            self.w = IconGallery(self.icon_categories[ind],
                                 self.background_color)
            self.hbox_top_panel.addWidget(self.w)

    def do_cancel(self):
        self.close()

    def do_accept(self):
        self.accept = True
        self.close()
