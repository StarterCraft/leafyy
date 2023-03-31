from PyQt5 import QtCore, QtGui, QtWidgets
from os import system
from datetime import datetime
from logging import getLevelName
from enum import Enum

from app import logging as manager
from app import userOptions, device
from logger import GreenyyLogger, GreenyyLogLevel
from uidef.window.log import Ui_LogWindow


class GreenyyLogWindowSource(Enum):
    Logger = 0
    Device = 1


class GreenyyLogWindow(QtWidgets.QMainWindow, Ui_LogWindow):
    def __init__(self):
        super().__init__()
        self.logger = GreenyyLogger('LogWindow')

        self.setupUi(self)
        self.setupMenu()
        self.setupUserInput()
        self.interconnect()
        self.bind()
        self.updateUi()

        self.logger.info('Окно журнала инициализировано')

    def show(self):
        self.updateUi()
        super().show()
        self.logger.info('Открыто окно журнала')

    def setupMenu(self):
        self.logLevelActions = QtWidgets.QActionGroup(self)
        self.logLevelActions.setExclusive(True)

        for level, action in zip(GreenyyLogLevel, [
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

        allLoggersAction = QtWidgets.QAction('Все внутренние логгеры', self)
        allLoggersAction.setCheckable(True)
        allLoggersAction.setChecked(
            bool(sum([logger.logWindowVisibility for logger in manager().loggers])))
        allLoggersAction.setData('logger')
        
        self.setLoggingSourceActions.addAction(allLoggersAction)
        
        for logger in manager().loggers:
            action = QtWidgets.QAction(logger.name, self)
            action.setCheckable(True)
            action.setChecked(logger.logWindowVisibility)
            action.setData('logger')
            self.setLoggingSourceActions.addAction(action)

        self.setLoggingSourceActions.addSeparator()

    def setupUserInput(self):
        return

    def interconnect(self):
        self.meiLogFolder.triggered.connect(self.openLogFolder)

        self.meiExit.triggered.connect(self.close)

        self.meiScroll.triggered.connect(self.setScrollingMode)
        self.meiIncreaseFontSize.triggered.connect(self.increaseFontSize)
        self.meiReduceFontSize.triggered.connect(self.reduceFontSize)

        self.btnSend.clicked.connect(self.sendDeviceMessage)

    def bind(self):
        self.meiLogFolder.setShortcut(QtGui.QKeySequence(userOptions().keys.logFolder))
        self.meiExit.setShortcut(QtGui.QKeySequence('Alt+F4'))

        self.meiScroll.setShortcut(QtGui.QKeySequence(userOptions().keys.logScrollMode))
        self.meiIncreaseFontSize.setShortcut(QtGui.QKeySequence(userOptions().keys.logIncreaseFontSize))
        self.meiReduceFontSize.setShortcut(QtGui.QKeySequence(userOptions().keys.logReduceFontSize))

    def updateUi(self):
        for action in self.logLevelActions.actions():
            action.setChecked(manager().globalLevel is action.data())

        self.meiScroll.setChecked(userOptions().logScrollMode)

    def scrollDown(self):
        if (userOptions().logScrollMode):
            c = self.txtLogDisplay.textCursor()
            c.movePosition(c.End)
            self.txtLogDisplay.setTextCursor(c)

    def setGlobalLogLevel(self):
        manager().setGlobalLogLevel(self.logLevelActions.checkedAction().data())
        userOptions().logLevel = getLevelName(self.logLevelActions.checkedAction().data())
        userOptions().write()

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
        userOptions().logScrollMode = self.meiScroll.isChecked()
        self.logger.debug(
            f'Автопрокрутка {"включена" if userOptions().logScrollMode else "отключена"}')
        self.scrollDown()

    def setASCIIMode(self, triggered: QtWidgets.QAction):
        text = triggered.text()
        isChecked = triggered.isChecked()

        if (text.startswith('Все')):
            for a in [ac for ac in self.setLoggingSourceActions.actions() if (
                not ac.text().startswith('Все'))]:
                a.setChecked(isChecked)
                device()[a.text()].logDecodeASCIIMode = isChecked

            userOptions().setLogDecodeASCII('All', isChecked)
            return

        device()[text].decodeASCII = isChecked

    def setLoggerVisibility(self, triggered: QtWidgets.QAction):
        text = triggered.text()
        data = triggered.data()
        isChecked = triggered.isChecked()

        if (text.startswith('Все')):
            for a in [ac for ac in self.setLoggingSourceActions.actions() if (
                ac.data() == data and not ac.text().startswith('Все'))]:
                a.setChecked(isChecked)
                
                if (a.data() == 'logger'):
                    manager()[a.text()].logWindow = isChecked


    def openLogFolder(self):
        system('explorer logs')
        self.logger.debug('Открыта папка с журналами')

    def writeDeviceMessage(self, device):
        if (device.logWindowVisibility):
            content = device.port.readLine()
            toPrint = (str(content) if (device.decodeASCII) else str(content.toHex(' ')))

            self.txtLogDisplay.append(
                f'<span style="color:gray">{datetime.now()}</span> '
                f'[<span style="color:lime">{device.address.upper()}</span>]: {toPrint}')
            
            self.scrollDown()
        
    def validateDeviceMessage(self):
        text = self.lneMessage.text()

        if (not text):
            self.lneMessage.setStyleSheet('border: 1px solid red;')
            self.statusbar.showMessage('Введите данные для отправки!', 2000)
            return

    def sendDeviceMessage(self):
        text = self.lneMessage.text()
        port = self.cbbPort.currentText().upper()

        if (not port):
            self.cbbPort.setStyleSheet('border: 1px solid red;')
            self.statusbar.showMessage('Сначала выберите порт!', 2000)
        else:
            self.cbbPort.setStyleSheet('')

        self.logger.debug(f'Пытаюсь отправить сообщение на порт {port}')

        if (device()[port].port.write(bytearray(text, 'ascii')) != -1):
            self.txtLogDisplay.append(
                f'<span style="color:gray">{datetime.now()}</span> '
                f'[Вы к <span style="color:lime">{port}</span>]: {text}')
        else:
            self.txtLogDisplay.append(
                f'<span style="color:gray">{datetime.now()}</span> '
                f'[Вы к <span style="color:lime">{self.cbbPort.currentText().capitalize()}</span>]: '
                f'<span style="color:red">[Не отправлено!]</span> {self.lneMessage.text()}')
            

        self.lneMessage.clear()
