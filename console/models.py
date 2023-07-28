# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing   import Any, Optional, Callable


class Command(BaseModel):
    key:         str
    call:        Callable[[list[str]], None]
    arguments:   Optional[list[str]]
    displayName: Optional[str]
    description: Optional[str]

    def __call__(self, a: list[str]) -> None:
        self.call(a)

class Order(BaseModel):
    target: str
    type:   str
    data:   str
