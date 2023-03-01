#INITIALIZER не работает по неизвестной причине,
#которую не удалось установить. Отключен.

from PyQt5 import QtCore, QtSerialPort
from PyQt5.QtCore import pyqtSignal, QObject
from .device import GreenyyDevice
import sys
import traceback


class GreenyyDeviceInitializer(QtCore.QThread):
    begun = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(tuple)
    initialized = QtCore.pyqtSignal(object)
    completed = QtCore.pyqtSignal()
    #STACKOVERFLOW: https://stackoverflow.com/a/6789205/13677671
    #STACKOVERFLOW: https://ru.stackoverflow.com/a/840447/397716

    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data


    def run(self):
        try:
            print('RUN START')
            result = GreenyyDevice(**self.data) 
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.error.emit((exctype, value, traceback.format_exc()))
        else:
            print(result.port.isOpen())
            self.initialized.emit(result)
        finally:
            self.completed.emit()
