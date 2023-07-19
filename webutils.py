# -*- coding: utf-8 -*-
from traceback import format_exception
from starlette.responses import Response


class FileStreamResponse(Response):
    media_type = 'application/octet-stream'


class CssResponse(Response):
    media_type = 'text/css'


class JsResponse(Response):
    media_type = 'text/javascript'


def formatExc(exc: Exception) -> str:
    return ''.join([line.replace(' ', '·') for line in format_exception(exc)])
