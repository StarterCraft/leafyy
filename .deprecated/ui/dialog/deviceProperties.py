from PySide6 import QtWidgets

from ui    import LeafyyUiComponent, LeafyyUiComponentType
from uidef.dialog.deviceProperties import Ui_DevicePropertiesDialog


class LeafyyDeviceDialog(
    LeafyyUiComponent,
    QtWidgets.QMainWindow,
    Ui_DevicePropertiesDialog):
    def __init__(self):
        super().__init__(f'deviceDialog ({id(self)})', LeafyyUiComponentType.Dialog)

        self.logger.debug(f'Инициализирован диалог {self.name}')

