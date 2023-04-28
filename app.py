from PyQt5         import QtWidgets


def _a():
    return QtWidgets.QApplication.instance()

def tr(*args, **kwargs):
    return _a().translate(*args, **kwargs)

def log():
    return _a().log

def options():
    return _a().options

def ui():
    return _a().ui

def hardware():
    return _a().hardware


from logger.logger import GreenyyLogger


class GreenyyComponent(object):
    '''
    Класс для большого количества похожих
    друг на друга объектов, имеющих общие атрибуты имени и логгера.
    '''
    def __init__(self, name, *args, loggerName: str = '', **kwargs) -> None:
        super().__init__(*args, **kwargs) #устранение ошибки инициализации
        self.name = name
        self.logger = GreenyyLogger(
            loggerName if loggerName else
            f'{name[0].capitalize()}{name[1:]}'
        )


