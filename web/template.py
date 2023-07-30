# -*- coding: utf-8 -*-
from typing   import Any
from pydantic import PositiveInt
from fastapi  import Request

from leafyy   import *

from starlette.templating import Jinja2Templates, _TemplateResponse


class Template:
    def __init__(self, name: str, engine: Jinja2Templates) -> None:
        self.name = name
        self.engine = engine
        self.address = f'{name}/{name}.jinja'

    def render(self, request: Request, statusCode: PositiveInt = 200, **kw: Any) -> _TemplateResponse:
            return self.engine.TemplateResponse(
                self.address,
                {
                    'request': request,
                    **kw
                },
                status_code = statusCode,
                headers = {'Content-Security-Policy': 'upgrade-insecure-requests'}
                )
