from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from . import styles
import os
HERE = os.path.dirname(os.path.abspath(__file__))

import numpy as np

## paths to background images
DEVICES = {"Keyboard": HERE + "/pictures/gamePad_KB.png", 
           "Playstation": HERE + "/pictures/gamePad_PS.png",
           "X-Box": HERE + "/pictures/gamePad_XB.png"}

## temporary polygons, remove before release ...
_tmp_polygons = [[(0.0, 0.0),   # ----------
                  (0.1, 0.1),   # central line left/top - right/bottom
                  (0.2, 0.2),
                  (0.3, 0.3),
                  (0.4, 0.4),
                  (0.99, 0.99)],  # ---------
                 [(.9999, 0.0001),  # --------- central line left/bottom - right/top
                  (0.0001, .9999)], ]

## Relative coordinates of polygons 
POLYGONS = { "Keyboard" : [],
             "X-Box" : [],  # ---------
             "Playstation" : [[(0.165, 0.481),    # ---------
                               (0.185, 0.481),   # cross left
                               (0.20, 0.461),   
                               (0.185, 0.441), 
                               (0.165, 0.441)],
                              [(0.255, 0.481),    # ---------
                               (0.235, 0.481),   # cross right
                               (0.22, 0.461),   
                               (0.235, 0.441), 
                               (0.255, 0.441)],
                              [(0.197, 0.395),    # ---------
                               (0.197, 0.426),   # cross up
                               (0.211, 0.441),   
                               (0.225, 0.426), 
                               (0.225, 0.395)],
                              [(0.197, 0.531),    # ---------
                               (0.197, 0.5),   # cross down
                               (0.211, 0.485),   
                               (0.225, 0.5), 
                               (0.225, 0.531)],
                              [(0.33, 0.45),              # -----------
                               (0.338, 0.45),              # select button
                               (0.338, 0.441),
                               (0.33, 0.441)], 
                              [(0.38, 0.439),              # -----------
                               (0.38, 0.452),              # start button
                               (0.388, 0.455)], 
                              [(0.185, 0.2),              # -----------
                               (0.255, 0.2),              # L1 button
                               (0.255, 0.185),
                               (0.185, 0.185)], 
                              [(0.188, 0.183),              # -----------
                               (0.258, 0.183),              # L2 button
                               (0.258, 0.168),
                               (0.188, 0.168)],
                              [(0.465, 0.2),              # -----------
                               (0.535, 0.2),              # R1 button
                               (0.535, 0.185),
                               (0.465, 0.185)], 
                              [(0.462, 0.183),              # -----------
                               (0.532, 0.183),              # R2 button
                               (0.532, 0.168),
                               (0.462, 0.168)], ]}

## Relative Coordinates/sizes of Ellipses
ELLIPSES = {"Keyboard": [],
            "X-Box": [],
            "Playstation": [[0.251, 0.521, 0.075, 0.115],  # left stick
                            [0.413, 0.521, 0.075, 0.115],  # right stick
                            [0.455, 0.511, 0.02, 0.025],  # right button element left button
                            [0.475, 0.53, 0.02, 0.025],  # right button element bottom button
                            [0.5, 0.511, 0.02, 0.025],  # right button element right button
                            [0.475, 0.492, 0.02, 0.025]]}

## Pen and brush items for different states
PEN_NORMAL = QPen( Qt.black )

BRUSH_NORMAL = QBrush( Qt.NoBrush )

PEN_HIGHLIGHT = QPen( Qt.green )
PEN_HIGHLIGHT.setWidth( 4.5 )
    
BRUSH_HIGHLIGHT = QBrush( Qt.Dense3Pattern )
BRUSH_HIGHLIGHT.setColor( Qt.green )


