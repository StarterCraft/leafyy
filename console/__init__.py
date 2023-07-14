from PySide6 import QtCore
from cmd2    import Cmd

from leafyy.generic import LeafyyComponent, LeafyyWorker


class LeafyyConsole(
    LeafyyComponent,
    QtCore.QObject,
    Cmd
    ):
    prompt = '(Leafyy Console)'

    def __init__(self):
        super().__init__('Console')

    def do_test(self, args):
        print('Test 18')

    def start(self):
        self.cmdloop()
