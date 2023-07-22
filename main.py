# -*- coding: utf-8 -*-
import sys

from leafyy.application import Leafyy


__version__ = '0.1dev4'


def main(args: list[str]) -> int:
    Leafyy.checkEnvironment()
    app = Leafyy(args, __version__)

    app.start()

    return app.exec()


if (__name__ == '__main__'):
    sys.exit(main(sys.argv))
