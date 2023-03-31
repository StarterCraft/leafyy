from PyQt5 import QtWidgets
from uidef.window.general import Ui_GeneralWindow


class GreenyyGeneralWindow(QtWidgets.QMainWindow, Ui_GeneralWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def bind(self):
        pass
        