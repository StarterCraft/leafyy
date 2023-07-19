# -*- coding: utf-8 -*-
from pydantic import BaseModel, PositiveFloat


class LogReport(BaseModel):
    time:    PositiveFloat
    level:   str
    message: str