class TabButtons(QWidget):

    def __init__(self,parent):
        

        self.analysis_list = [] 

        super(TabButtons,self).__init__()
        self.parent=parent
        self.selected_device='Playstation'
        self.init_UI()





    def init_UI(self):
        
        # ===========================
        # style sheet 
        # ===========================
        self.setStyleSheet(styles.tab_buttons)
        
        # ===========================
        # background image 
        # ===========================
        self.background_image = QLabel(self)
        self.background_image.setGeometry(0, 0, self.parent.height(), self.parent.width())
        self.pixmap=QPixmap(HERE+'/pictures/gamePad.png')
        self.background_image.setPixmap(self.pixmap.scaled(self.background_image.size(),Qt.KeepAspectRatio))
        self.background_image.setScaledContents(True)
        
        self.background_image.resize(self.size())


        # ===========================
        # Scene/View to draw on
        # ===========================
        
        self.scenes = {}

        for key in POLYGONS.keys():
            self.scenes[key] = QGraphicsScene(self)
            
        self.view = OverlayView( self.scenes[self.selected_device], self )
        self.view.show()

        
        # ===========================
        # combo box top
        # ===========================

        #vbox=QVBoxLayout()
        #lbl=QLabel('yo')
        #vbox.addWidget(lbl)
        #self.setLayout(vbox)
        #hbox_row_0 = QHBoxLayout()
        #vbox.addLayout(hbox_row_0)
        
        #hbox_row_0.addStretch(0)
        
        self.lbl_input_device = QLabel("select device layout ",self)
        #self.lbl_input_device.setStyleSheet("color: #AA0000")
        self.combo_input_device = QComboBox(self)
        for device in DEVICES.keys():
            self.combo_input_device.addItem(device)
        self.combo_input_device.activated[str].connect(self.set_device)
        
        s=self.size()

        self.lbl_input_device.move(int(s.width()*0.25),int(s.height()*0.15))
        self.combo_input_device.move(int(s.width()*0.5),int(s.height()*0.15))

        #hbox_row_0.addWidget(lbl_input_device)
        #hbox_row_0.addWidget(combo_input_device)

        #vbox.addStretch(1)


        ## create points for polygons:
        
        self.points = {}
        self.polygons = {}

        for key in POLYGONS.keys():


            self.points[key] = [ [QPointF() for xy in POLYGONS[key][i]] for i in range(len(POLYGONS[key]))]

            self.points[key] = self.points[key] + [[QPointF() for xy in _tmp_polygons[i]] for i in range(len(_tmp_polygons))]

            #self.polygons[key] = [Polygon( scene = self.scenes[key] ) for i in range( len(POLYGONS[key]))]
            self.polygons[key] = [Polygon() for i in range( len(POLYGONS[key]))]
            #self.polygons[key] = self.polygons[key] + [QGraphicsPolygonItem( scene = self.scenes[key] ) for i in _tmp_polygons]
            self.polygons[key] = self.polygons[key] + [QGraphicsPolygonItem() for i in _tmp_polygons]

            for item in self.polygons[key]:
                self.scenes[key].addItem(item)

        ## add ellipses

        self.ellipses = {}

        for key in ELLIPSES.keys():
            
            E = [Ellipse(*(item+[self])) for item in ELLIPSES[key]]

            self.ellipses[key] = E

            for e in E:

                self.scenes[key].addItem(e)

        ## first try: left joy-stick ellipse playstation
        #self.scenes['Playstation'].addEllipse(QRectF(200,200,100,100))


        self.update_polygons(self.background_image.size())

        self.view.show()


        # ---------------------------
        # Right column: button editor
        # ---------------------------

        self.button_editor = ButtonEditor(self)
        s = self.size()
        self.button_editor.setGeometry(int(s.width()*0.8),0, int(s.width()*0.199),s.height())

    def _print_msg(self, msg):
        print(str(msg))

    def resizeEvent(self, event):
        self.background_image.resize(event.size())
        #self.background_image.setPixmap(self.pixmap.scaled(self.background_image.size(),Qt.KeepAspectRatio))
        self.view.resize(event.size())
    
        self.update_polygons(self.background_image.size())

        s = self.background_image.size()

        self.lbl_input_device.move(int(s.width()*0.2),int(s.height()*0.06))
        self.combo_input_device.move(int(s.width()*0.39),int(s.height()*0.06))

        self.button_editor.resize(event.size())

    def update_polygons( self, size ):

        ind = 0
        for j in range(len(POLYGONS[self.selected_device])):
        #for j in range(POLYGONS[self.selected_device])):

            for i in range(len(POLYGONS[self.selected_device][j])):
                v = POLYGONS[self.selected_device][j][i]
                p = self.points[self.selected_device][j][i]
                p.setX( size.width() * v[0] )
                p.setY( size.height() * v[1] )

            #self.analysis_list.append([(size.width(),size.height()), v, (p.x(),p.y())]) 

            #print p.x(), p.y()
            self.polygons[self.selected_device][j].setPolygon( QPolygonF(self.points[self.selected_device][j]) )
            ind += 1


        for k in range(len(_tmp_polygons)):
            
            for i in range(len(_tmp_polygons[k])):

                v = _tmp_polygons[k][i]

                p = self.points[self.selected_device][ind+k][i]
                p.setX( size.width() * v[0] )
                p.setY( size.height() * v[1] )

            self.polygons[self.selected_device][ind+k].setPolygon( QPolygonF(self.points[self.selected_device][ind+k]) )
            self.polygons[self.selected_device][ind+k].setAcceptHoverEvents(True)


        for e in range(len(self.ellipses[self.selected_device])):
            rel = ELLIPSES[self.selected_device][e] # relative ellipse coordinates
            self.ellipses[self.selected_device][e].setRect(size.width()*rel[0],size.height()*rel[1],size.width()*rel[2],size.height()*rel[3])
            
        self.scenes[self.selected_device].setSceneRect(0,0, self.background_image.size().width()*0.98,self.background_image.size().height()*0.98)
        self.view.setScene( self.scenes[self.selected_device] )
        self.view.show()            

    def set_device(self, device):
        
        self.pixmap=QPixmap(DEVICES[str(device)])
        self.background_image.setPixmap(self.pixmap.scaled(self.background_image.size(),Qt.KeepAspectRatio))
        self.background_image.setScaledContents(True)

        self.selected_device = str(device)

        self.update_polygons(self.background_image.size())

    def close_event(self):

        a = np.zeros( (len(self.analysis_list),6) )

        for i in range(a.shape[0]):
            
            for j in range(6):
                
                a[i,j] = self.analysis_list[i][j/2][j%2]

        np.save("ana.npy",a)


    '''
    def paintEvent(self, event):

        print self.view

        
        for item in self.scenes[self.selected_device].items():
            if isinstance( item, Ellipse):
                item.paint( self.view)

        
        super(TabButtons, self).paintEvent(event)
        ## Problem: this seems to call paint() for all items again, 
        ##          and now it passes too few arguments to Ellipse.paint() ...
    '''

