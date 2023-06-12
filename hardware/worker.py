from PySide6 import QtCore, QtSerialPort
from PySide6.QtCore import Signal, QObject
from .device import GreenyyDevice
import sys
import traceback


class WorkerSignals(QObject):
    ''' Определяет сигналы, доступные из рабочего рабочего потока Worker(QRunnable).'''

    finish   = Signal()
    error    = Signal(tuple)
    result   = Signal(object)
    progress = Signal(int)


class GreenyyDeviceInitializationWorker(QtCore.QRunnable):
    ''' Наследует от QRunnable, настройки рабочего потока обработчика, сигналов и wrap-up. '''

    def __init__(self, d):
        super(GreenyyDeviceInitializationWorker, self).__init__()

        self.d = d
        self.signals = WorkerSignals()

    @QtCore.Slot()
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
