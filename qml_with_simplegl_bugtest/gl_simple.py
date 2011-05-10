#!/usr/bin/env python

import sys

# Commenting out numpy causes the hang (despite
# numpy not being used anywhere in this module)
import numpy

import PySide
from PySide import QtCore, QtOpenGL, QtGui
from PySide.QtGui import QGraphicsScene, QGraphicsView, QApplication
from PySide.QtDeclarative import QDeclarativeView

from overlay_widget_simple import OverlayWidget
from renderer_simple import Renderer

from OpenGL import GL

# Importing numpy *after* GL is not sufficient, it 
# needs to be done before.
#import numpy

class GraphicsView(QGraphicsView):

    def __init__(self, *args):

        super(GraphicsView, self).__init__(*args)

        self.setWindowTitle('QML on OpenGL Test Program')
        return

    def resizeEvent(self, event):
        scene = self.scene()
        if scene:
            new_rect = QtCore.QRect(QtCore.QPoint(0,0), event.size())
            scene.setSceneRect(new_rect)

        QGraphicsView.resizeEvent(self,event)

class OpenGLScene(QGraphicsScene):
    
    sliders_changed = QtCore.Signal(tuple)
    rotation_changed = QtCore.Signal(tuple)

    def __init__(self, *args):
        super(OpenGLScene, self).__init__(*args)

        self.renderer = Renderer(self, GL)

        self.initialised = False
        self.image = None

        return
    
    def drawBackground(self, painter, rect):
        
        if not (painter.paintEngine().type() == QtGui.QPaintEngine.OpenGL or
            painter.paintEngine().type() == QtGui.QPaintEngine.OpenGL2):
            QtCore.qWarning('OpenGLScene: drawBackground needs a QGLWidget '\
                        +'to be set as viewport on the '\
                        +'graphics view')
            return

        painter.beginNativePainting()
        
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()
        
        self.renderer.render()
        
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPopMatrix()
     
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPopMatrix()

        painter.endNativePainting()
    
class DisplayWidget(QtGui.QWidget):

    def __init__(self, *args, **kwargs):


        super(DisplayWidget, self).__init__(*args, **kwargs)

        # We draw to an OpenGL scene, so instantiate
        # the QGLWidget.
        gl_format = QtOpenGL.QGLFormat()
        gl_format.setSampleBuffers(True)

        self.gl_widget = QtOpenGL.QGLWidget(gl_format)

        # Set up the view
        self.view = GraphicsView()
        self.view.setViewport(self.gl_widget)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Set up the scene
        self.scene = OpenGLScene()
        
        # Add the controls to it
        self.overlay_widget = OverlayWidget()
        self.scene.addWidget(self.overlay_widget)

        self.overlay_widget.move(QtCore.QPoint(0,0))
        self.overlay_widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Assign in the scene to the view.
        self.view.setScene(self.scene)

        #self.view.show()
        #self.view.resize(800,600)
        
        # Set the scene and view to be a child of this class
        self.view.setParent(self)
        self.scene.setParent(self)

    def resizeEvent(self, event):
        ''' Called when the widget is resized
        '''
        # Call the view resize method
        self.view.resize(event.size())

def main(argv):
    app = QApplication(argv)

    widget = DisplayWidget()
    widget.show()
    widget.resize(800,600)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)

