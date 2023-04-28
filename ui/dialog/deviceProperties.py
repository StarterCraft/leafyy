from PyQt5 import QtWidgets

from ui    import GreenyyComponent
from uidef.dialog.deviceProperties import Ui_DevicePropertiesDialog


class GreenyyDeviceDialog(
    GreenyyComponent, 
    QtWidgets.QMainWindow,
    Ui_DevicePropertiesDialog):
    def __init__(self):
        super().__init__(f'deviceDialog ({id(self)})')

        self.setupUi(self)
        