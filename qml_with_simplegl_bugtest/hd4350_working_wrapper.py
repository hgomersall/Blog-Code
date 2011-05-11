#!/usr/bin/env python

# Calling this wrapper does work for the ATI
# HD 4350 but not the Intel GMA X3100

import sys
from PyQt4.QtGui import QApplication
from gl_simple import DisplayWidget

def make_it_work(argv):
    app = QApplication(argv)

    widget = DisplayWidget()
    widget.show()
    widget.resize(800,600)

    sys.exit(app.exec_())

def main(argv):
    make_it_work(argv)

if __name__ == '__main__':
    main(sys.argv)

