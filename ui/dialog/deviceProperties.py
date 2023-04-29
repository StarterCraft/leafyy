from PyQt5 import QtWidgets

from ui    import GreenyyUiComponent
from uidef.dialog.deviceProperties import Ui_DevicePropertiesDialog


class GreenyyDeviceDialog(
    GreenyyUiComponent, 
    QtWidgets.QMainWindow,
    Ui_DevicePropertiesDialog):
    def __init__(self):
        super().__init__(f'deviceDialog ({id(self)})')
        
        self.logger.debug(f'Инициализирован диалог {self.name}')
        