# -*- coding: utf-8 -*-
from pydantic import BaseModel, PositiveInt
from typing   import Optional


class Device(BaseModel):
    address:     str
    displayName: str
    description: Optional[str]
    status:      int
    decodeMode:  str

class DeviceCounter(BaseModel):
    total:    PositiveInt
    active:   PositiveInt
    disabled: PositiveInt
    failed:   PositiveInt

class Devices(BaseModel):
    count:   DeviceCounter
    devices: list[Device]
