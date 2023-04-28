from PyQt5 import QtWidgets

from ui    import GreenyyComponent
from uidef.dialog.ruleProperties import Ui_RulePropertiesDialog


class GreenyyRuleDialog(
    GreenyyComponent, 
    QtWidgets.QMainWindow,
    Ui_RulePropertiesDialog):
    def __init__(self):
        super().__init__(f'rulePropertiesDialog ({id(self)})')

        self.setupUi(self)
