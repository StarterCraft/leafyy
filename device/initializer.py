from PyQt5 import QtCore, QtSerialPort
from .device import GreenyyDevice
import sys
import traceback


class GreenyyDeviceInitializerSignals(QtCore.QObject):
    begun = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal()
    initialized = QtCore.pyqtSignal(object)
    completed = QtCore.pyqtSignal()


class GreenyyDeviceInitializer(QtCore.QRunnable):
    def __init__(self, data: dict) -> None:
        super(GreenyyDeviceInitializer, self).__init__()
        self.running = False
        self.data = data
        self.signals = GreenyyDeviceInitializerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        #STACKOVERFLOW: https://ru.stackoverflow.com/a/840447/397716
        try:
            print('RUN START')
            result = GreenyyDevice(**self.data) 
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            print(result)
            self.signals.initialized.emit(result)
        finally:
            self.signals.completed.emit()
