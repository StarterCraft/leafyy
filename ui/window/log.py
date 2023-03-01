from PyQt5 import QtWidgets
from uidef.window.log import Ui_Log


class LogWindow(QtWidgets.QMainWindow, Ui_Log):
    def __init__(self):
        super().__init__()

        self.setupUi(self)