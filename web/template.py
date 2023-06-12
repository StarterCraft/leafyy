from typing import Any
from fastapi import Request
from starlette.templating import Jinja2Templates, _TemplateResponse


class Template:
    def __init__(self, engine: Jinja2Templates, address: str) -> None:
        self.engine = engine
        self.address = address

    def render(self, request: Request, **kw: dict[str, Any]) -> _TemplateResponse: 
        return self.engine.TemplateResponse(
            self.address,
            {'request': request, **kw})
