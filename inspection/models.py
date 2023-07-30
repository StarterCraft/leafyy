# -*- coding: utf-8 -*-
from pydantic import BaseModel, PositiveInt, PositiveFloat
from typing   import Optional
from datetime import datetime


class Logger(BaseModel):
    name:   str
    level:  str
    live:   bool

class LogConfig(BaseModel):
    level:   str
    loggers: list[Logger]

class Log(BaseModel):
    name:  str
    size:  PositiveInt
    mtime: datetime
    lines: Optional[list[str]]

class LogRecord(BaseModel):
    stamp:   datetime
    logger:  str
    level:   str
    message: str

class ErrorRecord(BaseModel):
    stamp:   datetime
    origin:  Optional[str]
    caller:  str
    message: str
    