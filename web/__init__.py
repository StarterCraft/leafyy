from PySide6 import QtCore

from leafyy import options
from leafyy import LeafyyComponent

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from uvicorn import run as urun
from glob    import glob 

class LeafyyWebServer(
    LeafyyComponent,
    QtCore.QObject,
    FastAPI):
    def __init__(self) -> None:
        super().__init__(
            'WebServer',
            loggerName = 'WebServer',
            title = 'Leafyy Web Interface', 
            description = 'Testing!',
            debug = options('webServerDebug', False))

    def uvicornate(self):
        urun(self, 
            port = options().get('serverPort', 38001))

    def run(self):
        self.uvicornate()

    def runSeparately(self):
        'Run with Uvicorn'
        self.w = WebWorker(self.uvicornate)
        self.w.start()
        
    def start(self):
        self.run()

        self.logger.info('Веб-сервер запущен')

    def startSeparately(self):
        self.runSeparately()
        
        self.logger.info('Веб-сервер запущен в отдельном потоке')


class WebWorker(QtCore.QThread):
    def __init__(self, f) -> None:
        super().__init__()
        self.f = f

    def run(self):
        self.f()
        super().run()
