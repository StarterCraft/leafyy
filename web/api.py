from typing  import Annotated
from glob    import glob

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from .page import Template


class GreenyyWebApi:
    def __init__(self) -> None:
        self.jinja = Jinja2Templates('web/templates')
        self.btn1c = 0
        self.lr = ''

        self.pages: dict[str, Template] = {}

        self.loadWebPageTemplates()

    def __getitem__(self, key: str) -> Template:
        return self.pages[key]

    def loadWebPageTemplates(self):
        templateNames = [name.split('\\')[-1] for name in glob('web/templates/*')]

        for name in templateNames:
            self.pages.update({name: Template(self.jinja, f'{name}/{name}.html.jinja')})

    def assign(self, service: FastAPI):
        @service.get('/{cssId}.css', response_class = Response)
        def getCss(cssId: str):
            with open(f'web/templates/{cssId}/{cssId}.css') as f:
                return f.read()

        @service.get('/', response_class = HTMLResponse)
        def index(request: Request) -> _TemplateResponse:
            return self['index'].render(
                request,
                btn1counter = self.btn1c,
                message = self.lr)
        
        @service.get('/devices', response_class = HTMLResponse)
        def index(request: Request) -> _TemplateResponse:
            return self['devices'].render(
                request)
                #devices = [{'name': 'COM0', 'status': 'Active', 'description': 'Device 1'}, {'name': 'COM3', 'status': 'Active', 'description': 'Device 2'}])
        
        @service.get('/rules', response_class = HTMLResponse)
        def index(request: Request) -> _TemplateResponse:
            return self['rules'].render(
                request)
        
        @service.get('/clickBtn1', response_class = HTMLResponse)
        def onclickBtn1(request: Request) -> _TemplateResponse:
            self.btn1c += 1
            
            return self['index'].render(
                request,
                btn1counter = self.btn1c,
                message = self.lr
            )

        @service.post('/clickBtn2', response_class = HTMLResponse)
        def onclickBtn2(request: Request, data: Annotated[str, Form()]) -> _TemplateResponse:
            self.lr = data
            
            return self['index'].render(
                request,
                btn1counter = self.btn1c,
                message = self.lr
            )
        

