# -*- coding: utf-8 -*-

from typing import Any
from leafyy         import web
from leafyy.generic import LeafyyComponent

from .generic import LeafyyConsoleCommands
from .api     import LeafyyConsoleApi
from .cli     import LeafyyConsoleCli


class LeafyyConsole(
    LeafyyComponent,
    LeafyyConsoleCommands,
    LeafyyConsoleCli,
    LeafyyConsoleApi
    ):
    def __init__(self):
        super().__init__('Console')

    def __call__(self, key: str, *args: Any, **kwds: Any) -> None:
        self[key]()

    def assignApi(self):
        super().assignApi()
        web().mount('/console', self.api)

    def mount(self, superKey: str, commands: LeafyyConsoleCommands):
        for key, cmd in commands:
            self.append(cmd.copy({'key': f'{superKey}-{key}'}))

    def assignClis(self):
        self.assignCli()

    def format(self) -> list[str]:
        desc = ['Доступные команды:']

        for command in self.model():
            desc.append('{:<10}| {}'.format(
                f'{command[0]} ' +
                " ".join(command[1].arguments) if command[1].arguments else "",
                command[1].description))

        return desc
