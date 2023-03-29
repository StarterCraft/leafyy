from PyQt5 import QtCore, QtWidgets

from app import userOptions
from logger.logger import LogLevel, GreenyyLogger

class GreenyyLoggingManager(QtCore.QObject):
    def __init__(self) -> None:
        super().__init__()

        self.loggers = []
        self.globalLevel = LogLevel.DEBUG
        
    def __getitem__(self, name: str) -> GreenyyLogger:
        try:
            return [l for l in self.loggers if (l.name == name)][0]
        except IndexError:
            raise KeyError(f'Канала журналирования {name} не найдено', name)

    def registerLogger(self, logger: GreenyyLogger):
        self.loggers.append(logger)

    def setGlobalLogLevel(self, level):
        lvl = LogLevel.DEBUG

        if (isinstance(level, str)):
            lvl = LogLevel[level]

        if (isinstance(level, LogLevel) or isinstance(level, int)):
            lvl = LogLevel(level)

        self.globalLevel = lvl
        for logger in self.loggers:
            logger.setLogLevel(lvl)
