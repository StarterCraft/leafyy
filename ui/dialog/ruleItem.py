from PyQt5 import QtWidgets
from uidef.dialog.ruleItem import Ui_RuleItemDialog


class GreenyyRuleItemDialog(QtWidgets.QDialog, Ui_RuleItemDialog):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
