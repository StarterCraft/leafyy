from PySide6 import QtGui, QtWidgets
from uidef.widget.logSettings import Ui_LogWindowSettingsWidget


class LeafyyLogWindowSettingsWidget(
    QtWidgets.QWidget,
    Ui_LogWindowSettingsWidget):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
