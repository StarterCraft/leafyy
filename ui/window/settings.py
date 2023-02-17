from PyQt5 import QtWidgets
from enum import Enum
from uidef.window.settings import Ui_SettingsWindow


class SettingsWindow(QtWidgets.QMainWindow):
    class SettingsTab(Enum):
        Devices = 0
        Plants = 1

    def __init__(self):
        super().__init__()

        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)

    
    def show0(self):
        self.ui.tabs.setCurrentIndex(0)
        self.show()


    def show1(self):
        self.ui.tabs.setCurrentIndex(1)
        self.show()
