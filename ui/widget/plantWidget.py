from PyQt5 import QtGui, QtWidgets
from uidef.widget.plantWidget import Ui_PlantWidget


class PlantWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_PlantWidget()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon())
        self.resize(self.minimumSize())
