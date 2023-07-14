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
    lines: Optional[list[str]]

class LogReport(BaseModel):
    time:    PositiveFloat
    level:   str
    message: str

class ErrorRecord(BaseModel):
    time:    PositiveFloat
    origin:  str
    message: str
    