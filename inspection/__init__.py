# -*- coding: utf-8 -*-
from PySide6 import QtCore
from typing import Iterator
from pydantic import PositiveFloat
from time import strftime, localtime
from datetime import datetime
from glob import glob
from os import name as osname
from os.path import getsize, getmtime, sep as psep
from autils import fread

from leafyy            import app, web, postgres
from inspection.logger import LeafyyLogLevel, LeafyyLogger
from .api              import LeafyyLoggingApi
from .models           import Log, LogConfig, LogRecord


class LeafyyLogging(
    QtCore.QObject,
    LeafyyLoggingApi
    ):
    loggers: dict[str, LeafyyLogger] = {}

    def __init__(self) -> None:
        super().__init__()

        self.fileName = f'logs/Leafyy_{strftime("%d.%m.%Y_%H%M%S", localtime(app().startup))}.log'

        #Очищаем таблицу в базе данных для текущего журнала
        postgres('inspection.truncateLog')

        self.globalLevel = LeafyyLogLevel.DEBUG

    def __getitem__(self, key: int | str) -> LeafyyLogger:
        if (isinstance(key, str)):
            return self.loggers[key]

        else:
            return self.loggers.values()[key]

    def __iter__(self) -> Iterator[LeafyyLogger]:
        return iter(self.loggers.values())

    def __len__(self) -> int:
        return len(self.loggers)

    def append(self, logger: LeafyyLogger) -> None:
        self.loggers.update({logger.name: logger})

    def remove(self, logger: str) -> None:
        self.loggers.pop(logger)

    def model(self) -> LogConfig:
        return {
            'level': self.globalLevel.name,
            'loggers': [l.model() for l in self]
            }

    def assignApi(self):
        super().assignApi()
        web().mount('/log', self.api)

    async def getConfig(self) -> LogConfig:
        return self.model()

    def setConfig(self, config: LogConfig):
        self.setGlobalLogLevel(config.level)

        for c in config.loggers:
            try:
                self[c.name].console = c.live
                self[c.name].setLogLevel(LeafyyLogLevel[c.level])
            except KeyError:
                continue

    def record(self, time: datetime, logger: str, level: str, message: str) -> None:
        postgres().insert('inspection.insertLog', (time, logger, level, message))

    def getLogRecords(self, begin: PositiveFloat = 1) -> list[tuple]:
        t = datetime.fromtimestamp(begin / 1000 if osname == 'nt' else begin)
        return postgres().fetchall('inspection.selectLog', t)

    def flush(self) -> None:
        postgres('inspection.truncateLog')

    def setGlobalLogLevel(self, level: LeafyyLogLevel | str | int):
        lvl = LeafyyLogLevel.DEBUG

        if (isinstance(level, str)):
            lvl = LeafyyLogLevel[level]

        if (isinstance(level, LeafyyLogLevel) or isinstance(level, int)):
            lvl = LeafyyLogLevel(level)

        self.globalLevel = lvl

        for logger in self:
            logger.setLogLevel(lvl)

    async def getLogFolderSummary(self, reversed = False) -> list[Log]:
        data = [
            {'name': fileName.split(psep)[-1],
             'time': getmtime(fileName),
             'size': getsize(fileName),
            }
            for fileName in glob('logs/*.log')]

        return sorted(data, key = lambda t: t['time'], reverse = not bool(reversed))

    def format(self, log: list[LogRecord] = None, begin: PositiveFloat = 1) -> list[str]:
        if (not log):
            log = self.getLogRecords(begin)

        output = []

        for record in log:
            dateTimeChunk = f'<span style="color: gray; text-decoration: underlined;">{record.stamp}</span>'
            loggerInfoChunk = f'[<span style="color: green;">{record.logger}</span>@'

            loggerLvl = record.level
            lvlColor = ''
            match loggerLvl:
                case 'DEBUG': lvlColor = 'gray'
                case 'INFO': lvlColor = 'blue'
                case 'WARNING': lvlColor = 'orange'
                case 'ERROR': lvlColor = 'red'
                case _: lvlColor = 'darkred'

            loggerInfoChunk += f'<span style="color: {lvlColor};">{loggerLvl}</span>]'

            line = ' '.join([dateTimeChunk, loggerInfoChunk, record.message])

            output.append(line)

        return output

    def formatLines(self, log: list[str]) -> list[str]:
        output = []
        for line in log:
            try:
                #Найти последнее двоеточие
                lastColonIndex = line.index(']:') + 1
                message = line[lastColonIndex:]
                dataChunks = line[:lastColonIndex].split()

                #Дата и время сообщения журнала
                dateTimeChunk = f'{dataChunks[0]} {dataChunks[1]}'
                dateTimeChunk = f'<span style="color: gray; text-decoration: underlined;">{dateTimeChunk}</span>'

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

                #Если журнал передаётся в полном виде, то будет также
                #присутствовать информация о источнике сообщения.

                sourceChunk = ''

                if (len(dataChunks) > 3):
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
                output.append(completeLine)

            except:
                li = '<span style="background-color: beige;">'
                li += line.replace(' ', '·')
                li += '</span>'

                output.append(li)

        return output

    async def getLogFile(self, name: str, html: bool = False) -> Log:
        data = {
            'name': name,
            'time': getmtime(f'logs/{name}'),
            'size': getsize(f'logs/{name}')
        }

        if (html):
            initial = fread(f'logs/{name}', encoding = 'utf-8').splitlines()
            decorated = self.formatLines(initial)
            data.update(lines = decorated)

        else:
            data.update(lines = fread(f'logs/{name}', encoding = 'utf-8').splitlines())

        return data

