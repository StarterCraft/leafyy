from PyQt5 import QtWidgets
from uidef.dialog.deviceProperties import Ui_DevicePropertiesDialog


class DevicePropertiesDialog(QtWidgets.QDialog, Ui_DevicePropertiesDialog):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        