from PyQt5 import QtCore, QtWidgets
from typing import Iterator, Union

from app import options
from logger.logger import GreenyyLogLevel, GreenyyLogger

class GreenyyLoggingManager(QtCore.QObject):
    def __init__(self) -> None:
        super().__init__()

        self.loggers = []
        self.globalLevel = GreenyyLogLevel.DEBUG
        
    def __getitem__(self, name: str) -> GreenyyLogger:
        try:
            return [l for l in self.loggers if (l.name == name)][0]
        except IndexError:
            raise KeyError(f'Канала журналирования {name} не найдено', name)
        
    def __iter__(self) -> Iterator:
        return iter(self.loggers)

    def add(self, logger: GreenyyLogger):
        self.loggers.append(logger)

    def setGlobalLogLevel(self, level: Union[GreenyyLogLevel, str, int]):
        lvl = GreenyyLogLevel.DEBUG

        if (isinstance(level, str)):
            lvl = GreenyyLogLevel[level]

        if (isinstance(level, GreenyyLogLevel) or isinstance(level, int)):
            lvl = GreenyyLogLevel(level)

        self.globalLevel = lvl
        for logger in self.loggers:
            logger.setLogLevel(lvl)
