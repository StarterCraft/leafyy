#coding=utf-8
from typing import List, Dict, Any
from json   import loads, dumps
from utillo import fread, fwrite

from leafyy import deepget


class LeafyyOptions(dict):
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
