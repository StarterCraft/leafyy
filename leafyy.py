from PySide6         import QtWidgets
from fastapi         import FastAPI
from typing          import List, Dict, Any


#Утилитарные функции
def deepget(self: dict, key: str, default: Any = None, sep: str = '.'):
    steps = key.split(sep)
    fetched = self

    for stepKey in steps:
        fetched = fetched.get(stepKey, NotImplemented)

        if (fetched is NotImplemented):
            return default
    
    return fetched

def deepupdate(self: dict, key: str, value: Any, sep: str = '.'):
    pass

#Доступ к компонентам
def app() -> QtWidgets.QApplication:
    return QtWidgets.QApplication.instance()

def tr(*args, **kwargs) -> str:
    return app().translate(*args, **kwargs)

def log():
    return app().log

def options(key: str = None, default: Any = None, sep: str = '.') -> dict | Any:
    if (key):
        return app().options(key, default, sep)
    
    return app().options

def ui():
    return app().ui

def hardware():
    return app().hardware

def web() -> FastAPI:
    return app().web


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
