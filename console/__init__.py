from PySide6 import QtCore
from typing  import Callable

from leafyy         import app
from leafyy.generic import LeafyyIterableComponent
from .api           import LeafyyConsoleApi
from .models        import Command


class LeafyyConsole(
    LeafyyIterableComponent,
    QtCore.QObject,
    LeafyyConsoleApi
    ):
    commands: dict[str, Command] = {}

    def __init__(self):
        super().__init__('Console')

    def command(self, f: Callable):
        self.append(f)

        return f
