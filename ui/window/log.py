from PySide6    import QtCore, QtGui, QtWidgets
from os       import system
from datetime import datetime
from logging  import getLevelName
from enum     import Enum

from greenyy  import log
from greenyy  import ui, options, hardware
from logger   import GreenyyLogger, GreenyyLogLevel

from ui       import GreenyyUiComponent, GreenyyUiComponentType
from uidef.window.log import Ui_LogWindow


class GreenyyLogWindowSource(Enum):
    Logger = 0
    Device = 1


class GreenyyLogWindow(
    GreenyyUiComponent, 
    QtWidgets.QMainWindow,
    Ui_LogWindow):
    def __init__(self):
        super().__init__(
            'logWindow',
            GreenyyUiComponentType.Window,
            displayName = 'Журнал'
        )

        self.setupMenu()
        self.setupUserInput()

        self.logger.info('Окно журнала инициализировано')

    def setupMenu(self):
        self.logLevelActions = QtGui.QActionGroup(self)
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
        self.allASCIIAction = None

        self.setLoggingSourceActions = QtWidgets.QMenu(self)
        self.meiLogSource.setMenu(self.setLoggingSourceActions)
        self.setLoggingSourceActions.triggered.connect(self.setLoggerVisibility)

        self.allLoggersAction = QtGui.QAction('Все внутренние логгеры', self)
        self.allLoggersAction.setCheckable(True)
        self.allLoggersAction.setChecked(all(l.logWindow for l in log()))
        self.allLoggersAction.setData('logger')
        
        self.setLoggingSourceActions.addAction(self.allLoggersAction)
        
        for logger in log().loggers:
            action = QtGui.QAction(logger.name, self)
            action.setCheckable(True)
            action.setChecked(logger.logWindowVisibility)
            action.setData('logger')
            self.setLoggingSourceActions.addAction(action)

        self.setLoggingSourceActions.addSeparator()

        self.allDevicesAction = None

    def setupUserInput(self):
        return

    def interconnect(self):
        
        self.meiLog.triggered.connect(self.show)
        self.meiDevices.triggered.connect(ui().settingsWindow.show0)
        self.meiRules.triggered.connect(ui().settingsWindow.show1)
        self.meiKeys.triggered.connect(ui().settingsWindow.show2)
        self.meiViewSettings.triggered.connect(ui().settingsWindow.show3)

        self.meiLogFolder.triggered.connect(self.openLogFolder)

        self.meiExit.triggered.connect(self.close)

        self.meiScroll.triggered.connect(self.setScrollingMode)
        self.meiIncreaseFontSize.triggered.connect(self.increaseFontSize)
        self.meiReduceFontSize.triggered.connect(self.reduceFontSize)

        self.btnSend.clicked.connect(self.sendDeviceMessage)

    def bind(self):
        self.meiLog.setShortcut(options().keys.logWindow)
        self.meiDevices.setShortcut(options().keys.settingsWindow)

        self.meiLogFolder.setShortcut(QtGui.QKeySequence(options().keys.logFolder))
        self.meiExit.setShortcut(QtGui.QKeySequence('Alt+F4'))

        self.meiScroll.setShortcut(QtGui.QKeySequence(options().keys.logScrollMode))
        self.meiIncreaseFontSize.setShortcut(QtGui.QKeySequence(options().keys.logIncreaseFontSize))
        self.meiReduceFontSize.setShortcut(QtGui.QKeySequence(options().keys.logReduceFontSize))

    def cleanUi(self):
        self.statusbar.clearMessage()
        self.lneMessage.clear()

    def updateUi(self):
        for action in self.logLevelActions.actions():
            action.setChecked(log().globalLevel is action.data())

        self.meiLog.setChecked(self.isVisible())

        self.meiScroll.setChecked(options().logScrollMode)

    def updateShowLoggersMenu(self):
        for action in self.setLoggingSourceActions.actions():
            text = action.text()
            data = action.data()

            if (not data == 'logger'):
                continue

            if (text.startswith('Все')):
                action.setChecked(all(l.logWindow for l in log()))

                continue
                
            action.setChecked(log()[text].logWindow)

    def updateShowDevicesMenu(self):
        for action in self.setLoggingSourceActions.actions():
            text = action.text()
            data = action.data()

            if (not data == 'device'):
                continue

            if (text.startswith('Все')):
                action.setChecked(all(d.logWindow for d in hardware()))
                continue
                
            action.setChecked(hardware()[text].logWindow)

    def show(self, force: bool = False):
        if (force or not self.isVisible()):
            self.cleanUi()
            self.updateShowLoggersMenu()
            self.updateShowDevicesMenu()

            super().show()
            self.updateUi()

            self.logger.info('Открыто окно журнала')

        else:
            self.close()

    def close(self):
        super().close()
        ui().updateUi()

    def scrollDown(self):
        if (options().logScrollMode):
            c = self.txtLogDisplay.textCursor()
            c.movePosition(c.End)
            self.txtLogDisplay.setTextCursor(c)

    def setGlobalLogLevel(self):
        log().setGlobalLogLevel(self.logLevelActions.checkedAction().data())
        options().logLevel = getLevelName(self.logLevelActions.checkedAction().data())
        options().write()

        self.logger.publish(log().globalLogLevel,
            f'Глобальный уровень журнала установлен на {log().globalLogLevel.name}')

    def increaseFontSize(self):
        self.txtLogDisplay.zoomIn()
        self.logger.debug('Шрифт увеличен')
        self.scrollDown()

    def reduceFontSize(self):
        self.txtLogDisplay.zoomOut()
        self.logger.debug('Шрифт уменьшен')
        self.scrollDown()

    def setScrollingMode(self):
        value = self.meiScroll.isChecked()

        options().logScrollMode = value
        self.logger.debug(f'Автопрокрутка {"включена" if value else "отключена"}')
        self.scrollDown()
        options().write()

    def setASCIIMode(self, triggered: QtGui.QAction):
        text = triggered.text()
        isChecked = triggered.isChecked()

        if (triggered == self.allASCIIAction):
            for a in [ac for ac in self.setLoggingSourceActions.actions()
                      if (ac != self.allASCIIAction)]:
                a.setChecked(isChecked)
                hardware()[a.text()].logDecodeASCIIMode = isChecked

            options().setLogDecodeASCII('All', isChecked)
            return

        self.allASCIIAction.setChecked(all(d.decodeASCIIMode for d in hardware()))
        hardware()[text].decodeASCII = isChecked

    def setLoggerVisibility(self, triggered: QtGui.QAction):
        text = triggered.text()
        data = triggered.data()
        isChecked = triggered.isChecked()

        vendor = (log() 
                  if (data == 'logger') 
                  else hardware())
        
        config = (options().setLogWindowLoggers  
                  if (data == 'logger') else 
                  options().setLogWindowDevices)
        
        common = (self.allLoggersAction
                  if (data == 'logger') else
                  self.allDevicesAction)

        if (text.startswith('Все')):
            for a in [ac for ac in self.setLoggingSourceActions.actions()
                      if (ac.data() == data and ac != self.allASCIIAction)]:
                a.setChecked(isChecked)    
                vendor[a.text()].logWindow = isChecked
            
            config('All', isChecked)
            return
        
        common.setChecked(all(obj.logWindow for obj in vendor))
        vendor[text].logWindow = isChecked
        config(text, isChecked)

        self.updateUi()

    def openLogFolder(self):
        system('explorer logs')
        self.logger.debug('Открыта папка с журналами')

    def writeDeviceMessage(self, device):
        if (device.logWindowVisibility):
            content = device.port.readLine()
            toPrint = (str(content) if (device.decodeASCII) else str(content.toHex(' ')))

            self.txtLogDisplay.append(
                f'<span style="color:gray">{datetime.now().strftime(f"%m.%d %H:%M:%S.%f")}</span> '
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
            return

        else:
            self.cbbPort.setStyleSheet('')

        self.logger.debug(f'Пытаюсь отправить сообщение на порт {port}')

        if (hardware()[port].send(text) != -1):
            self.txtLogDisplay.append(
                f'<span style="color:gray">{datetime.now()}</span> '
                f'[Вы к <span style="color:lime">{port}</span>]: {text}')
            
        else:
            self.txtLogDisplay.append(
                f'<span style="color:gray">{datetime.now()}</span> '
                f'[Вы к <span style="color:lime">{self.cbbPort.currentText().capitalize()}</span>]: '
                f'<span style="color:red">[Не отправлено!]</span> {self.lneMessage.text()}')
            
        self.lneMessage.clear()
