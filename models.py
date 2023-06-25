from pydantic import BaseModel
from typing   import Optional


class LogSource(BaseModel):
    name:  str
    type:  str
    mode:  str
    live:  bool

class LogConfig(BaseModel):
    level:   str
    sources: list[LogSource]

class LogFile(BaseModel):
    name: str
    size: int

class Log(BaseModel):
    name:  str
    size:  int
    lines: list[str]

class LogReport(BaseModel):
    level:   str
    message: str

class ConsoleCommand(BaseModel):
    target: str
    data:   str
    type:   str
