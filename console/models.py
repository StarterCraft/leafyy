# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing   import Optional, Callable


class Command(BaseModel):
    key:         str
    call:        Callable[[list[str]], list[str]]
    displayName: Optional[str]
    description: Optional[str]