class OverlayView(QGraphicsView):

    def __init__(self, scene, parent):

        super(OverlayView,self).__init__( scene, parent )



class Polygon(QGraphicsPolygonItem):

    def __init__(self, scene = None):
        
        #super(Polygon, self).__init__() #scene = scene )

        QGraphicsPolygonItem.__init__(self, scene = scene)

        self.pen_normal = self.pen()
        self.brush_normal = self.brush()

        self.pen_highlight = QPen( Qt.green )
        self.pen_highlight.setWidth( 4.5 )

        self.brush_highlight = QBrush( Qt.Dense3Pattern )
        self.brush_highlight.setColor( Qt.green )

        self.pen_selected = QPen( Qt.white )
        self.pen_selected.setWidth( 4.5 )

        self.brush_selected = QBrush( Qt.Dense1Pattern )
        self.brush_selected.setColor( Qt.white )

        self.setAcceptHoverEvents(True)

        self.selected = False
        self.hovered = False


    def update_pen_and_brush(self):

        if self.hovered:
            self.setPen( self.pen_highlight )
            self.setBrush( self.brush_highlight )

        else:
            if self.selected:
                self.setPen( self.pen_selected )
                self.setBrush( self.brush_selected )

            else:
                self.setPen( self.pen_normal )
                self.setBrush( self.brush_normal )

                

    def hoverEnterEvent(self, event):

        self.hovered = True
        self.update_pen_and_brush()

    def hoverLeaveEvent(self, event):

        self.hovered = False
        self.update_pen_and_brush()

    def mousePressEvent(self, event):
    
        if self.selected:
            self.selected = False
        else:
            self.selected = True
        self.update_pen_and_brush()


