from PySide6 import QtCore, QtWidgets
from typing import Union, Iterator, List
from time import strftime, localtime

from greenyy import options
from inspection.logger import GreenyyLogLevel, GreenyyLogger


class GreenyyLogging(QtCore.QObject):


    def __init__(self) -> None:
        super().__init__()

        self.fileName = f'logs/Greenyy_{strftime("""%d.%m.%Y_%H%M%S""", localtime())}.log'

        self.loggers: List[GreenyyLogger] = []
        self.globalLevel = GreenyyLogLevel.DEBUG
        
    def __getitem__(self, name: str) -> GreenyyLogger:
        try:
            return [l for l in self.loggers if (l.name == name)][0]
        except IndexError:
            raise KeyError(f'Канала журналирования {name} не найдено', name)
        
    def __iter__(self) -> Iterator[GreenyyLogger]:
        return iter(self.loggers)

    def add(self, logger: GreenyyLogger):
        self.loggers.append(logger)

    def remove(self, logger: Union[GreenyyLogger, str]):
        if (isinstance(logger, GreenyyLogger)):
            self.loggers.remove(logger)

        if (isinstance(logger, str)):
            self.loggers.remove(
                [l for l in self if (l.name == logger)][0])

    def setGlobalLogLevel(self, level: Union[GreenyyLogLevel, str, int]):
        lvl = GreenyyLogLevel.DEBUG

        if (isinstance(level, str)):
            lvl = GreenyyLogLevel[level]

        if (isinstance(level, GreenyyLogLevel) or isinstance(level, int)):
            lvl = GreenyyLogLevel(level)

        self.globalLevel = lvl

        for logger in self:
            logger.setLogLevel(lvl)
