from PySide6 import QtCore, QtSerialPort
from PySide6.QtCore import Signal, QObject
from .device import LeafyyDevice
import sys
import traceback


class WorkerSignals(QObject):
    ''' Определяет сигналы, доступные из рабочего рабочего потока Worker(QRunnable).'''

    finish   = Signal()
    error    = Signal(tuple)
    result   = Signal(object)
    progress = Signal(int)


class LeafyyDeviceInitializationWorker(QtCore.QRunnable):
    ''' Наследует от QRunnable, настройки рабочего потока обработчика, сигналов и wrap-up. '''

    def __init__(self, d):
        super(LeafyyDeviceInitializationWorker, self).__init__()

        self.d = d
        self.signals = WorkerSignals()

    @QtCore.Slot()
    def run(self):
        try:
            result = LeafyyDevice(**self.d)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:  # если ошибок не была, испускаем сигнал .result и передаем результат `result`
            self.signals.result.emit(result)      # Вернуть результат обработки
        finally:
            self.signals.finish.emit()            # Done / Готово
