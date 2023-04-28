from PyQt5         import QtCore, QtGui, QtWidgets
from enum          import Enum

from app           import options, ui
from logger.logger import GreenyyLogger

from ui            import GreenyyComponent
from uidef.window.settings import Ui_SettingsWindow


class GreenyySettingsWindowTab(Enum):
    Devices = 0
    Rules = 1
    Keys = 2
    Environment = 3


class GreenyySettingsWindow(
    GreenyyComponent, 
    QtWidgets.QMainWindow,
    Ui_SettingsWindow):
    def __init__(self):
        super().__init__('settingsWindow')
        
        self.setupUi(self)
        self.defaultSize = (
            QtCore.QSize(*options().defaultWindowSize[self.name])
            if (self.name in options().defaultWindowSize.keys()) else
            self.minimumSize()
        )

        self.interconnect()
        self.updateUi()
        self.bind()

    def show(self, force: bool = False):
        if (force or not self.isVisible()):
            super().show()
            self.updateUi()
            self.updateTreeUi()
            self.logger.info('Открыто окно настроек')

        else:
            self.close()

    def show0(self):
        self.tabs.setCurrentIndex(
            GreenyySettingsWindowTab.Devices.value)
        self.show()

    def show1(self):
        self.tabs.setCurrentIndex(
            GreenyySettingsWindowTab.Rules.value)
        self.show()

    def show2(self):
        self.tabs.setCurrentIndex(
            GreenyySettingsWindowTab.Keys.value)
        self.show()

    def show3(self):
        self.tabs.setCurrentIndex(
            GreenyySettingsWindowTab.Environment.value)
        self.show()

    def close(self):
        self.treeDevices.setCurrentItem()
        self.liwRules.setCurrentItem()
        self.treeKeys.setCurrentItem()

        self.keySequenceEdit.clear()
        self.label.setStyleSheet()

        super().close()
        ui().updateUi()

    def interconnect(self):
        self.treeKeys.currentItemChanged.connect(self.keyBindingSelected)
        self.keySequenceEdit.keySequenceChanged.connect(self.keyBindingEditInitiated)
        self.keySequenceEdit.editingFinished.connect(self.keyBindingEdit)

        self.treeUi.currentItemChanged.connect(self.uiComponentEditInitiated)
        self.treeUi.itemClicked.connect(self.uiComponentToggled)

    def bind(self):
        pass

    def updateUi(self):
        keyBindingItemDefs = {
            'Среда': {
                'generalWindow': 'Открыть основное окно',
                'logWindow': 'Открыть окно журнала',
                'settingsWindow': 'Открыть окно настроек'
            },

            'Окно журнала': {
                'logFolder': 'Открыть папку с журналом',
                'logScrollMode': 'Автопрокрутка',
                'logIncreaseFontSize': 'Увеличить шрифт',
                'logReduceFontSize': 'Уменьшить шрифт'
            }
        }

        for key, subdict in keyBindingItemDefs.items():
            topLevelItem = QtWidgets.QTreeWidgetItem(self.treeKeys, [key])
            for bindingId, bindingDesc in subdict.items():
                bindingItem = QtWidgets.QTreeWidgetItem(topLevelItem, 
                    [bindingDesc, options().keys[bindingId]])
                bindingItem.setData(1, 0x100, options().keys[bindingId])

            self.treeKeys.addTopLevelItem(topLevelItem)

        self.treeKeys.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.treeKeys.header().setStretchLastSection(False)

        self.treeKeys.expandAll()
        self.treeKeys.header().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        
    def updateTreeUi(self):
        windowSettingsItemDef = {
            'Окна': {
                'generalWindow': 'Основное окно',
                'logWindow': 'Журнал',
                'settingsWindow': 'Настройки'
            }
        }

        for gn, subdict in windowSettingsItemDef.items():
            root = QtWidgets.QTreeWidgetItem(self.treeUi, [gn])
            for key, displayName in subdict.items():
                item = QtWidgets.QTreeWidgetItem(
                    root, [
                        displayName, 
                        f'{ui()[key].defaultSize.width()} ✕ '
                        f'{ui()[key].defaultSize.height()}'
                        ])
                
                item.setFlags(
                    QtCore.Qt.ItemIsSelectable | 
                    QtCore.Qt.ItemIsUserCheckable | 
                    QtCore.Qt.ItemIsEnabled)
                
                item.setData(0, 0x100, key)
                
                item.setCheckState(0, (
                    QtCore.Qt.Checked if (key in options().launchWith) else QtCore.Qt.Unchecked))
                
        self.treeUi.addTopLevelItem(root)
        root.setExpanded(True)

    def keyBindingSelected(self, *args):
        currentItem = args[0]
        self.keySequenceEdit.setKeySequence(QtGui.QKeySequence(currentItem.text(1)))

    def keyBindingEditInitiated(self):
        currentItem = self.treeKeys.currentItem()

        if (currentItem and currentItem.text(1)):
            self.keySequenceEdit.setKeySequence(currentItem.text(1))
            self.statusBar.showMessage(f'Установка комбинации для: {currentItem.text(0)}')
            return

        self.statusBar.showMessage('Сначала выберите действие!', 5000)

    def keyBindingEdit(self):
        currentItem = self.treeKeys.currentItem()

        if (not (currentItem and currentItem.text(1))):
            self.statusBar.showMessage('Сначала выберите действие!', 5000)

            self.keySequenceEdit.clear()
            return

        keys = self.keySequenceEdit.keySequence().toString()

        currentItem.setText(1, keys)
        options().keys[currentItem.data(1, 0x100)] = keys
        options().write()
        ui().bind()

        self.statusBar.showMessage(f'Установлена клавиша для {currentItem.text(0)}: {keys}', 5000)

    def uiComponentEditInitiated(self, item: QtWidgets.QTreeWidgetItem):
        '''
        Вызывается QTreeWidget#treeUi.currentItemChanged (self.interconnect).
        Обрабатывает всё, кроме галочки отображения при запуске.
        '''
        text = item.text(0)
        data = item.data(0, 0x100)
        value = (item.checkState(0) == 2)

        if (not data):
            return
        
        
            

    def uiComponentToggled(self, item: QtWidgets.QTreeWidgetItem):
        '''
        Вызывается QTreeWidget#treeUi.itemClicked (self.interconnect).
        Обрабатывает галочку отображения при запуске.
        '''
        data = item.data(0, 0x100)
        value = (item.checkState(0) == 2)

        if (not data):
            return
        
        if (value != data in options().launchWith):
            if (value):
                options().launchWith.append(data)
            else:
                options().launchWith.remove(data)
