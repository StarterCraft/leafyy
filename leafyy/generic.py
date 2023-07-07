from PySide6           import QtCore
from inspection.logger import LeafyyLogger


class LeafyyComponent(object):
    '''
    Класс для большого количества похожих
    друг на друга объектов, имеющих общие атрибуты имени и логгера.
    '''
    def __init__(
            self, 
            name: str, 
            *args, 
            loggerName: str = '',
            displayName: str = '',
            **kwargs
        ) -> None:
        super().__init__(*args, **kwargs) #устранение ошибки инициализации
        self.name = name
        self.displayName = displayName
        self.logger = LeafyyLogger(
            loggerName if loggerName else
            f'{name[0].capitalize()}{name[1:]}'
        )


class LeafyyWorker(QtCore.QThread):
    def __init__(self, f) -> None:
        super().__init__()
        self.f = f

    def run(self):
        self.f()
        super().run()
