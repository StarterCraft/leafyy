from PyQt5 import QtWidgets
from uidef.window.general import Ui_GeneralWindow


class GeneralWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_GeneralWindow()
        self.ui.setupUi(self)