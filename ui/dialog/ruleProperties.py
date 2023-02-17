from PyQt5 import QtWidgets
from ui import UiManager
from uidef.dialog.ruleProperties import Ui_RulePropertiesDialog


class RulePropertiesDialog(QtWidgets.QDialog):
    def __init__(self, ui: UiManager):
        super().__init__()

        ui.setupUiComponent(self, Ui_RulePropertiesDialog())
