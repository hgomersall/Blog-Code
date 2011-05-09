#!/usr/bin/env python

#from OpenGL import GL
from PySide import QtGui

class Renderer(object):
    
    def __init__(self, parent, gl_class):
        
        self.parent = parent

        self.gl_class = gl_class

    def render(self):
        
        self.gl_class.glMatrixMode(self.gl_class.GL_PROJECTION)
        self.gl_class.glLoadIdentity()
        self.gl_class.glMatrixMode(self.gl_class.GL_MODELVIEW)
        
        self.gl_class.glClearColor(0.0,0.0,0.0,0.0)
        self.gl_class.glClear(self.gl_class.GL_COLOR_BUFFER_BIT | self.gl_class.GL_DEPTH_BUFFER_BIT)
        self.gl_class.glLoadIdentity()
        self.gl_class.glTranslated(0.0, 0.0, 0.0)

        self.gl_class.glBegin(self.gl_class.GL_TRIANGLES)
        self.gl_class.glColor(1.0, 0.0, 0.0, 0.0)
        self.gl_class.glVertex3d(0, 1, 0)
        self.gl_class.glVertex3d(1, -1, 0)
        self.gl_class.glVertex3d(-1, -1, 0)
        self.gl_class.glEnd()
        
