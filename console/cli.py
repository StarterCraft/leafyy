# -*- coding: utf-8 -*-
from PySide6         import QtCore
from leafyy.generic  import LeafyyWorker
from leafyy          import app


class LeafyyConsoleCli:
    def assignCli(self):
        @self.command('Help',
            displayName = 'Помощь',
            description = 'Отобразить сообщение о помощи')
        def help():
            self.logger.info('\n' + '\n'.join(self.format()))

        @self.command('Exit',
            displayName = 'Остановить службу',
            description = 'Завершить работу службы')
        def exit():
            app().quit_()
