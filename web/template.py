# -*- coding: utf-8 -*-
from typing   import Any
from pydantic import PositiveInt
from fastapi  import Request
from json     import loads
from autils   import fread

from leafyy   import *

from starlette.templating import Jinja2Templates, _TemplateResponse


class Template:
    def __init__(self, name: str, engine: Jinja2Templates) -> None:
        self.name = name
        self.engine = engine
        self.address = f'{name}/{name}.jinja'

    def getAutoContext(self) -> dict[str, Any] | None:
        try:
            lines = fread(f'web/templates/{self.address}').splitlines()
            start = lines.index('context:')
            #ДОДЕЛАТЬ
        except ValueError:
             return None

    def render(self, request: Request, statusCode: PositiveInt = 200, **kw: Any) -> _TemplateResponse: 
            return self.engine.TemplateResponse(
                self.address,
                {
                    'request': request, 
                    **(self.getAutoContext() if self.autoContext else {}),
                    **kw
                },
                status_code = statusCode,
                headers = {'Content-Security-Policy': 'upgrade-insecure-requests'}
                )
