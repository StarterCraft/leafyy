from PyQt5    import QtWidgets
from datetime import datetime

from app      import GreenyyComponent
from app      import hardware


from .window.general          import GreenyyGeneralWindow
from .window.log              import GreenyyLogWindow
from .window.settings         import GreenyySettingsWindow

from .dialog.deviceProperties import GreenyyDeviceDialog
from .dialog.plantProperties  import GreenyyPlantDialog
from .dialog.ruleItem         import GreenyyRuleItemDialog
from .dialog.ruleProperties   import GreenyyRuleDialog

from .widget.plantWidget      import GreenyyPlantWidget


class GreenyyUiManager(GreenyyComponent):
    def __init__(self) -> None:
        super().__init__('ui')

        self.generalWindow = GreenyyGeneralWindow()
        self.settingsWindow = GreenyySettingsWindow()
        self.logWindow = GreenyyLogWindow()

        self.components = [
            self.generalWindow,
            self.settingsWindow,
            self.logWindow
        ]

        for c in self.components: 
            self.logger.debug(f'{c.name} size: {c.size()}')

        self.interconnect()

        self.logger.debug('Инициализация интерфейса завершена')

    def __getitem__(self, id: str) -> GreenyyComponent:
        try:
            return [c for c in self.components if (c.name == id)][0]
        except IndexError:
            raise KeyError(
                f'Компонент GUI {id} не найден или не зарегистрирован')

    def __iter__(self):
        return iter(self.components)
    
    def isVisible(self) -> bool:
        return any(c.isVisible() for c in self.components)

    def interconnect(self):
        self.generalWindow.meiGeneral.triggered.connect(self.generalWindow.show)
        self.generalWindow.meiLog.triggered.connect(self.logWindow.show)
        self.generalWindow.meiDevices.triggered.connect(self.settingsWindow.show0)
        self.generalWindow.meiRules.triggered.connect(self.settingsWindow.show1)
        self.generalWindow.meiKeys.triggered.connect(self.settingsWindow.show2)
        self.generalWindow.meiEnvironment.triggered.connect(self.settingsWindow.show3)

        self.logWindow.meiGeneral.triggered.connect(self.generalWindow.show)
        self.logWindow.meiLog.triggered.connect(self.logWindow.show)
        self.logWindow.meiDevices.triggered.connect(self.settingsWindow.show0)
        self.logWindow.meiRules.triggered.connect(self.settingsWindow.show1)
        self.logWindow.meiKeys.triggered.connect(self.settingsWindow.show2)
        self.logWindow.meiEnvironment.triggered.connect(self.settingsWindow.show3)

    def bind(self):
        self.generalWindow.bind()
        self.settingsWindow.bind()
        self.logWindow.bind()

    def updateUi(self):
        self.generalWindow.updateUi()
        self.logWindow.updateUi()
        self.settingsWindow.updateUi()

    def addComponent(self, component: GreenyyComponent):
        self.components.append(component)

    def deviceIntegration(self):
        self.logWindow.allDevicesAction = QtWidgets.QAction('Все устройства', self.logWindow)
        self.logWindow.allDevicesAction.setCheckable(True)
        self.logWindow.allDevicesAction.setChecked(all(d.logWindow for d in hardware()))
        self.logWindow.allDevicesAction.setData('device')
        self.logWindow.setLoggingSourceActions.addAction(self.logWindow.allDevicesAction)

        self.logWindow.allASCIIAction = QtWidgets.QAction('Все', self.logWindow)
        self.logWindow.allASCIIAction.setCheckable(True)
        self.logWindow.allASCIIAction.setChecked(all(d.decodeASCIIMode for d in hardware()))
        self.logWindow.setASCIIModeActions.addAction(self.logWindow.allASCIIAction)

        for d in hardware():
            self.generalWindow.meiWindow.addAction(d.address)

            self.logWindow.cbbPort.addItem(d.address)
            self.logWindow.cbbPort.setCurrentText(d.address)

            setASCIIModeAction = QtWidgets.QAction(d.address.upper(), self.logWindow)
            setASCIIModeAction.setCheckable(True)
            setASCIIModeAction.setChecked(d.decodeASCII)
            self.logWindow.setASCIIModeActions.addAction(setASCIIModeAction)

            setLoggerVisibilityAction = QtWidgets.QAction(d.address.upper(), self.logWindow)
            setLoggerVisibilityAction.setCheckable(True)
            setLoggerVisibilityAction.setChecked(d.logWindow)
            setLoggerVisibilityAction.setData('device')
            self.logWindow.setLoggingSourceActions.addAction(setLoggerVisibilityAction)

            self.settingsWindow.treeDevices.addTopLevelItem(d.liwDevicesItem)
            
            d.port.readyRead.connect(lambda: self.logWindow.writeDeviceMessage(d))
