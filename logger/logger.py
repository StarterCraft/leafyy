#coding=utf-8
import logging
import os
import time

from greenyy      import ui, log, options
from enum     import Enum
from colorama import Fore, Style
from datetime import datetime


class GreenyyLogLevel(Enum):
    'Объект для представления уровня журналирования'

    #Возможные уровни журналирования:
    DEBUG = logging.DEBUG       #Уровень ОТЛАДКА (все сообщения, по умолчанию)
    INFO = logging.INFO         #Уровень ИНФОРМАЦИЯ (важные сообщения)
    WARNING = logging.WARNING   #Уровень ПРЕДУПРЕЖДЕНИЯ (сообщения важностью
                                #ПРЕДУПРЕЖДЕНИЕ и выше)
    ERROR = logging.ERROR       #Уровень ОШИБКИ (только сообщения об ошибках и
                                #критические сообщения)
    CRITICAL = logging.CRITICAL #Уровень ТОЛЬКО КРИТИЧЕСКИЕ (только критические
                                #сообщения)

    #Спасибо ChatGPT
    def __lt__(self, other):
        if isinstance(other, GreenyyLogLevel):
            return self.value < other.value
        elif isinstance(other, int):
            return self.value < other
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, GreenyyLogLevel):
            return self.value <= other.value
        elif isinstance(other, int):
            return self.value <= other
        return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, GreenyyLogLevel):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, GreenyyLogLevel):
            return self.value != other.value
        elif isinstance(other, int):
            return self.value != other
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, GreenyyLogLevel):
            return self.value > other.value
        elif isinstance(other, int):
            return self.value > other
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, GreenyyLogLevel):
            return self.value >= other.value
        elif isinstance(other, int):
            return self.value >= other
        return NotImplemented


