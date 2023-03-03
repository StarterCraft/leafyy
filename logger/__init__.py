from PyQt5 import QtCore, QtWidgets
import logging

class Manager:
    def __init__(self, logTo) -> None:
        self.logTo = logTo

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = parent

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)


    