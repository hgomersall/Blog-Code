#!/usr/bin/env python

import sys, math
import numpy
import PySide
from PySide import QtCore, QtOpenGL, QtGui
from PySide.QtCore import QUrl
from PySide.QtGui import QGraphicsScene, QGraphicsView, QApplication
from PySide.QtDeclarative import QDeclarativeView
from PySide.QtOpenGL import QGLShader, QGLShaderProgram

try:
    from OpenGL import GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)

class VertexList():

    def __init__(self):
        self._vertex_list = []
        self._colour_list = []
        self.current_colour = (0.0, 0.0, 0.0, 0.0)

    def change_colour(self, r, g, b, a):
        self.current_colour = (r, g, b, a)
        return
    
    def glBegin(self, glmode):
        self._vertex_list = []
        self._colour_list = []
        self.vertex_list = numpy.array(self._vertex_list, 'float32')
        self.colour_list = numpy.array(self._colour_list, 'float32')
        self.glmode = glmode
    
    def glEnd(self):
        self.vertex_list = numpy.array(self._vertex_list, 'float32')
        self.colour_list = numpy.array(self._colour_list, 'float32')
        return self.vertex_list

    def glVertex3d(self, x, y, z):
        self._vertex_list.extend(numpy.float32([x, y, z]))
        self._colour_list.extend(numpy.float32(self.current_colour))
    
    def glColor4f(self, r, g, b, a):
        self.change_colour(r, g, b, a)
    
    def render(self):
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        GL.glColorPointer(4, GL.GL_FLOAT, 0, self.colour_list)
        GL.glVertexPointer(3, GL.GL_FLOAT, 0, self.vertex_list)
        GL.glDrawArrays(self.glmode, 0, len(self.vertex_list)/3)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_COLOR_ARRAY)


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

class OverlayWidget(QtGui.QWidget):
    
    change_signal = QtCore.Signal(tuple)
    x_rotation_changed = QtCore.Signal('double')
    y_rotation_changed = QtCore.Signal('double')
    z_rotation_changed = QtCore.Signal('double')
    

    def __init__(self, *args):
        super(OverlayWidget, self).__init__(*args)
        
        # We need to set the base colour of the qml widget to be transparent.
        # This is done by setting its palette.
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Base, QtCore.Qt.transparent)

        qml_view = QDeclarativeView(self)
        qml_view.setPalette(palette)

        qml_context = qml_view.rootContext()
        qml_context.setContextProperty("slider_handler", self)

        url = QUrl('control_slides.qml')
        qml_view.setSource(url)

        qml_root = qml_view.rootObject()
        self.x_rotation_changed.connect(qml_root.x_rotation_changed)
        self.y_rotation_changed.connect(qml_root.y_rotation_changed)
        self.z_rotation_changed.connect(qml_root.z_rotation_changed)

        return

    def handle_foo(self, val):
        print val

    @QtCore.Slot('double')
    def x_slider_changed(self, val):
        self.change_signal.emit(('x', val))

    @QtCore.Slot('double')
    def y_slider_changed(self, val):
        self.change_signal.emit(('y', val))

    @QtCore.Slot('double')
    def z_slider_changed(self, val):
        self.change_signal.emit(('z', val))

    def rotation_changed(self, angle_tuple):
        self.x_rotation_changed.emit(angle_tuple[0])
        self.y_rotation_changed.emit(angle_tuple[1])
        self.z_rotation_changed.emit(angle_tuple[2])
        pass
        

class OpenGLScene(QGraphicsScene):
    
    sliders_changed = QtCore.Signal(tuple)
    rotation_changed = QtCore.Signal(tuple)

    def __init__(self, *args):
        super(OpenGLScene, self).__init__(*args)

        self.model = Model(self)

        self.sliders_changed.connect(self.model.changeRotation)
        
        return

    def drawBackground(self, painter, rect):

        if not painter.paintEngine().type() == QtGui.QPaintEngine.OpenGL:
            QtCore.qWarning('OpenGLScene: drawBackground needs a QGLWidget '\
                        +'to be set as viewport on the '\
                        +'graphics view')
            return

        painter.beginNativePainting()
        
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()

        self.model.render()
        
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPopMatrix()
     
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPopMatrix()

        painter.endNativePainting()
    
    def mouseMoveEvent(self, event):

        QGraphicsScene.mouseMoveEvent(self, event)
        if event.isAccepted():
            return

        if (event.buttons() & QtCore.Qt.LeftButton):
            delta = event.scenePos() - event.lastScenePos()
            self.model.setXRotation(self.model.xRotation() - delta.y()*4)
            self.model.setYRotation(self.model.yRotation() + delta.x()*4)
        
        event.accept()
        self.update()


