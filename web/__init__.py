from PySide6 import QtCore

from greenyy import options
from greenyy import GreenyyComponent

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from uvicorn import run as uvicornate
from glob    import glob 

class GreenyyWebServer(
    GreenyyComponent,
    QtCore.QObject,
    FastAPI):
    def __init__(self) -> None:
        super().__init__(
            'WebServer',
            loggerName = 'WebServer',
            title = 'Greenyy Web Interface', 
            description = 'Testing!',
            debug = options().webServerDebug)

    def run(self):
        'Run with Uvicorn'
        pool = QtCore.QThreadPool.globalInstance()
        w = WebWorker(lambda: uvicornate(self))
        pool.start(w)
        
    def start(self):
        self.run()
        
        self.logger.info('Веб-сервер запущен')

class WebWorker(QtCore.QRunnable):
    def __init__(self, f) -> None:
        super().__init__()
        self.f = f

    @QtCore.Slot()
    def run(self):
        self.f()
