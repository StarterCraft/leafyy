# -*- coding: utf-8 -*-
import logging
import sys
import os
import inspect

from webutils import formatExc
from pydantic import PositiveFloat
from colorama import Fore, Style
from datetime import datetime

from leafyy   import log, errors, properties

from .models  import Logger
from .generic import LeafyyLogLevel


class LeafyyLogger:
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


    def __init__(self, name: str, logLevel: LeafyyLogLevel = LeafyyLogLevel.DEBUG,
                                  stdPrint: bool = True,
                                  console: bool = True):
        '''
        Инициализировать один канал журналирования.

        :param `name`: `str`
            Имя канала журналирования

        :param `logLevel`: `LeafyyLogger.LogLevel` = `DEBUG`
            Необходимый уровень журналирования.

            Возможные уровни журналирования:
             —— DEBUG (все сообщения, по умолчанию);
             —— INFO (важные сообщения);
             —— WARNING (сообщения важностью 
                ПРЕДУПРЕЖДЕНИЕ и выше);
             —— ERROR (только сообщения об ошибках и
                критические сообщения);
             —— CRITICAL (только критические сообщения)

        :param `disableStdPrint`: `bool` = `False`
            По умолчанию, сообщения журнала выводятся в консоль.
            Если этот параметр истинен, то вывод в консоль не будет
            производиться
        '''
        super(LeafyyLogger, self).__init__()
        self.name = name
        self.logLevel = logLevel
        self.stdPrint = stdPrint
        self.console = console

        self.Logger = logging.getLogger(name)
        self.formatString = ''
                
        self.Logger.setLevel(self.logLevel.value)

        self.file = logging.FileHandler(f'{log().fileName}', 'a+', 'utf-8')
        self.Logger.addHandler(self.file)

        self.printer = logging.StreamHandler(sys.stdout)

        if (stdPrint):
            self.Logger.addHandler(self.printer)

        log().append(self)

    def model(self) -> Logger:
        return {
            'name': self.name,
            'level': self.logLevel,
            'live': self.console
        }

    @property
    def logWindowVisibility(self):
        return self.console
    
    @logWindowVisibility.setter
    def logWindowVisibility(self, value: bool):
        self.console = value
        properties().setlogWindowLoggers(self.name, value)

    def setLogLevel(self, logLevel: LeafyyLogLevel):
        '''
        Установить уровень журналирования.

        :param `logLevel`: `LeafyyLogger.LogLevel`
            Необходимый уровень журналирования.

            Возможные уровни журналирования:
             —— DEBUG (все сообщения, по умолчанию);
             —— INFO (важные сообщения);
             —— WARNING (сообщения важностью 
                ПРЕДУПРЕЖДЕНИЕ и выше);
             —— ERROR (только сообщения об ошибках и
                критические сообщения);
             —— CRITICAL (только критические сообщения)

        :returns: `None`
        '''
        self.logLevel = logLevel
        self.Logger.setLevel(logLevel.value)

    def record(self, time: datetime, level: str, message: str):
        'Отправить сообщение в стек'

        if (self.console):
            log().record(time, self.name, level, message)

    def asError(self, time: datetime, origin: str, caller: str, message: str):
        errors().record(time, origin, caller, message)
            
    def publish(self, value: LeafyyLogLevel | str, message: str):
        'Опубликовать сообщение с заданным уровнем.'
        if (isinstance(value, LeafyyLogLevel)):
            value = value.name

        methods = dict.fromkeys(LeafyyLogLevel._member_names_)
        for level in LeafyyLogLevel._member_names_:
            methods[level] = getattr(self, level.lower())

        methods[value](message, back = 2)

    def debug(self, message: str, back: int = 1):
        '''
        Опубликовать сообщение с уровнем `DEBUG` (ОТЛАДКА).

        :param `message`: `str`
            Текст сообщения

        :returns: `None`
        '''
        callerFrame = inspect.currentframe()

        for i in range(back):
            callerFrame = callerFrame.f_back

        fileName = callerFrame.f_code.co_filename
        lineNo = callerFrame.f_lineno
        funcName = callerFrame.f_code.co_qualname
        
        indexFrom = 0

        if ('leafyy' in fileName):
            indexFrom = fileName.split(os.path.sep).index('leafyy') + 1

        callSource = '.'.join(fileName.split(os.path.sep)[indexFrom:])[:-3]
        callSource += f'.{funcName}'

        ctime = datetime.now()

        if (self.logLevel == LeafyyLogLevel.DEBUG):
            self.formatString = ('%(asctime)s [%(name)s@%(levelname)s] '
                                 f'[{callSource} <{lineNo}>]: '
                                 '%(message)s')
        else:
            self.formatString = '%(asctime)s [%(name)s@%(levelname)s] %(message)s'

        self.file.setFormatter(logging.Formatter(self.formatString))

        if (self.logLevel == LeafyyLogLevel.DEBUG) and self.stdPrint:
            self.Logger.addHandler(self.printer)
            self.printer.setFormatter(logging.Formatter(
                f'[{Fore.GREEN}%(name)s{Style.RESET_ALL}@{Fore.BLACK}%(levelname)s{Style.RESET_ALL}]: %(message)s'
                ))
        else:
            self.Logger.removeHandler(self.printer)

        self.Logger.debug(message)

        self.record(ctime, 'DEBUG', message)

    def info(self, message: str, back: int = 1):
        '''
        Опубликовать сообщение с уровнем `INFO` (ИНФОРМАЦИЯ).

        :param `message`: `str`
            Текст сообщения

        :returns: `None`
        '''
        callerFrame = inspect.currentframe()

        for i in range(back):
            callerFrame = callerFrame.f_back

        fileName = callerFrame.f_code.co_filename
        lineNo = callerFrame.f_lineno
        funcName = callerFrame.f_code.co_qualname
        
        indexFrom = 0

        if ('leafyy' in fileName):
            indexFrom = fileName.split(os.path.sep).index('leafyy') + 1

        callSource = '.'.join(fileName.split(os.path.sep)[indexFrom:])[:-3]
        callSource += f'.{funcName}'

        ctime = datetime.now()

        if (self.logLevel == LeafyyLogLevel.DEBUG):
            self.formatString = ('%(asctime)s [%(name)s@%(levelname)s] '
                                 f'[{callSource} <{lineNo}>]: '
                                 '%(message)s')
        else:
            self.formatString = '%(asctime)s [%(name)s@%(levelname)s] %(message)s'

        self.file.setFormatter(logging.Formatter(self.formatString))

        if (self.logLevel <= LeafyyLogLevel.INFO) and self.stdPrint:
            self.Logger.addHandler(self.printer)
            self.printer.setFormatter(logging.Formatter(
                f'[{Fore.GREEN}%(name)s{Style.RESET_ALL}@{Fore.BLUE}%(levelname)s{Style.RESET_ALL}]: %(message)s'
                ))
        else:
            self.Logger.removeHandler(self.printer)

        self.Logger.info(message)
        
        self.record(ctime, 'INFO', message)
        
    def warning(self, message: str, back: int = 1, origin: str = '', exc: Exception = None):
        '''
        Опубликовать сообщение с уровнем WARNING (ПРЕДУПРЕЖДЕНИE).

        :param `message`: `str`
            Текст сообщения

        :kwparam `back`: `int` = `1`
            Количество вызовов функций, которые нужно пропустить при определении источника вызова.

        :kwparam `origin`: `str` = `''`
            Источник вызова сообщения об ошибке, если нужно опубликовать сообщение как ошибку.

        :returns: `None`
        '''
        callerFrame = inspect.currentframe()

        for i in range(back):
            callerFrame = callerFrame.f_back

        fileName = callerFrame.f_code.co_filename
        lineNo = callerFrame.f_lineno
        funcName = callerFrame.f_code.co_qualname
        
        indexFrom = 0

        if ('leafyy' in fileName):
            indexFrom = fileName.split(os.path.sep).index('leafyy') + 1

        callSource = '.'.join(fileName.split(os.path.sep)[indexFrom:])[:-3]
        callSource += f'.{funcName}'

        ctime = datetime.now()

        if (self.logLevel == LeafyyLogLevel.DEBUG):
            self.formatString = ('%(asctime)s [%(name)s@%(levelname)s] '
                                 f'[{callSource} <{lineNo}>]: '
                                 '%(message)s')
        else:
            self.formatString = '%(asctime)s [%(name)s@%(levelname)s] %(message)s'

        self.file.setFormatter(logging.Formatter(self.formatString))

        if (self.logLevel <= LeafyyLogLevel.WARNING and self.stdPrint):
            self.Logger.addHandler(self.printer)
            self.printer.setFormatter(logging.Formatter(
                f'[{Fore.GREEN}%(name)s{Style.RESET_ALL}@{Fore.YELLOW}%(levelname)s{Style.RESET_ALL}]: %(message)s'
                ))
        else:
            self.Logger.removeHandler(self.printer)

        excStr = '\n' + formatExc(exc) if (exc) else ''

        self.Logger.warning(message + excStr)

        self.record(ctime, 'WARNING', message + excStr)
        
        if (origin):
            self.asError(ctime.timestamp(), origin, funcName, message + excStr)
        
    def error(self, message: str, back: int = 1, origin: str = '', exc: Exception = None):
        '''
        Опубликовать сообщение с уровнем ERROR (ОШИБКА).

        :param `message`: `str`
            Текст сообщения

        :kwparam `back`: `int` = `1`
            Количество вызовов функций, которые нужно пропустить при определении источника вызова.

        :kwparam `origin`: `str` = `''`
            Источник вызова сообщения об ошибке, если нужно опубликовать сообщение как ошибку.

        :returns: `None`
        '''
        callerFrame = inspect.currentframe()

        for i in range(back):
            callerFrame = callerFrame.f_back

        fileName = callerFrame.f_code.co_filename
        lineNo = callerFrame.f_lineno
        funcName = callerFrame.f_code.co_qualname
        
        indexFrom = 0

        if ('leafyy' in fileName):
            indexFrom = fileName.split(os.path.sep).index('leafyy') + 1

        callSource = '.'.join(fileName.split(os.path.sep)[indexFrom:])[:-3]
        callSource += f'.{funcName}'

        ctime = datetime.now()

        if (self.logLevel == LeafyyLogLevel.DEBUG):
            self.formatString = ('%(asctime)s [%(name)s@%(levelname)s] '
                                 f'[{callSource} <{lineNo}>]: '
                                 '%(message)s')
        else:
            self.formatString = '%(asctime)s [%(name)s@%(levelname)s] %(message)s'

        self.file.setFormatter(logging.Formatter(self.formatString))
        
        if (self.logLevel <= LeafyyLogLevel.ERROR and self.stdPrint):
            self.Logger.addHandler(self.printer)
            self.printer.setFormatter(logging.Formatter(
                f'[{Fore.GREEN}%(name)s{Style.RESET_ALL}@{Fore.RED}%(levelname)s{Style.RESET_ALL}]: %(message)s'
                ))
        else:
            self.Logger.removeHandler(self.printer)
            
        excStr = '\n' + formatExc(exc) if (exc) else ''

        self.Logger.error(message + excStr)

        self.record(ctime, 'ERROR', message + excStr)        

        if (origin):
            self.asError(ctime, origin, funcName, message + excStr)
          
    def critical(self, message: str, back: int = 1, origin: str = '', exc: Exception = None):
        '''
        Опубликовать сообщение с уровнем CRITICAL (КРИТИЧЕСКИЙ).

        :param `message`: `str`
            Текст сообщения

        :kwparam `back`: `int` = `1`
            Количество вызовов функций, которые нужно пропустить при определении источника вызова.

        :kwparam `origin`: `str` = `''`
            Источник вызова сообщения об ошибке, если нужно опубликовать сообщение как ошибку.

        :returns: `None`
        '''
        callerFrame = inspect.currentframe()

        for i in range(back):
            callerFrame = callerFrame.f_back

        fileName = callerFrame.f_code.co_filename
        lineNo = callerFrame.f_lineno
        funcName = callerFrame.f_code.co_qualname
        
        indexFrom = 0

        if ('leafyy' in fileName):
            indexFrom = fileName.split(os.path.sep).index('leafyy') + 1

        callSource = '.'.join(fileName.split(os.path.sep)[indexFrom:])[:-3]
        callSource += f'.{funcName}'

        ctime = datetime.now()

        if (self.logLevel == LeafyyLogLevel.DEBUG):
            self.formatString = ('%(asctime)s [%(name)s@%(levelname)s] '
                                 f'[{callSource} <{lineNo}>]: '
                                 '%(message)s')
        else:
            self.formatString = '%(asctime)s [%(name)s@%(levelname)s] %(message)s'

        self.file.setFormatter(logging.Formatter(self.formatString))
        
        if (self.logLevel <= LeafyyLogLevel.CRITICAL and self.stdPrint):
            self.Logger.addHandler(self.printer)
            self.printer.setFormatter(logging.Formatter(
                f'[{Fore.GREEN}%(name)s{Style.RESET_ALL}@{Fore.RED}%(levelname)s{Style.RESET_ALL}]: %(message)s'
                ))
        else:
            self.Logger.removeHandler(self.printer)
            
        excStr = '\n' + formatExc(exc) if (exc) else ''

        self.Logger.critical(message + excStr)

        self.record(ctime, 'CRITICAL', message + excStr) 
        
        if (origin):
            self.asError(ctime.timestamp(), origin, funcName, message + excStr)
