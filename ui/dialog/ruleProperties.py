from PySide6 import QtWidgets

from ui    import LeafyyUiComponent, LeafyyUiComponentType
from uidef.dialog.ruleProperties import Ui_RulePropertiesDialog


class LeafyyRuleDialog(
    LeafyyUiComponent, 
    QtWidgets.QMainWindow,
    Ui_RulePropertiesDialog):
    def __init__(self):
        super().__init__(f'rulePropertiesDialog ({id(self)})', LeafyyUiComponentType.Dialog)
        
        self.logger.debug(f'Инициализирован диалог {self.name}')
