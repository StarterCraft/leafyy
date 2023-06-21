from pydantic import BaseModel

class LogSource(BaseModel):
    name: str
    type: str
    mute: bool

class LogFile(BaseModel):
    name: str
    size: int

class Log(BaseModel):
    name: str
    size: int
    lines: list[str]

class LogReport(BaseModel):
    level: str
    message: str

class ConsoleCommand(BaseModel):
    target: str
    data: str
    type: str
