from PyQt5 import QtWidgets

from ui    import GreenyyUiComponent, GreenyyUiComponentType
from uidef.dialog.ruleProperties import Ui_RulePropertiesDialog


class GreenyyRuleDialog(
    GreenyyUiComponent, 
    QtWidgets.QMainWindow,
    Ui_RulePropertiesDialog):
    def __init__(self):
        super().__init__(f'rulePropertiesDialog ({id(self)})', GreenyyUiComponentType.Dialog)
        
        self.logger.debug(f'Инициализирован диалог {self.name}')
