#!/usr/bin/env python

import sys
from PySide.QtCore import QUrl
from PySide.QtGui import QGraphicsScene, QGraphicsView, QApplication, QMessageBox
from PySide.QtDeclarative import QDeclarativeView
from PySide.QtOpenGL import QGLWidget

try:
    from OpenGL import GL
except ImportError:
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "Drawer test",
                            "PyOpenGL must be installed to run this example.",
                            QMessageBox.Ok | QMessageBox.Default,
                            QMessageBox.NoButton)
    sys.exit(1)


def main(argv):
    app = QApplication(argv)

    display_widget = QDeclarativeView()
    display_widget.setViewport(QGLWidget())
 
    display_widget.setResizeMode(QDeclarativeView.SizeRootObjectToView)
    display_widget.setSource(QUrl('drawer_demo.qml'))
    display_widget.show()
    display_widget.resize(640,480)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)
