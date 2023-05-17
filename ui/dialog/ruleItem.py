from PyQt5 import QtWidgets

from ui    import GreenyyUiComponent, GreenyyUiComponentType
from uidef.dialog.ruleItem import Ui_RuleItemDialog


class GreenyyRuleItemDialog(
    GreenyyUiComponent, 
    QtWidgets.QMainWindow,
    Ui_RuleItemDialog):
    def __init__(self):
        super().__init__(f'ruleItemDialog ({id(self)})', GreenyyUiComponentType.Dialog)
        
        self.logger.debug(f'Инициализирован диалог {self.name}')
