# -*- coding: utf-8 -*-
from PySide6   import QtCore
from typing    import Callable, Iterator
from traceback import format_exc

from leafyy         import web
from leafyy.generic import LeafyyIterableComponent

from .generic import LeafyyConsoleCommands
from .api     import LeafyyConsoleApi
from .models  import Command


class LeafyyConsole(
    LeafyyIterableComponent,
    LeafyyConsoleCommands,
    LeafyyConsoleApi
    ):
    def __init__(self):
        super().__init__('Console')

    def assignApi(self):
        super().assignApi()
        web().mount('/console', self.api)

    def mount(self, superKey: str, commands: LeafyyConsoleCommands):
        for key, cmd in commands:
            self.append(cmd.copy({'key': f'{superKey} {key}'}))
