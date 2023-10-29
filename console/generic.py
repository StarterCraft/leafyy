# -*- coding: utf-8 -*-
from PySide6   import QtCore
from typing    import Callable, Iterator, ItemsView
from webutils  import formatExc

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

    def model(self) -> list[tuple[str, Command]]:
        output = []
        output.append(('Help', self['Help']))
        output.extend(sorted([c for c in self.commands.items() if len(c[0].split()) == 1 and c[0] != 'Help'], key = lambda c: c[0]))
        output.extend(sorted([c for c in self.commands.items() if len(c[0].split()) > 1 and c[0] != 'Help'], key = lambda c: c[0]))
        return output

    def append(self, command: Command):
        self.commands.update({command.key: command})

    def command(self,
        key: str,
        arguments: list[str] = None,
        displayName: str = None,
        description: str = None
        ) -> Callable[[list[str]], None]:
        def _commandInner(fn: Callable[[list[str]], None]) -> Callable[[list[str]], None]:
            def decorated(args: list[str]):
                try:
                    if (args):
                        print(f'found ARGS', args)
                        fn(args)
                    else:
                        fn()
                except Exception as e:
                    self.logger.error(f'Произошла ошибка при выполнении команды {key}: {formatExc(e)}')
            c = Command(key = key, call = decorated, arguments = arguments, displayName = displayName, description = description)
            self.append(c)

            return decorated

        return _commandInner
