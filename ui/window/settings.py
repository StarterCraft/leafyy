from PyQt5         import QtCore, QtGui, QtWidgets
from enum          import Enum

from greenyy       import deepget
from greenyy       import options, ui
from logger.logger import GreenyyLogger

from ui            import GreenyyUiComponent, GreenyyUiComponentType
from uidef.window.settings import Ui_SettingsWindow


class GreenyySettingsWindowTab(Enum):
    Devices = 0
    Rules = 1
    Keys = 2
    View = 3


class GreenyySettingsWindow(
    GreenyyUiComponent, 
    QtWidgets.QMainWindow,
    Ui_SettingsWindow):
    def __init__(self):
        super().__init__(
            'settingsWindow',
            GreenyyUiComponentType.Window,
            displayName = 'Настройки'
        )
        
        self.logger.debug('Окно настроек инициализировано')

    def interconnect(self):
        self.treeKeys.itemClicked.connect(self.keyBindingSelected)
        self.keySequenceEdit.keySequenceChanged.connect(self.keyBindingEditInitiated)
        self.keySequenceEdit.editingFinished.connect(self.keyBindingEdit)

        self.treeUi.currentItemChanged.connect(self.uiComponentEditInitiated)
        self.treeUi.itemClicked.connect(self.uiComponentToggled)
        self.treeUi.itemDoubleClicked.connect(self.uiComponentShowRequested)

        self.spbHorizontal.valueChanged.connect(self.uiComponentSizeAdjusted)
        self.spbVertical.valueChanged.connect(self.uiComponentSizeAdjusted)

        self.cbbGlobalTheme.currentTextChanged.connect(self.uiGlobalThemeSelected)
        self.cbbComponentTheme.currentTextChanged.connect(self.uiComponentThemeSelected)

    def bind(self):
        pass

    def clearUi(self):
        self.treeDevices.blockSignals(True)
        self.treeDevices.clearSelection()
        self.treeDevices.blockSignals(False)

        self.treeKeys.blockSignals(True)
        self.treeKeys.clearSelection()
        self.treeKeys.blockSignals(False)
        
        self.treeUi.blockSignals(True)
        self.treeUi.clearSelection()
        self.treeUi.blockSignals(False)

        self.keySequenceEdit.clear()
        self.statusBar.clearMessage()

    def updateUi(self):
        blockCbbGT = QtCore.QSignalBlocker(self.cbbGlobalTheme)

        self.cbbGlobalTheme.setDuplicatesEnabled(False)
        self.cbbGlobalTheme.clear()

        for theme in ui().themes:
            if (hasattr(theme, 'app') or theme.name == 'default'):
                self.cbbGlobalTheme.addItem(theme.displayName, theme.name)
                if (ui().getTheme(
                    deepget(options().ui, 'app.theme', default='default')).displayName ==
                    theme.displayName):
                    self.cbbGlobalTheme.setCurrentText(theme.displayName)

        keyBindingItemDefs = {
            'Внешний вид': {
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
                bindingItem.setData(1, 0x100, bindingId)

            self.treeKeys.addTopLevelItem(topLevelItem)

        self.treeKeys.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.treeKeys.header().setStretchLastSection(False)

        self.treeKeys.expandAll()
        self.treeKeys.header().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        
    def updateUiTree(self):
        self.treeUi.clear()

        windowSettingsItemDef = {
            n: dn for n, dn in
            zip(GreenyyUiComponentType._member_names_, ['Окна', 'Диалоги', 'Виджеты'])
        }

        for n, dn in windowSettingsItemDef.items():
            components = [c for c in ui() if (c.cmType == GreenyyUiComponentType[n])]
            root = QtWidgets.QTreeWidgetItem(self.treeUi, [f'{dn} ({len(components)})'])

            for component in components:
                item = QtWidgets.QTreeWidgetItem(
                    root, [
                        component.displayName, 
                        f'{ui()[component.name].defaultSize.width()} ✕ '
                        f'{ui()[component.name].defaultSize.height()}',
                        ui().getTheme(ui()[component.name].theme).displayName
                        ]
                    )
                
                item.setFlags(
                    QtCore.Qt.ItemIsSelectable | 
                    QtCore.Qt.ItemIsUserCheckable | 
                    QtCore.Qt.ItemIsEnabled
                )
                
                print(f'setting data to {component.name}')
                item.setData(0, 0x100, component.name)
                print(f'98 {item.data(0, 0x100)} {item.data(1, 0x100)}')
                
                item.setCheckState(0, (
                    2 if (deepget(options().ui, f'{component.name}.onLaunch', default = False)) else 0))
                
            self.treeUi.addTopLevelItem(root)

        self.treeUi.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.treeUi.header().setStretchLastSection(False)

        self.treeUi.expandAll()
        self.treeUi.header().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

    def show(self, force: bool = False):
        if (force or not self.isVisible()):
            super().show()
            self.clearUi()
            self.updateUi()
            self.updateUiTree()
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
            GreenyySettingsWindowTab.View.value)
        self.show()

    def close(self):
        self.treeDevices.blockSignals(True)
        self.treeDevices.clearSelection()
        self.treeDevices.blockSignals(False)

        self.liwRules.blockSignals(True)
        self.liwRules.clearSelection()
        self.liwRules.blockSignals(False)

        self.treeKeys.blockSignals(True)
        self.treeKeys.clearSelection()
        self.treeKeys.blockSignals(False)

        self.keySequenceEdit.clear()
        self.label.setStyleSheet('')

        super().close()
        ui().updateUi()

    def tabBarClicked(self, index: int):
        if (index):
            self.tabs.setCurrentIndex(index)
            self.statusBar.clearMessage()

    def keyBindingSelected(self, *args):
        currentItem = args[0]
        self.keySequenceEdit.setKeySequence(QtGui.QKeySequence(currentItem.text(1)))

    def keyBindingEditInitiated(self):
        print(f'started edit')
        currentItem = self.treeKeys.currentItem()

        if (currentItem and currentItem.text(1)):
            self.keySequenceEdit.setKeySequence('')
            self.statusBar.showMessage(f'Установка комбинации для: {currentItem.text(0)}')
            return

        self.statusBar.showMessage('Сначала выберите действие!', 5000)

    def keyBindingEdit(self):
        print('ended edit')
        currentItem = self.treeKeys.currentItem()

        if (not (currentItem and currentItem.text(1))):
            self.statusBar.showMessage('Сначала выберите действие!', 5000)

            self.keySequenceEdit.clear()
            return

        keys = self.keySequenceEdit.keySequence().toString()

        print(currentItem.data(1, 0x100))

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
        if (not item):
            self.cbbComponentTheme.clear()
            self.cbbComponentTheme.setEnabled(False)
            return

        text = item.text(0)
        data = item.data(0, 0x100)
        value = (item.checkState(0) == 2)

        if (not data):
            return
        
        self.logger.debug(f'Выбрали {text} ({data}, {value})')

        blockH = QtCore.QSignalBlocker(self.spbHorizontal)
        blockV = QtCore.QSignalBlocker(self.spbVertical)

        self.spbHorizontal.setRange(
            ui()[data].minimumSize().width(),
            ui()[data].maximumSize().width()
        )
        self.spbHorizontal.setValue(
            ui()[data].defaultSize.width()
        )

        self.spbVertical.setRange(
            ui()[data].minimumSize().height(),
            ui()[data].maximumSize().height()
        )
        self.spbVertical.setValue(
            ui()[data].defaultSize.height()
        )

        self.cbbComponentTheme.setEnabled(True)
        self.cbbComponentTheme.setDuplicatesEnabled(False)
        self.cbbComponentTheme.clear()

        blockCbbCT = QtCore.QSignalBlocker(self.cbbComponentTheme)

        for theme in ui().themes:
            if (hasattr(theme, data) or theme.name == 'default'):
                self.cbbComponentTheme.addItem(theme.displayName, theme.name)
                if (ui().getTheme(
                    deepget(options().ui, f'{data}.theme', default='default')).displayName ==
                    theme.displayName):
                    self.cbbComponentTheme.setCurrentText(theme.displayName)

    def uiComponentToggled(self, item: QtWidgets.QTreeWidgetItem):
        '''
        Вызывается QTreeWidget#treeUi.itemClicked (self.interconnect).
        Обрабатывает галочку отображения при запуске.
        '''
        if (not item):
            self.cbbComponentTheme.clear()
            self.cbbComponentTheme.setEnabled(False)
            return

        text = item.text(0)
        data = item.data(0, 0x100)
        value = (item.checkState(0) == 2)

        self.logger.debug(f'Тыкнули {item.text(0)} ({data}, {value})')

        if (not data):
            self.cbbComponentTheme.clear()
            self.cbbComponentTheme.setEnabled(False)
            return
        
        if (value != deepget(options().ui, f'{data}.onLaunch', False)):
            if (options().ui.get(data, False)):
                options().ui[data]['onLaunch'] = value
            
            else:
                options().ui[data] = {
                    'onLaunch': value
                }

            options().write()

    def uiComponentShowRequested(self):
        item: QtWidgets.QTreeWidgetItem = self.treeUi.currentItem()

        if (not item or not item.data(0, 0x100)):
            return
        
        data = item.data(0, 0x100)

        ui()[data].show()
        self.logger.debug(f'Компонент {data} открыт по запросу')

    def uiComponentSizeAdjusted(self):
        item: QtWidgets.QTreeWidgetItem = self.treeUi.currentItem()

        if (not item or not item.data(0, 0x100)):
            return
        
        data = item.data(0, 0x100)
        
        ui()[data].resize(self.spbHorizontal.value(), self.spbVertical.value())
        ui()[data].defaultSize = QtCore.QSize(self.spbHorizontal.value(), self.spbVertical.value())
        options().ui[data]['size'] = [self.spbHorizontal.value(), self.spbVertical.value()]

        options().write()

        item.setText(1, f'{self.spbHorizontal.value()} ✕ '
                        f'{self.spbVertical.value()}')

    def uiGlobalThemeSelected(self, text: str):
        for theme in ui().themes:
            if (text == theme.displayName):
                ui().themize(theme.name)

                if ('app' in options().ui.keys()):
                    options().ui['app']['theme'] = theme.name
                else:
                    options().ui['app'] = {'theme': theme.name}

                options().write()
                break

    def uiComponentThemeSelected(self, text: str):
        item: QtWidgets.QTreeWidgetItem = self.treeUi.currentItem()

        if (not item):
            self.cbbComponentTheme.setEnabled(False)
            return

        data = item.data(0, 0x100)

        for theme in ui().themes:
            if (theme.displayName == text):
                if (data in options().ui.keys()):
                    options().ui[data]['theme'] = theme.name
                else:
                    options().ui[data] = {'theme': theme.name}

                options().write()

                ui().themizeComponent(ui()[data], theme.name)

                item.setText(2, theme.displayName)
                self.logger.info(f'Тема для {item.text(0)} ({data}) изменена на {theme.name}')
                return
