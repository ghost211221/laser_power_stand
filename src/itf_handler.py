from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import QLocale

import re

from itf_modules.gui import Ui_MainWindow
from itf_modules.combos import CombosHandler


class ItfHandler(QtWidgets.QMainWindow, Ui_MainWindow, CombosHandler):

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        super().__init__()

        self.setupUi(self)  # Это нужно для инициализации нашего дизайна