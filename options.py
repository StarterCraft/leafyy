# -*- coding: utf-8 -*-
from typing import Any
from json   import loads, dumps
from autils import fread, fwrite

from leafyy import deepget


class LeafyyProperties(dict):
    FILENAME = 'options.json'

    def __init__(self):
        super().__init__()
        self.read()

    def __call__(self, key: str, default: Any = None, sep: str = '.') -> Any:
        return deepget(self, key, default, sep)

    def read(self):
        self.update(loads(fread(self.FILENAME, encoding = 'utf-8')))

    def write(self):
        fwrite(self.FILENAME, dumps(self))