class GreenyyLogger:
    '''
    Класс канала журналирования.

    Журналирование необходимо для отборажения пользователю информацию о 
    текущих действиях сервера, сообщения о предупреждениях и об ошибках.

    Каналов журналирования (или `логгеров`) может быть сколько угодно.
    При этом итоговый журнал всегда сохраняется в ОДИН файл, имя которого
    определяется при запуске самого ПЕРВОГО канала журналирования.
    Каждый из этих каналов имеет своё имя и настраивается по уровню жур-
    налирования (насколько важные сообщения нужно выводить в консоль и
    сохранять в журнал?).

    Любые файлы журналов сохраняются в папке
    '{папка местонаждения программы}/logs'.
    '''


    def __init__(self, name: str, logLevel: GreenyyLogLevel = GreenyyLogLevel.DEBUG,
                                  disableStdPrint: bool = False,
                                  disableLogWindow: bool = False,
                                  useColorama = 1):
        '''
        Инициализировать один канал журналирования.

        :param 'name': str
            Имя канала журналирования

        :param 'logLevel': GreenyyLogger.LogLevel = DEBUG
            Необходимый уровень журналирования.

            Возможные уровни журналирования:
             —— DEBUG (все сообщения, по умолчанию);
             —— INFO (важные сообщения);
             —— WARNING (сообщения важностью 
                ПРЕДУПРЕЖДЕНИЕ и выше);
             —— ERROR (только сообщения об ошибках и
                критические сообщения);
             —— CRITICAL (только критические сообщения)

        :param 'disableStdPrint': bool = False
            По умолчанию, сообщения журнала выводятся в консоль.
            Если этот параметр истинен, то вывод в консоль не будет
            производиться

        :param 'useColorama': int = 1
            Использовать ли цветной текст Colorama, и если да, то
            как. Имеются следующие варианты:
            0 —— отключить использование цветного текста;
            1 —— использовать цветной текст для вывода
                 сообщений в консоль
        '''
        super(GreenyyLogger, self).__init__()
        self.name = name
        self.logLevel = logLevel
        self.printDsb = disableStdPrint
        self.logWindow = not disableLogWindow
        self.useColorama = useColorama
        self.filenames = list()

        self.Logger = logging.getLogger(name)
        self.formatString = ''
        self.getFilename()
                
        self.Logger.setLevel(self.logLevel.value)

        self.handler = logging.FileHandler(rf'{self.filenames[0]}', 'a+', 'utf-8')
        
        self.Logger.addHandler(self.handler)

        log().add(self)

    @property
    def logWindowVisibility(self):
        return self.logWindow
    
    @logWindowVisibility.setter
    def logWindowVisibility(self, value: bool):
        self.logWindow = value
        options().setlogWindowLoggers(self.name, value)

    def setLogLevel(self, logLevel: GreenyyLogLevel):
        '''
        Установить уровень журналирования.

        :param 'logLevel': GreenyyLogger.LogLevel
            Необходимый уровень журналирования.

            Возможные уровни журналирования:
             —— DEBUG (все сообщения, по умолчанию);
             —— INFO (важные сообщения);
             —— WARNING (сообщения важностью 
                ПРЕДУПРЕЖДЕНИЕ и выше);
             —— ERROR (только сообщения об ошибках и
                критические сообщения);
             —— CRITICAL (только критические сообщения)

        :returns: None
        '''
        self.logLevel = logLevel
        self.Logger.setLevel(logLevel.value)

    def getFilename(self):
        '''
        Сгенерировать имя файла для сохранения лога и сохранить его в список
        'self.filenames'. Метод вызывается при инициализации канала журнали-
        рования, но при этом для сохранения логов всегда используется файл с
        именем, которое было получено при инициализации ПЕРВОГО по счёту
        канала.

        :returns: None
        '''
        self.filenames.append(f'logs/Greenyy_{time.strftime("""%d.%m.%Y_%H%M%S""", time.localtime())}.log')

    def publishToLogWindow(self, message: str):
        'Отправить сообщение в LogWindow'
        if (self.logWindow):
            try:
                ui().logWindow.txtLogDisplay.append(message)
                ui().logWindow.scrollDown()
            except:
                return
            
    def publish(self, value: GreenyyLogLevel, message: str):
        'Опубликовать сообщение с заданным уровнем.'
        methods = dict.fromkeys(GreenyyLogLevel)
        for level in GreenyyLogLevel:
            methods[level] = getattr(self, level.name)

        methods[value](message)

    def debug(self, message: str):
        '''
        Опубликовать сообщение с уровнем DEBUG (ОТЛАДКА).

        :param 'message': str
            Текст сообщения

        :returns: None
        '''
        callerInfo = self.Logger.findCaller()
        fileName = callerInfo[0]
        lineNo = str(callerInfo[1])
        moduleName = ('UNKNOWN' if callerInfo[0] == '(unknown file)' else callerInfo[0][:callerInfo[0].index('.')])
        funcName = callerInfo[2]

        if self.useColorama <= 1 and self.logLevel == GreenyyLogLevel.DEBUG:
            self.formatString = ('{%(asctime)s} [%(name)s:%(levelname)s] '
                                 f'[{fileName} <{lineNo}>: {moduleName}.{funcName}]: '
                                 '%(message)s')
        elif self.useColorama <= 1 and self.logLevel >= GreenyyLogLevel.INFO:
            self.formatString = '{%(asctime)s} [%(name)s:%(levelname)s] %(message)s'
            
            self.formatString = (str(Fore.CYAN)   +  '{%(asctime)s} [' + str(Style.RESET_ALL) +
                                 str(Fore.GREEN)  +   '%(name)s'       + str(Style.RESET_ALL) + ':'   +
                                 str(Fore.YELLOW) +   '%(levelname)s'  + str(Style.RESET_ALL) + '] [' +
                                 str(Fore.BLUE)   +   moduleName       + str(Style.RESET_ALL) + '.'   + 
                                                      funcName + ': %(message)s')
        self.handler.setFormatter(logging.Formatter(self.formatString))

        self.Logger.debug(message)
        if self.logLevel == GreenyyLogLevel.DEBUG and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}DEBUG{Style.RESET_ALL}]: {message}')

        self.publishToLogWindow(
            f'<span style="color:gray">{datetime.now().strftime(f"%m.%d %H:%M:%S.%f")}</span> '
            f'[<span style="color:green">{self.name}</span>'
            f'@<span style="color:darkgray">DEBUG</span>]: {message}')

    def info(self, message: str):
        '''
        Опубликовать сообщение с уровнем INFO (ИНФОРМАЦИЯ).

        :param 'message': str
            Текст сообщения

        :returns: None
        '''
        callerInfo = self.Logger.findCaller()
        fileName = callerInfo[0]
        lineNo = str(callerInfo[1])
        moduleName = ('UNKNOWN' if callerInfo[0] == '(unknown file)' else callerInfo[0][:callerInfo[0].index('.')])
        funcName = callerInfo[2]

        if self.useColorama <= 1 and self.logLevel == GreenyyLogLevel.DEBUG:
            self.formatString = ('{%(asctime)s} [%(name)s:%(levelname)s] '
                                 f'[{fileName} <{lineNo}>: {moduleName}.{funcName}]: '
                                 '%(message)s')
        elif self.useColorama <= 1 and self.logLevel >= GreenyyLogLevel.INFO:
            self.formatString = '{%(asctime)s} [%(name)s:%(levelname)s] %(message)s'

        self.handler.setFormatter(logging.Formatter(self.formatString))

        self.Logger.info(message)
        if self.logLevel <= GreenyyLogLevel.INFO and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}INFO{Style.RESET_ALL}]: {message}')

        self.publishToLogWindow(
            f'<span style="color:gray">{datetime.now().strftime(f"%m.%d %H:%M:%S.%f")}</span> '
            f'[<span style="color:green">{self.name}</span>'
            f'@<span style="color:blue">INFO</span>]: {message}')
        
    def warning(self, message: str):
        '''
        Опубликовать сообщение с уровнем WARNING (ПРЕДУПРЕЖДЕНИE).

        :param 'message': str
            Текст сообщения

        :returns: None
        '''
        callerInfo = self.Logger.findCaller()
        fileName = callerInfo[0]
        lineNo = str(callerInfo[1])
        moduleName = ('UNKNOWN' if callerInfo[0] == '(unknown file)' else callerInfo[0][:callerInfo[0].index('.')])
        funcName = callerInfo[2]

        if self.useColorama <= 1 and self.logLevel == GreenyyLogLevel.DEBUG:
            self.formatString = ('{%(asctime)s} [%(name)s:%(levelname)s] '
                                 f'[{fileName} <{lineNo}>: {moduleName}.{funcName}]: '
                                 '%(message)s')
        elif self.useColorama <= 1 and self.logLevel >= GreenyyLogLevel.INFO:
            self.formatString = '{%(asctime)s} [%(name)s:%(levelname)s] %(message)s'

        self.handler.setFormatter(logging.Formatter(self.formatString))

        self.Logger.warning(message)
        if self.logLevel <= GreenyyLogLevel.WARNING and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}WARN{Style.RESET_ALL}]: {message}')

        self.publishToLogWindow(
            f'<span style="color:gray">{datetime.now().strftime(f"%m.%d %H:%M:%S.%f")}</span> '
            f'[<span style="color:green">{self.name}</span>'
            f'@<span style="color:orange">WARN</span>]: {message}')
        
    def error(self, message: str):
        '''
        Опубликовать сообщение с уровнем ERROR (ОШИБКА).

        :param 'message': str
            Текст сообщения

        :returns: None
        '''
        callerInfo = self.Logger.findCaller()
        fileName = callerInfo[0]
        lineNo = str(callerInfo[1])
        moduleName = ('UNKNOWN' if callerInfo[0] == '(unknown file)' else callerInfo[0][:callerInfo[0].index('.')])
        funcName = callerInfo[2]

        if self.useColorama <= 1 and self.logLevel == GreenyyLogLevel.DEBUG:
            self.formatString = ('{%(asctime)s} [%(name)s:%(levelname)s] '
                                 f'[{fileName} <{lineNo}>: {moduleName}.{funcName}]: '
                                 '%(message)s')
        elif self.useColorama <= 1 and self.logLevel >= GreenyyLogLevel.INFO:
            self.formatString = '{%(asctime)s} [%(name)s:%(levelname)s] %(message)s'

        self.handler.setFormatter(self.formatString)

        self.Logger.error(message)
        if self.logLevel <= GreenyyLogLevel.ERROR and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}ERROR{Style.RESET_ALL}]: {message}')

        self.publishToLogWindow(
            f'<span style="color:gray">{datetime.now().strftime(f"%m.%d %H:%M:%S.%f")}</span> '
            f'[<span style="color:green">{self.name}</span>'
            f'@<span style="color:red">ERROR</span>]: {message}')
        
    def critical(self, message: str):
        '''
        Опубликовать сообщение с уровнем CRITICAL (КРИТИЧЕСКИЙ).

        :param 'message': str
            Текст сообщения

        :returns: None
        '''
        callerInfo = self.Logger.findCaller()
        fileName = callerInfo[0]
        lineNo = str(callerInfo[1])
        moduleName = ('UNKNOWN' if callerInfo[0] == '(unknown file)' else callerInfo[0][:callerInfo[0].index('.')])
        funcName = callerInfo[2]

        if self.useColorama <= 1 and self.logLevel == GreenyyLogLevel.DEBUG:
            self.formatString = ('{%(asctime)s} [%(name)s:%(levelname)s] '
                                 f'[{fileName} <{lineNo}>: {moduleName}.{funcName}]: '
                                 '%(message)s')
        elif self.useColorama <= 1 and self.logLevel >= GreenyyLogLevel.INFO:
            self.formatString = '{%(asctime)s} [%(name)s:%(levelname)s] %(message)s'
            
        self.handler.setFormatter(logging.Formatter(self.formatString))
        
        self.Logger.critical(message)
        if self.logLevel <= GreenyyLogLevel.CRITICAL and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}CRITICAL{Style.RESET_ALL}]: {message}')

        self.publishToLogWindow(
            f'<span style="color:gray">{datetime.now().strftime(f"%m.%d %H:%M:%S.%f")}</span> '
            f'[<span style="color:green">{self.name}</span>'
            f'@<span style="color:magenta">CRITICAL</span>]: {message}')
        
    def exception(self, _exception: Exception):
        '''
        Опубликовать сообщение о возникновении исключения

        :param '_exception': Exception
            Объект исключения.

        :returns: None
        '''
        print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}CRITICAL{Style.RESET_ALL}]: '
              f'Программа аварийно завершила работу из-за исключения {type(_exception)}:')
        self.Logger.exception(f'Программа аварийно завершила работу из-за исклоючения {type(_exception)}:',
                                exc_info = _exception)
        
        self.publishToLogWindow(
            f'<span style="color:gray">{datetime.now().strftime(f"%m.%d %H:%M:%S.%f")}</span> '
            f'[<span style="color:green">{self.name}</span>'
            f'@<span style="color:brown">EXCEPTION</span>]: '
            f'Программа аварийно завершила работу из-за исключения {type(_exception)}:')

    @staticmethod
    def openLogFolder():
        '''
        Открыть папку с файлами журналов.

        :returns: None
        '''
        os.system('explorer logs')
