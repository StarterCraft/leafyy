from PySide6 import QtWidgets

from ui    import GreenyyUiComponent, GreenyyUiComponentType
from uidef.dialog.deviceProperties import Ui_DevicePropertiesDialog


class GreenyyDeviceDialog(
    GreenyyUiComponent, 
    QtWidgets.QMainWindow,
    Ui_DevicePropertiesDialog):
    def __init__(self):
        super().__init__(f'deviceDialog ({id(self)})', GreenyyUiComponentType.Dialog)
        
        self.logger.debug(f'Инициализирован диалог {self.name}')
        