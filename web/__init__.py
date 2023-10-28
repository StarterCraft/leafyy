# -*- coding: utf-8 -*-
from leafyy               import app, config
from leafyy.generic       import LeafyyComponent, LeafyyThreadedWorker

from fastapi              import FastAPI, Request
from fastapi.responses    import RedirectResponse
from starlette.templating import _TemplateResponse
from starlette.exceptions import HTTPException
from fastapi.security     import OAuth2PasswordBearer
from uvicorn              import run as urun


class LeafyyWebService(
    LeafyyComponent,
    FastAPI):
    def __init__(self) -> None:
        super().__init__(
            'WebService',
            loggerName = 'WebService',
            title = 'Leafyy Web Service',
            description = 'Testing!',
            debug = config('webServiceDebug', False))

        self.authBearer = OAuth2PasswordBearer(tokenUrl = 'token')

        @self.exception_handler(HTTPException)
        def error(request: Request, exc: HTTPException) -> RedirectResponse | _TemplateResponse:
            if (exc.status_code == 401):
                return RedirectResponse(
                    '/auth?to=' + request.url.path,
                    status_code = 302,
                    headers = {"WWW-Authenticate": "Bearer"})

            return app().ui['error'].render(
                request,
                statusCode = exc.status_code,
                exception = exc
            )

    def assignApis(self):
        app().ui.assignApi()
        app().cli.assignApi()
        app().log.assignApi()
        app().devices.assignApi()

    def uvicornate(self):
        urun(self,
            host = config('service.host', 'localhost'),
            port = config('service.port', 8381)
            )

    def run(self):
        'Run with Uvicorn'
        self.w = LeafyyThreadedWorker(self.uvicornate)
        self.w.run()

    def start(self):
        self.run()

        self.logger.info('Веб-сервер запущен')

    def stop(self):
        self.w.exit()

