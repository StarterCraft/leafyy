from PySide6 import QtCore
from typing import Iterator
from time import strftime, localtime
from glob import glob
from os.path import getsize, getmtime, sep
from autils import fread, fwrite

from fastapi           import FastAPI

from leafyy            import web
from inspection.logger import LeafyyLogLevel, LeafyyLogger
from .api              import LeafyyLoggingApi
from .models           import Log, LogConfig


class LeafyyLogging(
    QtCore.QObject,
    LeafyyLoggingApi
    ):
    loggers: list[LeafyyLogger] = []
    api = FastAPI(
        title = 'API Листочка: подсистема журнала'
    )

    def __init__(self) -> None:
        super().__init__()

        self.fileName = f'logs/Leafyy_{strftime("""%d.%m.%Y_%H%M%S""", localtime())}.log'

        #Вместо стеков попробуем использовать буферы
        self.generalBuffer = 'logs/buffer/.log'
        self.updateBuffer = 'logs/buffer/update.log'
        self.errorBuffer = 'logs/buffer/error.log'

        fwrite(self.generalBuffer, '')
        fwrite(self.updateBuffer, '')
        fwrite(self.errorBuffer, '')

        self.globalLevel = LeafyyLogLevel.DEBUG
        
    def __getitem__(self, key: int | str) -> LeafyyLogger:
        if (isinstance(key, str)):
            try:
                return [l for l in self.loggers if (l.name == key)][0]
            except IndexError as e:
                raise KeyError(f'Канала журналирования {key} не найдено', key) from e
            
        else:
            return self.loggers[key]
        
    def __iter__(self) -> Iterator[LeafyyLogger]:
        return iter(self.loggers)
    
    def __len__(self) -> int:
        return len(self.loggers)

    def add(self, logger: LeafyyLogger):
        self.loggers.append(logger)

    def remove(self, logger: LeafyyLogger | str):
        if (isinstance(logger, LeafyyLogger)):
            self.loggers.remove(logger)

        if (isinstance(logger, str)):
            self.loggers.remove(
                [l for l in self if (l.name == logger)][0])
            
    def model(self) -> LogConfig:
        return {
            'level': self.globalLevel.name,
            'loggers': [l.model() for l in self]}

    def assignApi(self):
        self.assign()
        web().mount('/log', self.api)
            
    def getConfig(self) -> LogConfig:
        return self.model()

    def setConfig(self, config: LogConfig):
        self.setGlobalLogLevel()

        for c in config:
            try:
                self[c.name].console = c.live
                self[c.name].setLogLevel(LeafyyLogLevel[c.level])
            except KeyError:
                continue

    def toStack(self, message: str) -> None:
        fwrite(self.generalBuffer, f'{message}\n', mode = 'a')
        fwrite(self.updateBuffer, f'{message}\n', mode = 'a')

    def toErrorStack(self, message: str) -> None:
        fwrite(self.errorBuffer, f'{message}\n', mode = 'a')

    def toUpdateStack(self, message: str) -> None:
        fwrite(self.updateBuffer, f'{message}\n', mode = 'a')

    def getGeneralStack(self) -> list[str]:
        self.flushUpdateStack()
        return fread(self.generalBuffer).splitlines()
    
    def getErrorStack(self) -> list[str]:
        return NotImplemented
    
    def getUpdateStack(self) -> list[str]:
        d = fread(self.updateBuffer).splitlines()
        self.flushUpdateStack()
        return d
    
    def flush(self):
        self.flushGeneralStack()
        self.flushErrorStack()
        self.flushUpdateStack()

    def flushGeneralStack(self) -> None:
        fwrite(self.generalBuffer, '')

    def flushErrorStack(self) -> None:
        fwrite(self.errorBuffer, '')

    def flushUpdateStack(self) -> None:
        fwrite(self.updateBuffer, '')

    def setGlobalLogLevel(self, level: LeafyyLogLevel | str | int):
        lvl = LeafyyLogLevel.DEBUG

        if (isinstance(level, str)):
            lvl = LeafyyLogLevel[level]

        if (isinstance(level, LeafyyLogLevel) or isinstance(level, int)):
            lvl = LeafyyLogLevel(level)

        self.globalLevel = lvl

        for logger in self:
            logger.setLogLevel(lvl)

    def getLogFolderSummary(self, reversed = False) -> list[Log]:
        data = [
            {'name': fileName.split(sep)[-1],
             'time': int(getmtime(fileName)),
             'size': getsize(fileName),
            } 
            for fileName in glob('logs/*.log')]
        
        return sorted(data, key = lambda t: t['time'], reverse = not bool(reversed))
    
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
            loggerInfoChunk = f'[<span style="color: green;">{dataChunks[2][1:].split("@")[0]}</span>@'
            
            loggerLvl = dataChunks[2][:-1].split('@')[1]
            lvlColor = ''
            match loggerLvl:
                case 'DEBUG': lvlColor = 'gray'
                case 'INFO': lvlColor = 'blue'
                case 'WARNING': lvlColor = 'orange'
                case 'ERROR': lvlColor = 'red'
                case _: lvlColor = 'darkred'

            loggerInfoChunk += f'<span style="color: {lvlColor};">{dataChunks[2][:-1].split("@")[1]}</span>]'

            #Источник сообщения, вплоть до строки кода
            #Сделаем подсветку синтаксиса для каждого элемента пути
            sourceTokens = dataChunks[3][1:].split('.')

            sourceChunk = '['

            toFunctions = False
            for ix, token in enumerate(sourceTokens):
                if (token.startswith('<')):
                    continue

                if (ix > 0):
                    sourceChunk += '.'

                if (token[0].istitle()):
                    toFunctions = True
                    sourceChunk += f'<span class="bold" style="color:darkorange;">{token}</span>'
                    continue

                if (toFunctions or (ix == len(sourceTokens) - 1)):
                    sourceChunk += f'<span style="color:blue;">{token}</span>'
                    continue

                else:
                    sourceChunk += f'<span class="bold" style="color:coral;">{token}</span>'
                    continue

            sourceChunk += f' {dataChunks[4]}' #строка кода

            #Собираем всё
            completeLine = ' '.join((dateTimeChunk, loggerInfoChunk, sourceChunk))
            completeLine += message

            #Отправляем в сборщик
            logs.append(completeLine)

        return logs

    def getLogFile(self, name: str, html: bool = False) -> Log:
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
                

        return data
        