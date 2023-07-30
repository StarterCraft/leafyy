from PySide6 import QtGui, QtWidgets

from ui    import LeafyyUiComponent
from uidef.widget.plantWidget import Ui_PlantWidget


class LeafyyPlantWidget(
    LeafyyUiComponent,
    QtWidgets.QMainWindow,
    Ui_PlantWidget):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QtGui.QIcon())

        self.resize(self.minimumSize())
