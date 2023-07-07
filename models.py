from pydantic import BaseModel

class ConsoleCommand(BaseModel):
    target: str
    data:   str
    type:   str
