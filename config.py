# -*- coding: utf-8 -*-
from typing import Any
from yaml   import safe_load, safe_dump
from autils import fread, fwrite

from leafyy import deepget


class LeafyyConfig(dict):
    FILENAME = 'config.yml'

    def __init__(self):
        super().__init__()
        self.read()

    def __call__(self, key: str, default: Any = None, sep: str = '.') -> Any:
        return deepget(self, key, default, sep)

    def read(self):
        with open(self.FILENAME, encoding = 'utf-8') as f:
            self.update(safe_load(f))

    def write(self):
        with open(self.FILENAME, 'w', encoding = 'utf-8') as f:
            self.update(safe_dump(self, f, indent = 4, allow_unicode = True))
