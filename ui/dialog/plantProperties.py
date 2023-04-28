from PyQt5 import QtWidgets

from ui    import GreenyyComponent
from uidef.dialog.plantProperties import Ui_PlantPropertiesDialog


class GreenyyPlantDialog(
    GreenyyComponent, 
    QtWidgets.QMainWindow,
    Ui_PlantPropertiesDialog):
    def __init__(self):
        super().__init__(f'plantDialog ({id(self)})')

        self.setupUi(self)
