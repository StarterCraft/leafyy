from PyQt5 import QtGui, QtWidgets
from enum import Enum

from app import userOptions, ui
from logger.logger import GreenyyLogger
from uidef.window.settings import Ui_SettingsWindow


class SettingsWindow(QtWidgets.QMainWindow, Ui_SettingsWindow):
    class SettingsTab(Enum):
        Devices = 0
        Rules = 1

    def __init__(self):
        super().__init__()

        self.logger = GreenyyLogger('SettingsWindow')
        self.setupUi(self)
        self.interconnect()
        self.updateUi()

    def show(self):
        self.statusBar.clearMessage()
        super().show()
        self.logger.info('Открыто окно настроек')

    def show0(self):
        self.tabs.setCurrentIndex(0)
        self.show()

    def show1(self):
        self.tabs.setCurrentIndex(1)
        self.show()

    def show2(self):
        self.tabs.setCurrentIndex(2)
        self.show()

    def close(self):
        self.treeDevices.setCurrentItem()
        self.liwRules.setCurrentItem()
        self.treeKeys.setCurrentItem()

        self.keySequenceEdit.clear()
        self.label.setStyleSheet()
        super().close()

    def interconnect(self):
        self.treeKeys.currentItemChanged.connect(self.keyBindingSelected)
        self.keySequenceEdit.keySequenceChanged.connect(self.keyBindingEditInitiated)
        self.keySequenceEdit.editingFinished.connect(self.keyBindingEdit)

    def bind(self):
        pass

    def updateUi(self):
        items = {
            'Окно журнала': {
                'logFolder': ['Открыть папку с журналом', userOptions().keys.logFolder],
                'logScrollMode': ['Автопрокрутка', userOptions().keys.logScrollMode],
                'logIncreaseFontSize': ['Увеличить шрифт', userOptions().keys.logIncreaseFontSize],
                'logReduceFontSize': ['Уменьшить шрифт', userOptions().keys.logReduceFontSize]
            }
        }

        for key, subdict in items.items():
            topLevelItem = QtWidgets.QTreeWidgetItem(self.treeKeys, [key])
            for bindingName, binding in subdict.items():
                bindingItem = QtWidgets.QTreeWidgetItem(topLevelItem, binding)
                bindingItem.setData(1, 0x100, bindingName)

            self.treeKeys.addTopLevelItem(topLevelItem)

        self.treeKeys.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.treeKeys.header().setStretchLastSection(False)

    def keyBindingSelected(self, *args):
        currentItem = args[0]
        self.keySequenceEdit.setKeySequence(QtGui.QKeySequence(currentItem.text(1)))

    def keyBindingEditInitiated(self):
        if (self.treeKeys.currentItem() and self.treeKeys.currentItem().text(1)):
            self.statusBar.showMessage(f'Установка комбинации для: {self.treeKeys.currentItem().text(0)}')
            self.btnKeySequence.clicked.connect(self.keyBindingEdit)
            return

        self.statusBar.showMessage('Сначала выберите действие!', 5000)

    def keyBindingEdit(self):
        currentItem = self.treeKeys.currentItem()
        keys = self.keySequenceEdit.keySequence().toString()

        currentItem.setText(1, keys)
        userOptions().keys.setBinding(currentItem.data(1, 0x100), keys)
        userOptions().write()
        ui().bind()

        self.statusBar.showMessage(f'Установлена клавиша для {currentItem.text(0)}: {keys}', 5000)
