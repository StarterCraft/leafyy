# -*- coding: utf-8 -*-
from pydantic import BaseModel, PositiveInt, PositiveFloat
from typing   import Optional


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
    time:  PositiveFloat
    lines: Optional[list[str]]

class ErrorRecord(BaseModel):
    time:    PositiveFloat
    origin:  Optional[str]
    caller:  str
    message: str
    