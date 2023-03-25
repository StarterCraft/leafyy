from PyQt5 import QtWidgets
from uidef.dialog.plantProperties import Ui_PlantPropertiesDialog


class PlantPropertiesDialog(QtWidgets.QDialog, Ui_PlantPropertiesDialog):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
