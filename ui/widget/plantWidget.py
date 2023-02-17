from PyQt5 import QtWidgets
from uidef.widget.plantWidget import Ui_PlantWidget


class PlantWidget(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_PlantWidget()
        self.ui.setupUi(self)
