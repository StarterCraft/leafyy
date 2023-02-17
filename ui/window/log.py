from PyQt5 import QtWidgets
from uidef.window.log import Ui_Log


class LogWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Log()
        self.ui.setupUi(self)