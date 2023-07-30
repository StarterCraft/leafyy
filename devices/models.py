# -*- coding: utf-8 -*-
from pydantic import BaseModel, NonNegativeInt
from typing   import Optional


class Device(BaseModel):
    address:     str
    displayName: Optional[str]
    description: Optional[str]
    enabled:     bool
    decodeMode:  str

class DeviceCounter(BaseModel):
    total:    NonNegativeInt
    active:   NonNegativeInt
    disabled: NonNegativeInt
    failed:   NonNegativeInt

class Devices(BaseModel):
    count:   DeviceCounter
    devices: list[Device]
