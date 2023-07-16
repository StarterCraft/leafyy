# -*- coding: utf-8 -*-
from PySide6   import QtCore
from typing    import Callable, Iterator, ItemsView
from traceback import format_exc

from .models   import Command


class LeafyyConsoleCommands(
    QtCore.QObject
    ):
    commands: dict[str, Command] = {}

    def __getitem__(self, key: str) -> Command:
            return self.commands[key]
        
    def __iter__(self) -> Iterator[tuple[str, Command]]:
        return iter(self.commands.items())
    
    def __len__(self) -> int:
        return len(self.commands.items())
    
    def model(self) -> NotImplemented:
        return NotImplemented

    def append(self, command: Command):
        self.commands.update({command.key: command})

    def command(self,
        f: Callable[[list[str]], None],
        key: str,
        displayName: str = None,
        description: str = None
        ) -> Callable[[list[str]], None]:
        self.append(key, Command(key = key, call = f, displayName = displayName, description = description))

        def decorated(args: list[str]):
            try:
                f(args)
            except Exception as e:
                self.logger.error(format_exc().splitlines())

        return decorated
