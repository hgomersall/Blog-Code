#!/usr/bin/env python

import sys
import numpy
import PySide
from PySide import QtCore, QtOpenGL, QtGui
from PySide.QtGui import QGraphicsScene, QGraphicsView, QApplication
from PySide.QtDeclarative import QDeclarativeView

from overlay_widget_simple import OverlayWidget
from renderer_simple import Renderer

from OpenGL import GL

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
    

def main(argv):
    app = QApplication(argv)

    gl_format = QtOpenGL.QGLFormat()
    gl_format.setSampleBuffers(True)

    gl_widget = QtOpenGL.QGLWidget(gl_format)
    
    view = GraphicsView()

    view.setViewport(gl_widget)
    view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
    
    scene = OpenGLScene()

    overlay_widget = OverlayWidget()     
    scene.addWidget(overlay_widget)

    overlay_widget.move(QtCore.QPoint(0,0))
    overlay_widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    
    view.setScene(scene)
    print view.children()
    view.show()
    
    view.resize(800,600)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)

