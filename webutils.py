# -*- coding: utf-8 -*-
from starlette.responses import Response


class FileStreamResponse(Response):
    media_type = 'application/octet-stream'


class CssResponse(Response):
    media_type = 'text/css'


class JsResponse(Response):
    media_type = 'text/javascript'
