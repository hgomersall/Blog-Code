#!/usr/bin/env python

import sys
import PySide
from PySide import QtCore, QtOpenGL, QtGui
from PySide.QtCore import QUrl
from PySide.QtGui import QGraphicsScene, QGraphicsView, QApplication
from PySide.QtDeclarative import QDeclarativeView

try:
    from OpenGL import GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "Drawer test",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)


class GraphicsView(QGraphicsView):

    def __init__(self, *args):

        super(GraphicsView, self).__init__(*args)

        self.setWindowTitle('QML on OpenGL Test Program')
        self.setStyleSheet('QGraphicsView { border-style: none; }')
        return

    def resizeEvent(self, event):
        
        scene = self.scene()
        if scene:
            new_rect = QtCore.QRect(QtCore.QPoint(0,0), event.size())
            scene.setSceneRect(new_rect)

        QGraphicsView.resizeEvent(self,event)

class OverlayWidget(QtGui.QWidget):
    
    def __init__(self, *args):
        super(OverlayWidget, self).__init__(*args)
        
        # Set this widget itself to be transparent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # We need to set the base colour of the qml widget to be transparent.
        # This is done by setting its palette.
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Base, QtCore.Qt.transparent)

        self.setPalette(palette)
        
        
        self.qml_view = QDeclarativeView(self)
        self.qml_view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        self.qml_view.setPalette(palette)
        self.qml_view.setResizeMode(QDeclarativeView.SizeRootObjectToView)

        url = QUrl('dynamic_drawers.qml')
        self.qml_view.setSource(url)
    
    def resizeEvent(self, event):
        self.qml_view.resize(event.size())

class OpenGLScene(QGraphicsScene):
    
    def __init__(self, *args):
        super(OpenGLScene, self).__init__(*args)

        return

    def drawBackground(self, painter, rect):
        
        if not painter.paintEngine().type() == QtGui.QPaintEngine.OpenGL2:
            print painter.paintEngine().type()
            QtCore.qWarning('OpenGLScene: drawBackground needs a QGLWidget '\
                        +'to be set as viewport on the '\
                        +'graphics view')
            return

        painter.beginNativePainting()
        
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()

        GL.glClearColor(1.0,1.0,1.0,1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        # OpenGL stuff goes here...
        
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
        gl_format.setDepth(False)

        self.gl_widget = QtOpenGL.QGLWidget(gl_format)

        # Set up the view
        self.view = GraphicsView()
        self.view.setViewport(self.gl_widget)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Set up the scene
        self.scene = OpenGLScene()
        
        self.overlay_widget = OverlayWidget()     
        self.scene.addWidget(self.overlay_widget)

        self.overlay_widget.move(QtCore.QPoint(0,0))
        
        # Assign in the scene to the view.
        self.view.setScene(self.scene)

        # Set the scene and view to be a child of this class
        self.view.setParent(self)
        self.scene.setParent(self)
    
    def resizeEvent(self, event):
        ''' Called when the widget is resized
        '''
        # Call the view resize method
        self.view.resize(event.size())
        self.overlay_widget.resize(event.size())
    

def main(argv):
    app = QApplication(argv)
    
    display_widget = DisplayWidget()
    display_widget.show()
    display_widget.resize(640,480)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)
