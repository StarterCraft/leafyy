from PyQt5 import QtGui, QtWidgets

from ui    import GreenyyUiComponent
from uidef.widget.plantWidget import Ui_PlantWidget


class GreenyyPlantWidget(
    GreenyyUiComponent, 
    QtWidgets.QMainWindow,
    Ui_PlantWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowIcon(QtGui.QIcon())

        self.resize(self.minimumSize())
