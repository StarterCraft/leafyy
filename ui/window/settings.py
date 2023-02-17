from PyQt5 import QtWidgets
from enum import Enum
from uidef.window.settings import Ui_SettingsWindow


class SettingsWindow(QtWidgets.QMainWindow):
    class SettingsTab(Enum):
        Devices = 0
        Rules = 1

    def __init__(self):
        super().__init__()

        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)

        self.ui.btnAddDevice.clicked.connect(self.addItem_debug)
        self.ui.btnRemoveDevice.clicked.connect(self.delete_debug)
        
    def show0(self):
        self.ui.tabs.setCurrentIndex(0)
        self.show()

    def show1(self):
        self.ui.tabs.setCurrentIndex(1)
        self.show()

    def addItem_debug(self):
        if (self.ui.tabs.currentIndex()):
            self.ui.liwRules.addItem(f'testItem {self.ui.liwRules.currentIndex().row()}')

        else:
            print(32)
            self.ui.treeDevices.addTopLevelItem(
                QtWidgets.QTreeWidgetItem(self.ui.treeDevices, [f'testItem {self.ui.treeDevices.currentIndex().row()}']))

    def delete_debug(self):
        if (self.ui.tabs.currentIndex()):
            self.ui.liwRules.removeItemWidget(self.ui.liwRules.currentItem())

        else:
            print(42)
            self.ui.treeDevices.removeItemWidget(self.ui.treeDevices.currentItem(), 1)