class Model(object):
    
    def __init__(self, parent):
        
        self.parent = parent
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        
        self.trolltechGreen = QtGui.QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.trolltechPurple = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)

        self.threed_object = VertexList()
        self.makeObject()
        self.number = 1

    def xRotation(self):
        return self.xRot

    def yRotation(self):
        return self.yRot

    def zRotation(self):
        return self.zRot

    def changeRotation(self, angle_tuple):
        if angle_tuple[0] == 'x':
            self.setXRotation(angle_tuple[1])
        elif angle_tuple[0] == 'y':
            self.setYRotation(angle_tuple[1])
        elif angle_tuple[0] == 'z':
            self.setZRotation(angle_tuple[1])
        
        return

    def rotationChanged(self):
        self.parent.rotation_changed.emit((self.xRot, self.yRot, self.zRot))
        self.parent.update()

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.rotationChanged()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.rotationChanged()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.rotationChanged()
    
    def render(self):
        viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]
        
        # Render the widget using a separate viewport
        side = min(width, height)
        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)

        GL.glClearColor(*self.trolltechPurple.darker().getRgbF())
        GL.glShadeModel(GL.GL_FLAT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        #GL.glEnable(GL.GL_CULL_FACE)
        
        GL.glTranslatef(0.0, 0.0, -10.0)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glTranslated(0.0, 0.0, -10.0)

        GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        
        self.threed_object.render()
        
        # reset the viewport
        GL.glViewport(*viewport)

    def makeObject(self):
        self.threed_object.glBegin(GL.GL_QUADS)

        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22


        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
        self.quad(x3, y3, x4, y4, y4, x4, y3, x3)

        self.extrude(x1, y1, x2, y2)
        self.extrude(x2, y2, y2, x2)
        self.extrude(y2, x2, y1, x1)
        self.extrude(y1, x1, x1, y1)
        self.extrude(x3, y3, x4, y4)
        self.extrude(x4, y4, y4, x4)
        self.extrude(y4, x4, y3, x3)

        Pi = 3.14159265358979323846
        NumSectors = 200

        for i in range(NumSectors):
            angle1 = (i * 2 * Pi) / NumSectors
            x5 = 0.30 * math.sin(angle1)
            y5 = 0.30 * math.cos(angle1)
            x6 = 0.20 * math.sin(angle1)
            y6 = 0.20 * math.cos(angle1)

            angle2 = ((i + 1) * 2 * Pi) / NumSectors
            x7 = 0.20 * math.sin(angle2)
            y7 = 0.20 * math.cos(angle2)
            x8 = 0.30 * math.sin(angle2)
            y8 = 0.30 * math.cos(angle2)
            
            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

            self.extrude(x6, y6, x7, y7)
            self.extrude(x8, y8, x5, y5)

        self.threed_object.glEnd()

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.threed_object.glColor4f(*self.trolltechGreen.getRgbF())

        self.threed_object.glVertex3d(x1, y1, -0.05)
        self.threed_object.glVertex3d(x2, y2, -0.05)
        self.threed_object.glVertex3d(x3, y3, -0.05)
        self.threed_object.glVertex3d(x4, y4, -0.05)

        self.threed_object.glVertex3d(x4, y4, +0.05)
        self.threed_object.glVertex3d(x3, y3, +0.05)
        self.threed_object.glVertex3d(x2, y2, +0.05)
        self.threed_object.glVertex3d(x1, y1, +0.05)

    def extrude(self, x1, y1, x2, y2):
        self.threed_object.glColor4f(*self.trolltechGreen.darker(250 + int(100 * x1)).getRgbF())

        self.threed_object.glVertex3d(x1, y1, +0.05)
        self.threed_object.glVertex3d(x2, y2, +0.05)
        self.threed_object.glVertex3d(x2, y2, -0.05)
        self.threed_object.glVertex3d(x1, y1, -0.05)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle
    
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

    overlay_widget.change_signal.connect(scene.sliders_changed)
    scene.rotation_changed.connect(overlay_widget.rotation_changed)

    overlay_widget.move(QtCore.QPoint(0,0))
    overlay_widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    
    view.setScene(scene)
    view.show()
    
    view.resize(1024,768)
    scene.model.setXRotation(45*16)


    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)
