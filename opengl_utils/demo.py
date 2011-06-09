#!/usr/bin/env python

import numpy
from PySide import QtCore, QtGui
from PySide.QtOpenGL import QGLShader, QGLShaderProgram, QGLWidget
from OpenGL import GL
from opengl_utils import TextureStream2D
import sys
import Image

vertex_shader_code = '''
attribute highp vec4 vertex;

void main(void)
{
    gl_TexCoord[0] = gl_Vertex;
    gl_Position = gl_Vertex;
}
'''

frag_shader_code = '''
uniform sampler2D image;

void main(void)
{   
    const vec2 offset = vec2 (0.5, 0.5);
    gl_FragColor = texture2D(image, gl_TexCoord[0].st + offset);
}
'''

class GLWidget(QGLWidget):

    __QUAD_VERTICES = numpy.array((
        (-0.5, +0.5, 0.0),
        (-0.5, -0.5, 0.0),
        (+0.5, -0.5, 0.0),
        (+0.5, +0.5, 0.0)), 'float32')
    
    def __init__(self, *args):
        super(GLWidget, self).__init__(*args)
        
        self.load_images()
        self.texture_streamnks = None
        self.cur_image = 0

    def initializeGL(self):
        self.vertex_shader = QGLShader(QGLShader.Vertex)
        self.vertex_shader.compileSourceCode(vertex_shader_code)

        self.fragment_shader = QGLShader(QGLShader.Fragment)
        self.fragment_shader.compileSourceCode(frag_shader_code)
        
        self.program = QGLShaderProgram()
        self.program.addShader(self.vertex_shader)
        self.program.addShader(self.fragment_shader)

        self.program.link()
        
        self.texture_location = self.program.uniformLocation('image')
        self.offset = self.program.uniformLocation('image')

        # Set up the texture stream
        # Arguments are (size, gl_format, gl_type, gl_internal_format)
        self.texture_stream = \
                TextureStream2D((512,512), GL.GL_RGBA, 
                        GL.GL_UNSIGNED_BYTE, GL.GL_RGBA)
        
        self.switch_image()

        GL.glClearColor(0.0,0.0,0.0,0.0)
    
    def load_images(self):
        im = Image.open('test.jpg').tostring("raw", "RGBX", 0, -1)
        self.image1 =\
                numpy.frombuffer(buffer(im), dtype='uint8').reshape(512,512,4)
        im = Image.open('test2.jpg').tostring("raw", "RGBX", 0, -1)
        self.image2 = \
                numpy.frombuffer(buffer(im), dtype='uint8').reshape(512,512,4)

    def switch_image(self):
        ''' Upload the other texture to be rendered
        '''
        if self.cur_image == 0:
            self.texture_stream.update_texture(self.image2)
            self.cur_image = 1
        else:
            self.texture_stream.update_texture(self.image1)
            self.cur_image = 0

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        self.program.bind()
        
        with self.texture_stream:
                
            # Tell the shader to use texture unit 0
            self.program.setUniformValue(self.texture_location, 0)

            # Draw the quad that is shaded with the image
            GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
            GL.glVertexPointer(3, GL.GL_FLOAT, 0, \
                    self.__QUAD_VERTICES.ravel())
            GL.glDrawArrays(GL.GL_QUADS, 0, self.__QUAD_VERTICES.shape[0])
            GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

        self.program.release()

    def sizeHint(self):
        return QtCore.QSize(640, 480)
    
    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)

class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        
        QtGui.QWidget.__init__(self, parent)
        self.gl_widget = GLWidget()
        
        main_layout = QtGui.QHBoxLayout()

        main_layout.addWidget(self.gl_widget)
        self.setLayout(main_layout)

        self.setWindowTitle("Texture Streams...")

    def mouseMoveEvent(self, event):
        self.gl_widget.switch_image()
        self.gl_widget.updateGL()

def main(argv):
    app = QtGui.QApplication(argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main(sys.argv)
