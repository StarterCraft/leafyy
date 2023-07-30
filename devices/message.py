# -*- coding: utf-8 -*-
import datetime

class LeafyyDeviceMessage:
    def __init__(self, author, raw: bytes):
        self.author = author
        self.raw = raw
        self.time = datetime.datetime.now()

    def __str__(self):
        return str(self.raw)

    def __repr__(self) -> str:
        return f'{self.author} at {self.time}: {str(self)}'
