from PyQt5 import QtWidgets
from uidef.dialog.deviceProperties import Ui_DevicePropertiesDialog


class DevicePropertiesDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        ui.setupUiComponent(self, Ui_DevicePropertiesDialog())
        