# -*- coding: utf-8 -*-
from leafyy         import app, properties
from leafyy.generic import LeafyyComponent, LeafyyThreadedWorker

from fastapi          import FastAPI
from fastapi.security import OAuth2PasswordBearer
from uvicorn          import run as urun


class LeafyyWebService(
    LeafyyComponent,
    FastAPI):
    def __init__(self) -> None:
        super().__init__(
            'WebService',
            loggerName = 'WebService',
            title = 'Leafyy Web Service', 
            description = 'Testing!',
            debug = properties('webServiceDebug', False))
        
        self.authBearer = OAuth2PasswordBearer(tokenUrl = 'token')
        
    def assignApis(self):
        app().ui.assignApi()
        app().cli.assignApi()
        app().log.assignApi()
        app().devices.assignApi()

    def uvicornate(self):
        urun(self, 
            port = properties().get('serverPort', 38001))

    def run(self):
        'Run with Uvicorn'
        self.w = LeafyyThreadedWorker(self.uvicornate)
        self.w.run()
        
    def start(self):
        self.run()

        self.logger.info('Веб-сервер запущен')

    def stop(self):
        self.w.exit()
        