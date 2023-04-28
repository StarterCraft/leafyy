from PyQt5 import QtGui, QtWidgets

from ui    import GreenyyComponent
from uidef.widget.plantWidget import Ui_PlantWidget


class GreenyyPlantWidget(
    GreenyyComponent, 
    QtWidgets.QMainWindow,
    Ui_PlantWidget):
    def __init__(self):
        super().__init__()
        
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon())

        self.resize(self.minimumSize())
