# -*- coding: utf-8 -*-
from leafyy         import app, options
from leafyy.generic import LeafyyComponent, LeafyyWorker

from fastapi import FastAPI
from uvicorn import run as urun


class LeafyyWebService(
    LeafyyComponent,
    FastAPI):
    def __init__(self) -> None:
        super().__init__(
            'WebService',
            loggerName = 'WebService',
            title = 'Leafyy Web Service', 
            description = 'Testing!',
            debug = options('webServiceDebug', False))
        
    def assignApis(self):
        app().ui.assignApi()
        app().log.assignApi()
        app().devices.assignApi()
        

    def uvicornate(self):
        urun(self, 
            port = options().get('serverPort', 38001))

    def run(self):
        'Run with Uvicorn'
        self.w = LeafyyWorker(self.uvicornate)
        self.w.start()
        
    def start(self):
        self.run()

        self.logger.info('Веб-сервер запущен')
        