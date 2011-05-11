#!/usr/bin/env python

# Calling this file doesn't work

import sys
from PyQt4.QtGui import QApplication
from gl_simple import DisplayWidget

def main(argv):
    app = QApplication(argv)

    widget = DisplayWidget()
    widget.show()
    widget.resize(800,600)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)

