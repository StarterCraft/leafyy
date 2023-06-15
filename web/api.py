from typing  import Annotated
from glob    import glob
from stdlib  import fread, fwrite

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from fastapi.responses import HTMLResponse, FileResponse, Response

from leafyy import hardware as _hardware
from leafyy import log as logging

from .template import Template


DEVICE_CARD_SINGLE = [
                    {'name': 'COM0', 'status': 'Active', 'description': 'Device 1'}]

DEVICE_CARD_MANY = [ {'name': 'COM0', 'status': 'Active', 'description': 'Device 1'},
    {'name': 'COM1', 'status': 'Inactive', 'description': 'Device 2'},
    {'name': 'COM2', 'status': 'Active', 'description': 'Device 3'},
    {'name': 'COM3', 'status': 'Inactive', 'description': 'Device 4'},
    {'name': 'COM4', 'status': 'Active', 'description': 'Device 5'},
    {'name': 'COM5', 'status': 'Inactive', 'description': 'Device 6'},
    {'name': 'COM6', 'status': 'Active', 'description': 'Device 7'},
    {'name': 'COM7', 'status': 'Inactive', 'description': 'Device 8'},
    {'name': 'COM8', 'status': 'Active', 'description': 'Device 9'},
    {'name': 'COM9', 'status': 'Inactive', 'description': 'Device 10'},
    {'name': 'COM10', 'status': 'Active', 'description': 'Device 11'},
    {'name': 'COM11', 'status': 'Inactive', 'description': 'Device 12'},
    {'name': 'COM12', 'status': 'Active', 'description': 'Device 13'},
    {'name': 'COM13', 'status': 'Inactive', 'description': 'Device 14'},
    {'name': 'COM14', 'status': 'Active', 'description': 'Device 15'},
    {'name': 'COM15', 'status': 'Inactive', 'description': 'Device 16'}]


class LeafyyWebApi:
    def __init__(self) -> None:
        self.jinja = Jinja2Templates('web/templates')

        self.pages: dict[str, Template] = {}

        self.loadWebPageTemplates()

    def __getitem__(self, key: str) -> Template:
        return self.pages[key]

    def loadWebPageTemplates(self):
        templateNames = [name.split('\\')[-1] for name in glob('web/templates/*')]

        for name in templateNames:
            self.pages.update({name: Template(self.jinja, f'{name}/{name}.html.jinja')})

    def assign(self, service: FastAPI):
        @service.get('/leafyy.css', response_class = Response)
        def getGlobalCss() -> str:
            return fread('web/leafyy.css')

        @service.get('/{cssId}.css', response_class = Response)
        def getCss(cssId: str) -> str:
            return fread(f'web/templates/{cssId}/{cssId}.css')

        @service.get('/leafyy.js', response_class = Response)
        def getGlobalJs() -> str:
            return fread('web/leafyy.js')

        @service.get('/{scriptId}.js', response_class = Response)
        def getJs(scriptId: str) -> str:
            return fread(f'web/templates/{scriptId}/{scriptId}.js')
        
        @service.get('/site.webmanifest', response_class = Response)
        def getWebManifest() -> str:
            return fread('web/site.webmanifest')
        
        @service.get('/resources/{resourceId}', response_class = FileResponse)
        def getResource(resourceId: str) -> FileResponse:
            return f'web/resources/{resourceId}'

        @service.get('/favicon.ico', response_class = FileResponse)
        def getFavicon() -> FileResponse:
            return f'web/resources/favicon.svg'
        
        @service.get('/auth', response_class = HTMLResponse)
        def auth(request: Request) -> _TemplateResponse:
            return self['auth'].render(
                request)

        @service.get('/', response_class = HTMLResponse)
        def index(request: Request) -> _TemplateResponse:
            return self['index'].render(
                request)
        
        @service.get('/hardware', response_class = HTMLResponse)
        def hardware(request: Request) -> _TemplateResponse:
            return self['hardware'].render(
                request,
                hardware = _hardware().toDict())
        
        @service.get('/rules', response_class = HTMLResponse)
        def rules(request: Request) -> _TemplateResponse:
            return self['rules'].render(
                request)
        
        @service.get('/log', response_class = HTMLResponse)
        def log(request: Request) -> _TemplateResponse:
            return self['log'].render(
                request
            )
        
        @service.get('/log/view', response_class = HTMLResponse)
        def logList(request: Request, reversed = 0) -> _TemplateResponse:
            return self['logList'].render(
                request,
                logData = logging().logFolderSummary(reversed),
                reversed = reversed
            )
        
        @service.get('/log/{name}')
        def logFile(request: Request, name: str) -> FileResponse:
            return FileResponse(f'logs/{name}', media_type='application/octet-stream',filename = name)
        
        @service.get('/log/view/{name}', response_class = HTMLResponse)
        def logFileView(request: Request, name: str) -> _TemplateResponse:
            print(0b111001011011)
            return self['logView'].render(
                request,
                logFile = logging().logFile(name, html = True)
            )

        @service.get('/doc', response_class = HTMLResponse)
        def doc(request: Request) -> _TemplateResponse:
            return self['doc'].render(
                request
            )      
