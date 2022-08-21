#!/usr/bin/python3
# -*- coding: utf-8 -*-


# -----
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from numpy import random

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.uic import loadUiType

#ui,_ = loadUiType("plot_builder.ui")
# -----



class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        uic.loadUi('plot_builder.ui', self)
        #QMainWindow.__init__(self)
        #self.setupUi(self)




if __name__ == '__main__':
    import sys 
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
