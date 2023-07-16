# -*- coding: utf-8 -*-
from sys import argv, exit as iexit

from leafyy.application import Leafyy


__version__ = '0.1a3'


def main(args: list[str]) -> int:
    Leafyy.checkEnvironment()
    app = Leafyy(args)

    app.devices.initDevices()
    app.devices.start()
    
    app.web.start()
    app.logger.debug('Привет, ребят!')

    app.web.assignApis()
    app.cli.assignCommands()

    return app.exec()


if (__name__ == '__main__'):
    iexit(main(argv))
