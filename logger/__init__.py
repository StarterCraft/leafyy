#coding=utf-8
from PyQt5 import QtCore, QtWidgets

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
            raise KeyError(f'Канала журналирования {name} не найдено')

    def registerLogger(self, logger: GreenyyLogger):
        self.loggers.append(logger)

    def setGlobalLogLevel(self, level: LogLevel):
        self.globalLevel = level
        for logger in self.loggers:
            logger.setLogLevel(level)
