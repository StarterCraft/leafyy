from PySide6 import QtWidgets

from ui    import LeafyyUiComponent, LeafyyUiComponentType
from uidef.dialog.plantProperties import Ui_PlantPropertiesDialog


class LeafyyPlantDialog(
    LeafyyUiComponent,
    QtWidgets.QMainWindow,
    Ui_PlantPropertiesDialog):
    def __init__(self):
        super().__init__(f'plantDialog ({id(self)})', LeafyyUiComponentType.Dialog)

        self.logger.debug(f'Инициализирован диалог {self.name}')
