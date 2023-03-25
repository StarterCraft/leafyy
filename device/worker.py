from PyQt5 import QtCore, QtSerialPort
from PyQt5.QtCore import pyqtSignal, QObject
from .device import GreenyyDevice
import sys
import traceback


class WorkerSignals(QObject):
    ''' Определяет сигналы, доступные из рабочего рабочего потока Worker(QRunnable).'''

    finish   = pyqtSignal()
    error    = pyqtSignal(tuple)
    result   = pyqtSignal(object)
    progress = pyqtSignal(int)


class GreenyyDeviceIniitializationWorker(QtCore.QRunnable):
    ''' Наследует от QRunnable, настройки рабочего потока обработчика, сигналов и wrap-up. '''

    def __init__(self, d):
        super(GreenyyDeviceIniitializationWorker, self).__init__()

        self.d = d
        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = GreenyyDevice(**self.d)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:  # если ошибок не была, испускаем сигнал .result и передаем результат `result`
            self.signals.result.emit(result)      # Вернуть результат обработки
        finally:
            self.signals.finish.emit()            # Done / Готово