class Ellipse(QGraphicsEllipseItem):

    def __init__(self, x, y , width, height, parent = None):

        QGraphicsEllipseItem.__init__(self)
        
        self.parent = parent # should be a reference to a TabButtons object

        self.relative_rect = [x, y, width, height]

        #self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.setAcceptHoverEvents(True)

        self.pen_normal = self.pen()
        self.brush_normal = self.brush()

        self.pen_highlight = QPen( Qt.green )
        self.pen_highlight.setWidth( 4.5 )
    
        self.brush_highlight = QBrush( Qt.Dense3Pattern )
        self.brush_highlight.setColor( Qt.green )

        self.pen_selected = QPen( Qt.white )
        self.pen_selected.setWidth( 4.5 )

        self.brush_selected = QBrush( Qt.Dense1Pattern )
        self.brush_selected.setColor( Qt.white )

        self.selected = False
        self.hovered = False


    def set_position(self, size):

        w = size.width()
        h = size.height()

        x = self.relative_rect[0] * w
        y = self.relative_rect[1] * h
        width = self.relative_rect[2] * w
        height = self.relative_rect[3] * h

        self.setRect( QRectF(x, y, width, height) )


    def hoverEnterEvent(self, event):
        
        #print "yeah HOVER HOVER!!"

        self.hovered = True
        self.update_pen_and_brush()

    def hoverLeaveEvent(self, event):

        #print "no HOVER for you!"

        self.hovered = False
        self.update_pen_and_brush()

    def mousePressEvent(self, event):
    
        if self.selected:
            self.selected = False
        else:
            self.selected = True
        self.update_pen_and_brush()


    def update_pen_and_brush(self):

        if self.hovered:
            self.setPen( self.pen_highlight )
            self.setBrush( self.brush_highlight )

        else:
            if self.selected:
                self.setPen( self.pen_selected )
                self.setBrush( self.brush_selected )

            else:
                self.setPen( self.pen_normal )
                self.setBrush( self.brush_normal )



class ButtonEditor(QWidget):

    def __init__(self, parent):
        
        self.parent = parent
        super(ButtonEditor,self).__init__(parent)

        print(self.parent)

        self.init_UI()

    def init_UI(self):

        self.setStyleSheet("background-color: #AA0000;")

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)


    def add_edit_line(self, initial = None):
        pass
        #new_edit_line = ButtonEditLine(self.parent.parent.tab_list[0].)


class ButtonEditLine(QWidget):

    def __init__(self, animals_and_behaviuors, init_tuple = None):

        super(ButtonEditLine,self).__init__()

        self.animals_and_behaviuors = animals_and_behaviuors

        self.init_UI(init_tuple)




    def init_UI(self, init_tuple):

        hbox = QHBoxLayout()
        self.setLayout(hbox)

        self.combo_animal = QComboBox()

        for animal in animals_and_behaviuors:
            self.combo_animal.addItem(animal)

        self.combo_behaviour = QComboBox()

        hbox.addWidget(self.combo_animal)
        hbox.addWidget(self.combo_behaviour)
