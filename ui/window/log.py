from PyQt5 import QtGui, QtWidgets
from os import system
from datetime import datetime

from app import logging as manager
from app import userOptions, device
from logger import GreenyyLogger, LogLevel
from uidef.window.log import Ui_LogWindow


class LogWindow(QtWidgets.QMainWindow, Ui_LogWindow):
    def __init__(self):
        super().__init__()
        self.logger = GreenyyLogger('LogWindow')

        self.setupUi(self)
        self.setupMenu()
        self.interconnect()
        self.bind()
        self.updateUi()

        self.logger.info('Окно журнала инициализировано')

    def show(self):
        super().show()
        self.logger.info('Открыто окно журнала')

    def setupMenu(self):
        self.logLevelActions = QtWidgets.QActionGroup(self)
        self.logLevelActions.setExclusive(True)

        for level, action in zip(LogLevel, [
            self.meiLogLvlDEBUG, self.meiLogLvlINFO,
            self.meiLogLvlWARNING, self.meiLogLvlERROR,
            self.meiLogLvlCRITICAL
        ]):
            action.setData(level)
            action.setCheckable(True)
            action.triggered.connect(self.setGlobalLogLevel)
            action.setActionGroup(self.logLevelActions)
            self.menuFile.addAction(action)

        self.menuFile.addSeparator()
        self.menuFile.addAction(self.meiExit)

        self.meiScroll.setCheckable(True)

        self.setASCIIModeActions = QtWidgets.QMenu(self)
        self.meiASCII.setMenu(self.setASCIIModeActions)
        self.setASCIIModeActions.triggered.connect(self.setASCIIMode)

        self.setLoggingSourceActions = QtWidgets.QMenu(self)
        self.meiLogSource.setMenu(self.setLoggingSourceActions)
        self.setLoggingSourceActions.triggered.connect(self.setLoggerVisibility)

        for logger in manager().loggers:
            action = QtWidgets.QAction(logger.name, self)
            action.setCheckable(True)
            action.setChecked(logger.logWindowVisibility)
            self.setLoggingSourceActions.addAction(action)

        self.setLoggingSourceActions.addSeparator()


    def interconnect(self):
        self.meiLogFolder.triggered.connect(self.openLogFolder)

        self.meiExit.triggered.connect(self.close)

        self.meiScroll.triggered.connect(self.setScrollingMode)
        self.meiIncreaseFontSize.triggered.connect(self.increaseFontSize)
        self.meiReduceFontSize.triggered.connect(self.reduceFontSize)

    def bind(self):
        self.meiLogFolder.setShortcut(QtGui.QKeySequence(userOptions().keys.logFolder))
        self.meiExit.setShortcut(QtGui.QKeySequence('Alt+F4'))

        self.meiScroll.setShortcut(QtGui.QKeySequence(userOptions().keys.logWindowScrollMode))
        self.meiIncreaseFontSize.setShortcut(QtGui.QKeySequence(userOptions().keys.logIncreaseFontSize))
        self.meiReduceFontSize.setShortcut(QtGui.QKeySequence(userOptions().keys.logReduceFontSize))

    def updateUi(self):
        for action in self.logLevelActions.actions():
            action.setChecked(manager().globalLevel is action.data())

        self.meiScroll.setChecked(userOptions().logWindowScrollMode)

    def scrollDown(self):
        if (userOptions().logWindowScrollMode):
            c = self.txtLogDisplay.textCursor()
            c.movePosition(c.End)
            self.txtLogDisplay.setTextCursor(c)

    def setGlobalLogLevel(self):
        manager().setGlobalLogLevel(self.logLevelActions.checkedAction().data())
        self.logger.publish(manager().globalLogLevel,
            f'Глобальный уровень журнала установлен на {manager().globalLogLevel.name}')

    def increaseFontSize(self):
        self.txtLogDisplay.zoomIn()
        self.logger.debug('Шрифт увеличен')
        self.scrollDown()

    def reduceFontSize(self):
        self.txtLogDisplay.zoomOut()
        self.logger.debug('Шрифт уменьшен')
        self.scrollDown()

    def setScrollingMode(self):
        userOptions().logWindowScrollMode = self.meiScroll.isChecked()
        self.logger.debug(
            f'Автопрокрутка {"включена" if userOptions().logWindowScrollMode else "отключена"}')
        self.scrollDown()

    def setASCIIMode(self, action: QtWidgets.QAction):
        device()[action.text()].decodeASCII = action.isChecked()

    def setLoggerVisibility(self, action: QtWidgets.QAction):
        manager()[action.text()].logWindowVisibility = action.isChecked()

    def openLogFolder(self):
        system('explorer logs')
        self.logger.debug('Открыта папка с журналами')

    def writeDeviceMessage(self, device):
        self.txtLogDisplay.append(
            f'<span style="color:gray">{datetime.now()}</span> '
            f'[<span style="color:green">{device.address.capitalize()}</span>]: '
            f'{device.port.readLine()}')

    def sendDeviceMessage(self):
        device()[self.cbbPort.currentText].port.write(
            bytearray(self.lneMessage.text(), 'utf-8'))
        self.txtLogDisplay.append(
            f'<span style="color:gray">{datetime.now()}</span> '
            f'[Вы к <span style="color:green">{self.cbbPort.currentText().capitalize()}</span>]: '
            f'{self.lneMessage.text()}')
        self.lneMessage.clear()
