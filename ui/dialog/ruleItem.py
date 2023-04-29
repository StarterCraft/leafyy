from PyQt5 import QtWidgets

from ui    import GreenyyUiComponent
from uidef.dialog.ruleItem import Ui_RuleItemDialog


class GreenyyRuleItemDialog(
    GreenyyUiComponent, 
    QtWidgets.QMainWindow,
    Ui_RuleItemDialog):
    def __init__(self):
        super().__init__(f'ruleItemDialog ({id(self)})')
        
        self.logger.debug(f'Инициализирован диалог {self.name}')
