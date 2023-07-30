from PySide6 import QtWidgets

from ui    import LeafyyUiComponent, LeafyyUiComponentType
from uidef.dialog.ruleItem import Ui_RuleItemDialog


class LeafyyRuleItemDialog(
    LeafyyUiComponent,
    QtWidgets.QMainWindow,
    Ui_RuleItemDialog):
    def __init__(self):
        super().__init__(f'ruleItemDialog ({id(self)})', LeafyyUiComponentType.Dialog)

        self.logger.debug(f'Инициализирован диалог {self.name}')
