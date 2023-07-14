# -*- coding: utf-8 -*-
#coding=utf-8
import logging
import os
import time
import inspect

from leafyy         import log, options
from enum           import Enum
from colorama       import Fore, Style
from datetime       import datetime

from .models import Logger


class LeafyyLogLevel(Enum):
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
        if isinstance(other, LeafyyLogLevel):
            return self.value < other.value
        elif isinstance(other, int):
            return self.value < other
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, LeafyyLogLevel):
            return self.value <= other.value
        elif isinstance(other, int):
            return self.value <= other
        return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, LeafyyLogLevel):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, LeafyyLogLevel):
            return self.value != other.value
        elif isinstance(other, int):
            return self.value != other
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, LeafyyLogLevel):
            return self.value > other.value
        elif isinstance(other, int):
            return self.value > other
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, LeafyyLogLevel):
            return self.value >= other.value
        elif isinstance(other, int):
            return self.value >= other
        return NotImplemented


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

        :param 'name': str
            Имя канала журналирования

        :param 'logLevel': LeafyyLogger.LogLevel = DEBUG
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
        '''
        super(LeafyyLogger, self).__init__()
        self.name = name
        self.logLevel = logLevel
        self.printDsb = not stdPrint
        self.console = console

        self.Logger = logging.getLogger(name)
        self.formatString = ''
                
        self.Logger.setLevel(self.logLevel.value)

        self.handler = logging.FileHandler(rf'{log().fileName}', 'a+', 'utf-8')
        
        self.Logger.addHandler(self.handler)

        log().add(self)

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
        options().setlogWindowLoggers(self.name, value)

    def setLogLevel(self, logLevel: LeafyyLogLevel):
        '''
        Установить уровень журналирования.

        :param 'logLevel': LeafyyLogger.LogLevel
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

    def toBuffer(self, message: str):
        'Отправить сообщение в стек'
        if (self.console):
            log().toBuffer(message)
            
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
        Опубликовать сообщение с уровнем DEBUG (ОТЛАДКА).

        :param 'message': str
            Текст сообщения

        :returns: None
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

        if self.logLevel == LeafyyLogLevel.DEBUG:
            self.formatString = ('%(asctime)s [%(name)s@%(levelname)s] '
                                 f'[{callSource} <{lineNo}>]: '
                                 '%(message)s')
        else:
            self.formatString = '%(asctime)s [%(name)s@%(levelname)s] %(message)s'

        self.handler.setFormatter(logging.Formatter(self.formatString))

        self.Logger.debug(message)
        if self.logLevel == LeafyyLogLevel.DEBUG and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}DEBUG{Style.RESET_ALL}]: {message}')

        self.toBuffer(
            f'<span style="color:gray">{datetime.now().strftime(f"%m.%d %H:%M:%S.%f")}</span> '
            f'[<span style="color:green">{self.name}</span>'
            f'@<span style="color:darkgray">DEBUG</span>]: {message}')

    def info(self, message: str, back: int = 1):
        '''
        Опубликовать сообщение с уровнем INFO (ИНФОРМАЦИЯ).

        :param 'message': str
            Текст сообщения

        :returns: None
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

        if self.logLevel == LeafyyLogLevel.DEBUG:
            self.formatString = ('%(asctime)s [%(name)s@%(levelname)s] '
                                 f'[{callSource} <{lineNo}>]: '
                                 '%(message)s')
        else:
            self.formatString = '%(asctime)s [%(name)s@%(levelname)s] %(message)s'

        self.handler.setFormatter(logging.Formatter(self.formatString))

        self.Logger.info(message)
        if self.logLevel <= LeafyyLogLevel.INFO and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}INFO{Style.RESET_ALL}]: {message}')

        self.toBuffer(
            f'<span style="color:gray">{datetime.now().strftime(f"%m.%d %H:%M:%S.%f")}</span> '
            f'[<span style="color:green">{self.name}</span>'
            f'@<span style="color:blue">INFO</span>]: {message}')
        
    def warning(self, message: str, back: int = 1):
        '''
        Опубликовать сообщение с уровнем WARNING (ПРЕДУПРЕЖДЕНИE).

        :param 'message': str
            Текст сообщения

        :returns: None
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

        if self.logLevel == LeafyyLogLevel.DEBUG:
            self.formatString = ('%(asctime)s [%(name)s@%(levelname)s] '
                                 f'[{callSource} <{lineNo}>]: '
                                 '%(message)s')
        else:
            self.formatString = '%(asctime)s [%(name)s@%(levelname)s] %(message)s'

        self.handler.setFormatter(logging.Formatter(self.formatString))

        self.Logger.warning(message)
        if self.logLevel <= LeafyyLogLevel.WARNING and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}WARN{Style.RESET_ALL}]: {message}')

        self.toBuffer(
            f'<span style="color:gray">{datetime.now().strftime(f"%m.%d %H:%M:%S.%f")}</span> '
            f'[<span style="color:green">{self.name}</span>'
            f'@<span style="color:orange">WARN</span>]: {message}')
        
    def error(self, message: str, back: int = 1):
        '''
        Опубликовать сообщение с уровнем ERROR (ОШИБКА).

        :param 'message': str
            Текст сообщения

        :returns: None
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

        if self.logLevel == LeafyyLogLevel.DEBUG:
            self.formatString = ('%(asctime)s [%(name)s@%(levelname)s] '
                                 f'[{callSource} <{lineNo}>]: '
                                 '%(message)s')
        else:
            self.formatString = '%(asctime)s [%(name)s@%(levelname)s] %(message)s'
        self.handler.setFormatter(logging.Formatter(self.formatString))

        self.Logger.error(message)
        if self.logLevel <= LeafyyLogLevel.ERROR and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}ERROR{Style.RESET_ALL}]: {message}')

        self.toBuffer(
            f'<span style="color:gray">{datetime.now().strftime(f"%m.%d %H:%M:%S.%f")}</span> '
            f'[<span style="color:green">{self.name}</span>'
            f'@<span style="color:red">ERROR</span>]: {message}')
        
    def critical(self, message: str, back: int = 1):
        '''
        Опубликовать сообщение с уровнем CRITICAL (КРИТИЧЕСКИЙ).

        :param 'message': str
            Текст сообщения

        :returns: None
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

        if self.logLevel == LeafyyLogLevel.DEBUG:
            self.formatString = ('%(asctime)s [%(name)s@%(levelname)s] '
                                 f'[{callSource} <{lineNo}>]: '
                                 '%(message)s')
        else:
            self.formatString = '%(asctime)s [%(name)s@%(levelname)s] %(message)s'

        self.handler.setFormatter(logging.Formatter(self.formatString))
        
        self.Logger.critical(message)
        if self.logLevel <= LeafyyLogLevel.CRITICAL and not self.printDsb:
            print(f'[{Fore.GREEN}{self.name}{Style.RESET_ALL}@{Fore.YELLOW}CRITICAL{Style.RESET_ALL}]: {message}')

        self.toBuffer(
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
        
        self.toBuffer(
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
