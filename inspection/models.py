from pydantic import BaseModel, PositiveInt
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
    time:    PositiveInt
    level:   str
    message: str
    