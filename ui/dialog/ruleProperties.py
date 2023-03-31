from PyQt5 import QtWidgets
from uidef.dialog.ruleProperties import Ui_RulePropertiesDialog


class GreenyyRuleDialog(QtWidgets.QDialog, Ui_RulePropertiesDialog):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
