from PySide6 import QtCore, QtWidgets
from typing import Union, Iterator, List
from time import strftime, localtime
from glob import glob
from os.path import getsize, sep
from stdlib import fread
from collections import deque

from leafyy import options
from inspection.logger import LeafyyLogLevel, LeafyyLogger


class LeafyyLogging(QtCore.QObject):
    def __init__(self) -> None:
        super().__init__()

        self.fileName = f'logs/Leafyy_{strftime("""%d.%m.%Y_%H%M%S""", localtime())}.log'

        self.completeStack = deque(maxlen = 1024)
        self.updateStack = deque(maxlen = 128)

        self.loggers: List[LeafyyLogger] = []
        self.globalLevel = LeafyyLogLevel.DEBUG
        
    def __getitem__(self, name: str) -> LeafyyLogger:
        try:
            return [l for l in self.loggers if (l.name == name)][0]
        except IndexError:
            raise KeyError(f'Канала журналирования {name} не найдено', name)
        
    def __iter__(self) -> Iterator[LeafyyLogger]:
        return iter(self.loggers)

    def add(self, logger: LeafyyLogger):
        self.loggers.append(logger)

    def remove(self, logger: Union[LeafyyLogger, str]):
        if (isinstance(logger, LeafyyLogger)):
            self.loggers.remove(logger)

        if (isinstance(logger, str)):
            self.loggers.remove(
                [l for l in self if (l.name == logger)][0])

    def toStack(self, message: str):
        self.completeStack.append(message)
        self.updateStack.append(message)

    def toUpdateStack(self, message: str):
        self.updateStack.append(message)

    def flushUpdateStack(self):
        self.updateStack.clear()

    def getCompleteStack(self) -> list[str]:
        self.flushUpdateStack()
        return [m for m in self.completeStack]
    
    def getUpdateStack(self) -> list[str]:
        d = [m for m in self.updateStack]
        self.flushUpdateStack()
        return d

    def setGlobalLogLevel(self, level: Union[LeafyyLogLevel, str, int]):
        lvl = LeafyyLogLevel.DEBUG

        if (isinstance(level, str)):
            lvl = LeafyyLogLevel[level]

        if (isinstance(level, LeafyyLogLevel) or isinstance(level, int)):
            lvl = LeafyyLogLevel(level)

        self.globalLevel = lvl

        for logger in self:
            logger.setLogLevel(lvl)

    def logFolderSummary(self, reversed) -> list[dict[str, str]]:
        data = [
            {'name': fileName.split(sep)[-1],
             'size': getsize(fileName),
            } 
            for fileName in glob('logs/*.log')]
        
        if (reversed):
            return data
        
        print(data)

        return data[::-1]
    
    def formatLog(self, log: list[str]) -> list[str]:
        logs = []
        for line in log:
            #Найти последнее двоеточие
            lastColonIndex = line.index(']:') + 1
            message = line[lastColonIndex:]
            dataChunks = line[:lastColonIndex].split()

            #Для обычного сообщения журнала разделители ниже:
            #Дата и время сообщения журнала
            dateTimeChunk = f'{dataChunks[0]} {dataChunks[1]}'
            dateTimeChunk = '{<span style="text-decoration: underline;">%s</span>}' % dateTimeChunk[1:-1]

            #Канал и уровень журналирования
            loggerInfoChunk = f'[<span style="color: green;">{dataChunks[2][1:].split("@")[0]}</span>:'
            
            loggerLvl = dataChunks[2][:-1].split('@')[1]
            lvlColor = ''
            match loggerLvl:
                case 'DEBUG': lvlColor = 'green'
                case 'INFO': lvlColor = 'blue'
                case 'WARNING': lvlColor = 'orange'
                case _: lvlColor = 'red'

            loggerInfoChunk += f'<span style="color: {lvlColor};">{dataChunks[2][:-1].split("@")[1]}</span>]'

            #Источник сообщения, вплоть до строки кода
            sourceChunk = f'[<span style="color: blue;">{dataChunks[3][1:]}</span> '
            sourceChunk += f'{dataChunks[4]}'

            #Собираем всё
            completeLine = ' '.join((dateTimeChunk, loggerInfoChunk, sourceChunk))
            completeLine += message

            #Отправляем в сборщик
            logs.append(completeLine)

        return logs

    def logFile(self, name: str, html: bool = False) -> dict[str, str | int | list[str]]:
        data = {
            'name': name,
            'size': getsize(f"logs/{name}")
        }

        if (html):
            initial = fread(f'logs/{name}', encoding = 'utf-8').splitlines()
            decorated = self.formatLog(initial)
            data.update(lines = decorated)

        else:
            data.update(lines = fread(f'logs/{name}', encoding = 'utf-8').splitlines())
                
        print(data['size'])

        return data
        