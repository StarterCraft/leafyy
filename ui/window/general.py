from PyQt5 import QtCore, QtGui, QtWidgets

from app   import GreenyyComponent
from app   import ui, options

from uidef.window.general import Ui_GeneralWindow


class GreenyyGeneralWindow(
    GreenyyComponent, 
    QtWidgets.QMainWindow,
    Ui_GeneralWindow):
    def __init__(self):
        super().__init__('generalWindow')

        self.setupUi(self)
        self.defaultSize = (
            QtCore.QSize(**options().defaultWindowSize[self.name])
            if (self.name in options().defaultWindowSize.keys()) else
            self.minimumSize()
        )
        
        self.setCentralWidget(self.mdi)

        self.bind()

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
        