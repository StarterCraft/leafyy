from PySide6   import QtCore, QtGui, QtWidgets

from leafyy import ui, options

from ui      import LeafyyUiComponent, LeafyyUiComponentType
from uidef.window.general import Ui_GeneralWindow


class LeafyyGeneralWindow(
    LeafyyUiComponent,
    QtWidgets.QMainWindow,
    Ui_GeneralWindow):
    def __init__(self):
        super().__init__(
            'generalWindow',
            LeafyyUiComponentType.Window,
            displayName = 'Основное окно'
        )

        self.setWindowTitle(self.displayName)
        self.setCentralWidget(self.mdi)

        self.logger.debug('Основное окно инициализировано')

    def interconnect(self):
        self.meiGeneral.triggered.connect(self.show)
        self.meiLog.triggered.connect(ui().logWindow.show)
        self.meiDevices.triggered.connect(ui().settingsWindow.show0)
        self.meiRules.triggered.connect(ui().settingsWindow.show1)
        self.meiKeys.triggered.connect(ui().settingsWindow.show2)
        self.meiViewSettings.triggered.connect(ui().settingsWindow.show3)

    def bind(self):
        self.meiGeneral.setShortcut(QtGui.QKeySequence(options().keys.generalWindow))
        self.meiLog.setShortcut(options().keys.logWindow)
        self.meiDevices.setShortcut(options().keys.settingsWindow)

    def updateUi(self):
        self.meiGeneral.setChecked(self.isVisible())
        self.meiLog.setChecked(ui().logWindow.isVisible())

    def show(self, force: bool = False):
        if (force or not self.isVisible()):
            super().show()
            self.updateUi()

        else:
            self.close()

    def close(self):
        super().close()
        ui().updateUi()

