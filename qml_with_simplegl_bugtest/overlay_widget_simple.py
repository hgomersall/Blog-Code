#!/usr/bin/env python

from PySide import QtGui, QtCore
from PySide.QtDeclarative import QDeclarativeView
from PySide.QtCore import QUrl

# Importing GL here also causes everything to break
#from OpenGL import GL

class OverlayWidget(QtGui.QWidget):
    
    def __init__(self, *args):
        super(OverlayWidget, self).__init__(*args)
        
        # We need to set the base colour of the qml widget to be transparent.
        # This is done by setting its palette.
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Base, QtCore.Qt.transparent)

        qml_view = QDeclarativeView(self)
        qml_view.setPalette(palette)

        url = QUrl('control_slides.qml')
        qml_view.setSource(url)

        return

