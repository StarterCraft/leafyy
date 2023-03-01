from PyQt5 import QtWidgets
from enum import Enum
from uidef.window.settings import Ui_SettingsWindow


class SettingsWindow(QtWidgets.QMainWindow, Ui_SettingsWindow):
    class SettingsTab(Enum):
        Devices = 0
        Rules = 1

    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.btnAddDevice.clicked.connect(self.addItem_debug)
        self.btnRemoveDevice.clicked.connect(self.delete_debug)
        
    def show0(self):
        self.tabs.setCurrentIndex(0)
        self.show()

    def show1(self):
        self.tabs.setCurrentIndex(1)
        self.show()

    def addItem_debug(self):
        if (self.tabs.currentIndex()):
            self.liwRules.addItem(f'testItem {self.liwRules.currentIndex().row()}')

        else:
            print(32)
            self.treeDevices.addTopLevelItem(
                QtWidgets.QTreeWidgetItem(self.treeDevices, [f'testItem {self.treeDevices.currentIndex().row()}']))

    def delete_debug(self):
        if (self.tabs.currentIndex()):
            self.liwRules.removeItemWidget(self.liwRules.currentItem())

        else:
            print(42)
            self.treeDevices.removeItemWidget(self.treeDevices.currentItem(), 1)
