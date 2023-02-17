from PyQt5 import QtWidgets
from ui import UiManager
from uidef.dialog.ruleItemAppend import Ui_RuleItemAppendDialog


class RuleItemAppendDialog(QtWidgets.QDialog):
    def __init__(self, ui: UiManager):
        super().__init__()

        ui.setupUiComponent(self, Ui_RuleItemAppendDialog())
