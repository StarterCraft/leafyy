from pydantic import BaseModel

class LogReport(BaseModel):
    level: str
    message: str

class ConsoleCommand(BaseModel):
    target: str
    data: str
    type: str
