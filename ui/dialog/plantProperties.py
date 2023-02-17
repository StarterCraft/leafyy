from PyQt5 import QtWidgets
from ui import UiManager
from uidef.dialog.plantProperties import Ui_PlantPropertiesDialog


class PlantPropertiesDialog(QtWidgets.QDialog):
    def __init__(self, ui: UiManager):
        super().__init__()

        ui.setupUiComponent(self, Ui_PlantPropertiesDialog())
