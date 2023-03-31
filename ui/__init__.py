from PyQt5 import QtWidgets
from datetime import datetime

from app import device
from logger import GreenyyLogger

from .window.general import GreenyyGeneralWindow
from .window.log import GreenyyLogWindow
from .window.settings import GreenyySettingsWindow

from .dialog.deviceProperties import GreenyyDeviceDialog
from .dialog.plantProperties import GreenyyPlantDialog
from .dialog.ruleItem import GreenyyRuleItemDialog
from .dialog.ruleProperties import GreenyyRuleDialog


class GreenyyUiManager():
    def __init__(self) -> None:
        self.logger = GreenyyLogger('UIManager')
        self.generalWindow = GreenyyGeneralWindow()
        self.settingsWindow = GreenyySettingsWindow()
        self.logWindow = GreenyyLogWindow()

        self.interconnect()
        self.logger.debug('Инициализация интерфейса завершена')

    def interconnect(self):
        self.generalWindow.meiDevices.triggered.connect(self.settingsWindow.show0)
        self.generalWindow.meiRules.triggered.connect(self.settingsWindow.show1)
        self.generalWindow.meiKeys.triggered.connect(self.settingsWindow.show2)
        self.generalWindow.meiLog.triggered.connect(self.logWindow.show)

    def bind(self):
        self.generalWindow.bind()
        self.settingsWindow.bind()
        self.logWindow.bind()

    def deviceIntegration(self):
        allDevicesAction = QtWidgets.QAction('Все устройства', self.logWindow)
        allDevicesAction.setCheckable(True)
        allDevicesAction.setChecked(
            bool(sum([d.logWindow for d in device().devices])))
        allDevicesAction.setData('device')
        self.logWindow.setLoggingSourceActions.addAction(allDevicesAction)

        for d in device().devices:
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
