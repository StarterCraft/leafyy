#INITIALIZER не работает по неизвестной причине,
#которую не удалось установить. Отключен.

from PySide6 import QtCore, QtSerialPort
from PySide6.QtCore import Signal, QObject
from .device import LeafyyDevice
import sys
import traceback


class LeafyyDeviceInitializer(QtCore.QThread):
    error = QtCore.Signal(tuple)
    initialized = QtCore.Signal(LeafyyDevice)
    #STACKOVERFLOW: https://stackoverflow.com/a/6789205/13677671
    #STACKOVERFLOW: https://ru.stackoverflow.com/a/840447/397716

    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data


    def run(self):
        try:
            result = LeafyyDevice(**self.data)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.initialized.emit(result)
