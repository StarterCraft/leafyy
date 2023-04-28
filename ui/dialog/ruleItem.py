from PyQt5 import QtWidgets

from ui    import GreenyyComponent
from uidef.dialog.ruleItem import Ui_RuleItemDialog


class GreenyyRuleItemDialog(
    GreenyyComponent, 
    QtWidgets.QMainWindow,
    Ui_RuleItemDialog):
    def __init__(self):
        super().__init__(f'ruleItemDialog ({id(self)})')

        self.setupUi(self)
