import logging
import os
import time

from colorama import Fore, Style


class AqLogger:
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
    class LogLevel:
        'Объект для представления уровня журналирования'
        def __init__(self, lm: int):
            self._level = lm


        def __repr__(self):
            repr(self._level)


        def __eq__(self, other):
            if not hasattr(other, '_level'):
                return self._level == other
            else: return self._level == other._level


        def __gt__(self, other):
            if not hasattr(other, '_level'):
                return self._level > other
            else: return self._level > other._level


        def __lt__(self, other):
            if not hasattr(other, '_level'):
                return self._level < other
            else: return self._level < other._level


        def __ge__(self, other):
            if not hasattr(other, '_level'):
                return self._level >= other
            else: return self._level >= other._level


        def __le__(self, other):
            if not hasattr(other, '_level'):
                return self._level <= other
            else: return self._level <= other._level


    #Возможные уровни журналирования:
    DEBUG = LogLevel(logging.DEBUG)       #Уровень ОТЛАДКА (все сообщения, по умолчанию)
    INFO = LogLevel(logging.INFO)         #Уровень ИНФОРМАЦИЯ (важные сообщения)

    WARNING = LogLevel(logging.WARNING)   #Уровень ПРЕДУПРЕЖДЕНИЯ (сообщения важностью
                                          #ПРЕДУПРЕЖДЕНИЕ и выше)

    ERROR = LogLevel(logging.ERROR)       #Уровень ОШИБКИ (только сообщения об ошибках и
                                          #критические сообщения)

    CRITICAL = LogLevel(logging.CRITICAL) #Уровень ТОЛЬКО КРИТИЧЕСКИЕ (только критические
                                          #сообщения)


    def __init__(self, name: str, logLevel: LogLevel = DEBUG,
                                  disableStdPrint: bool = False,
                                  useColorama = 1):
        '''
        Инициализировать один канал журналирования.

        :param 'name': str
            Имя канала журналирования

        :param 'logLevel': AqLogger.LogLevel = DEBUG
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
            Если этот параметр ложен, то вывод в консоль не будет
            производиться

        :param 'useColorama': int = 1
            Использовать ли цветной текст Colorama, и если да, то
            как. Имеются следующие варианты:
            0 —— отключить использование цветного текста;
            1 —— использовать цветной текст для вывода
                 сообщений в консоль;
            2 —— использовать цветной текст для вывода
                 сообщений в консоль и для файла журнала
        '''
        self.name, self.logLevel, self.printDsb, self.useColorama = name, logLevel, disableStdPrint, useColorama
        self.filenames = list()

        self.Logger = logging.getLogger(name)
        self.formatString = ''
        self.getFilename()
        
        self.Logger.setLevel(self.logLevel._level)

        self.handler = logging.FileHandler(rf'{self.filenames[0]}', 'a+', 'utf-8')
        self.Logger.addHandler(self.handler)


    def setLogLevel(self, logLevel: LogLevel):
        '''
        Установить уровень журналирования.

        :param 'logLevel': AqLogger.LogLevel
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
        self.Logger.setLevel(logLevel._level)


    def getFilename(self):
        '''
        Сгенерировать имя файла для сохранения лога и сохранить его в список
        'self.filenames'. Метод вызывается при инициализации канала журнали-
        рования, но при этом для сохранения логов всегда используется файл с
        именем, которое было получено при инициализации ПЕРВОГО по счёту
        канала.

        :returns: None
        '''
        self.filenames.append(f'logs/{(time.strftime("""%d.%m.%Y_%H%M%S""", time.localtime()))}_AsQammLog.log')


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

        if self.useColorama <= 1 and self.logLevel == self.DEBUG:
            self.formatString = ('{%(asctime)s} [%(name)s:%(levelname)s] '
                                 f'[{fileName} <{lineNo}>: {moduleName}.{funcName}]: '
                                 '%(message)s')
        elif self.useColorama <= 1 and self.logLevel >= self.INFO:
            self.formatString = '{%(asctime)s} [%(name)s:%(levelname)s] %(message)s'

        elif self.useColorama == 2 and self.logLevel == self.DEBUG:
            self.formatString = (str(Fore.CYAN)   +  '{%(asctime)s} [' + str(Style.RESET_ALL) +
                                 str(Fore.GREEN)  +   '%(name)s'       + str(Style.RESET_ALL) + ':'   +
                                 str(Fore.YELLOW) +   '%(levelname)s'  + str(Style.RESET_ALL) + '] [' +
                                 str(Fore.BLUE)   +   fileName         + str(Style.RESET_ALL) + ' <'  +
                                 str(Fore.WHITE)  +   lineNo           + str(Style.RESET_ALL) + '>: ' +
                                 str(Fore.BLUE)   +   moduleName       + str(Style.RESET_ALL) + '.'   +
                                                      funcName         + ': %(message)s')

        elif self.useColorama == 2 and self.logLevel >= self.INFO:
            self.formatString = (str(Fore.CYAN)   +  '{%(asctime)s} [' + str(Style.RESET_ALL) +
                                 str(Fore.GREEN)  +   '%(name)s'       + str(Style.RESET_ALL) + ':'   +
                                 str(Fore.YELLOW) +   '%(levelname)s'  + str(Style.RESET_ALL) + '] [' +
                                 str(Fore.BLUE)   +   moduleName       + str(Style.RESET_ALL) + '.'   + 
                                                      funcName + ': %(message)s')
        self.handler.setFormatter(logging.Formatter(self.formatString))

        self.Logger.debug(message)
        if self.logLevel == self.DEBUG and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}DEBUG{Style.RESET_ALL}]: {message}')
        

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

        if self.useColorama <= 1 and self.logLevel == self.DEBUG:
            self.formatString = ('{%(asctime)s} [%(name)s:%(levelname)s] '
                                 f'[{fileName} <{lineNo}>: {moduleName}.{funcName}]: '
                                 '%(message)s')
        elif self.useColorama <= 1 and self.logLevel >= self.INFO:
            self.formatString = '{%(asctime)s} [%(name)s:%(levelname)s] %(message)s'

        elif self.useColorama == 2 and self.logLevel == self.DEBUG:
            self.formatString = (str(Fore.CYAN)   +  '{%(asctime)s} [' + str(Style.RESET_ALL) +
                                 str(Fore.GREEN)  +   '%(name)s'       + str(Style.RESET_ALL) + ':'   +
                                 str(Fore.YELLOW) +   '%(levelname)s'  + str(Style.RESET_ALL) + '] [' +
                                 str(Fore.BLUE)   +   fileName         + str(Style.RESET_ALL) + ' <'  +
                                 str(Fore.WHITE)  +   lineNo           + str(Style.RESET_ALL) + '>: ' +
                                 str(Fore.BLUE)   +   moduleName       + str(Style.RESET_ALL) + '.'   +
                                                      funcName         + ': %(message)s')

        elif self.useColorama == 2 and self.logLevel >= self.INFO:
            self.formatString = (str(Fore.CYAN)   +  '{%(asctime)s} [' + str(Style.RESET_ALL) +
                                 str(Fore.GREEN)  +   '%(name)s'       + str(Style.RESET_ALL) + ':'   +
                                 str(Fore.YELLOW) +   '%(levelname)s'  + str(Style.RESET_ALL) + '] [' +
                                 str(Fore.BLUE)   +   moduleName       + str(Style.RESET_ALL) + '.'   + 
                                                      funcName + ': %(message)s')
        self.handler.setFormatter(logging.Formatter(self.formatString))

        self.Logger.info(message)
        if self.logLevel <= self.INFO and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}INFO{Style.RESET_ALL}]: {message}')


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

        if self.useColorama <= 1 and self.logLevel == self.DEBUG:
            self.formatString = ('{%(asctime)s} [%(name)s:%(levelname)s] '
                                 f'[{fileName} <{lineNo}>: {moduleName}.{funcName}]: '
                                 '%(message)s')
        elif self.useColorama <= 1 and self.logLevel >= self.INFO:
            self.formatString = '{%(asctime)s} [%(name)s:%(levelname)s] %(message)s'

        elif self.useColorama == 2 and self.logLevel == self.DEBUG:
            self.formatString = (str(Fore.CYAN)   +  '{%(asctime)s} [' + str(Style.RESET_ALL) +
                                 str(Fore.GREEN)  +   '%(name)s'       + str(Style.RESET_ALL) + ':'   +
                                 str(Fore.YELLOW) +   '%(levelname)s'  + str(Style.RESET_ALL) + '] [' +
                                 str(Fore.BLUE)   +   fileName         + str(Style.RESET_ALL) + ' <'  +
                                 str(Fore.WHITE)  +   lineNo           + str(Style.RESET_ALL) + '>: ' +
                                 str(Fore.BLUE)   +   moduleName       + str(Style.RESET_ALL) + '.'   +
                                                      funcName         + ': %(message)s')

        elif self.useColorama == 2 and self.logLevel >= self.INFO:
            self.formatString = (str(Fore.CYAN)   +  '{%(asctime)s} [' + str(Style.RESET_ALL) +
                                 str(Fore.GREEN)  +   '%(name)s'       + str(Style.RESET_ALL) + ':'   +
                                 str(Fore.YELLOW) +   '%(levelname)s'  + str(Style.RESET_ALL) + '] [' +
                                 str(Fore.BLUE)   +   moduleName       + str(Style.RESET_ALL) + '.'   + 
                                                      funcName + ': %(message)s')
        self.handler.setFormatter(logging.Formatter(self.formatString))

        self.Logger.warning(message)
        if self.logLevel <= self.WARNING and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}WARN{Style.RESET_ALL}]: {message}')


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

        if self.useColorama <= 1 and self.logLevel == self.DEBUG:
            self.formatString = ('{%(asctime)s} [%(name)s:%(levelname)s] '
                                 f'[{fileName} <{lineNo}>: {moduleName}.{funcName}]: '
                                 '%(message)s')
        elif self.useColorama <= 1 and self.logLevel >= self.INFO:
            self.formatString = '{%(asctime)s} [%(name)s:%(levelname)s] %(message)s'

        elif self.useColorama == 2 and self.logLevel == self.DEBUG:
            self.formatString = (str(Fore.CYAN)   +  '{%(asctime)s} [' + str(Style.RESET_ALL) +
                                 str(Fore.GREEN)  +   '%(name)s'       + str(Style.RESET_ALL) + ':'   +
                                 str(Fore.YELLOW) +   '%(levelname)s'  + str(Style.RESET_ALL) + '] [' +
                                 str(Fore.BLUE)   +   fileName         + str(Style.RESET_ALL) + ' <'  +
                                 str(Fore.WHITE)  +   lineNo           + str(Style.RESET_ALL) + '>: ' +
                                 str(Fore.BLUE)   +   moduleName       + str(Style.RESET_ALL) + '.'   +
                                                      funcName         + ': %(message)s')

        elif self.useColorama == 2 and self.logLevel >= self.INFO:
            self.formatString = (str(Fore.CYAN)   +  '{%(asctime)s} [' + str(Style.RESET_ALL) +
                                 str(Fore.GREEN)  +   '%(name)s'       + str(Style.RESET_ALL) + ':'   +
                                 str(Fore.YELLOW) +   '%(levelname)s'  + str(Style.RESET_ALL) + '] [' +
                                 str(Fore.BLUE)   +   moduleName       + str(Style.RESET_ALL) + '.'   + 
                                                      funcName + ': %(message)s')
        self.handler.setFormatter(logging.Formatter(self.formatString))

        self.Logger.error(message)
        if self.logLevel <= self.ERROR and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}ERROR{Style.RESET_ALL}]: {message}')


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

        if self.useColorama <= 1 and self.logLevel == self.DEBUG:
            self.formatString = ('{%(asctime)s} [%(name)s:%(levelname)s] '
                                 f'[{fileName} <{lineNo}>: {moduleName}.{funcName}]: '
                                 '%(message)s')
        elif self.useColorama <= 1 and self.logLevel >= self.INFO:
            self.formatString = '{%(asctime)s} [%(name)s:%(levelname)s] %(message)s'

        elif self.useColorama == 2 and self.logLevel == self.DEBUG:
            self.formatString = (str(Fore.CYAN)   +  '{%(asctime)s} [' + str(Style.RESET_ALL) +
                                 str(Fore.GREEN)  +   '%(name)s'       + str(Style.RESET_ALL) + ':'   +
                                 str(Fore.YELLOW) +   '%(levelname)s'  + str(Style.RESET_ALL) + '] [' +
                                 str(Fore.BLUE)   +   fileName         + str(Style.RESET_ALL) + ' <'  +
                                 str(Fore.WHITE)  +   lineNo           + str(Style.RESET_ALL) + '>: ' +
                                 str(Fore.BLUE)   +   moduleName       + str(Style.RESET_ALL) + '.'   +
                                                      funcName         + ': %(message)s')

        elif self.useColorama == 2 and self.logLevel >= self.INFO:
            self.formatString = (str(Fore.CYAN)   +  '{%(asctime)s} [' + str(Style.RESET_ALL) +
                                 str(Fore.GREEN)  +   '%(name)s'       + str(Style.RESET_ALL) + ':'   +
                                 str(Fore.YELLOW) +   '%(levelname)s'  + str(Style.RESET_ALL) + '] [' +
                                 str(Fore.BLUE)   +   moduleName       + str(Style.RESET_ALL) + '.'   + 
                                                      funcName + ': %(message)s')
        self.handler.setFormatter(logging.Formatter(self.formatString))
        
        self.Logger.critical(message)
        if self.logLevel <= self.CRITICAL and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}CRITICAL{Style.RESET_ALL}]: {message}')

    def exception(self, _exception: Exception):
        '''
        Опубликовать сообщение о возникновении исключения

        :param '_exception': Exception
            Объект исключения.

        :returns: None
        '''
        print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}CRITICAL{Style.RESET_ALL}]: '
              f'Программа аварийно завершила работу из-за исклоючения {type(_exception)}:')
        self.Logger.exception(f'Программа аварийно завершила работу из-за исклоючения {type(_exception)}:',
                                exc_info = _exception)


    @staticmethod
    def openLogFolder():
        '''
        Открыть папку с файлами журналов.

        :returns: None
        '''
        os.system('explorer logs')
