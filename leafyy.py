from PySide6         import QtWidgets
from fastapi         import FastAPI
from typing          import List, Dict, Any


#Утилитарные функции
def deepget(self: dict, key: str, default: Any = None, sep: str = '.'):
    steps = key.split(sep)
    fetched = self

    for stepKey in steps:
        fetched = fetched.get(stepKey, False)

        if (not fetched):
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

def options():
    return app().options

def ui():
    return app().ui

def hardware():
    return app().hardware

def web() -> FastAPI:
    return app().web


from inspection.logger import LeafyyLogger


class LeafyyDirectDict:
    __reserved__ = [
        'keys',
        'get',
        'update'
        'toDict'
    ]

    def __init__(self, data: Dict[str, Any] = {}, **kd: Dict[str, Any]) -> None:
        self.update(data)
        self.update(kd)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]
    
    def __setitem__(self, key: str, value: Any):
        if (key in self.__reserved__):
            raise KeyError(f'Имя {key} зарезервировано')

        self.__dict__[key] = value
    
    def keys(self) -> List[str]:
        return [k for k in self.__dict__.keys() if (
            '_' not in k and k not in ['toDict', 'keys']
        )]
    
    def update(self, data: Dict[str, Any] = {}, **kd: Dict[str, Any]):
        for key in data.keys():
            if (key not in self.__reserved__ and '_' not in key):
                #Значение для key будет проигнорировано, если key — 
                #зарезервированное имя 
                self.__dict__[key] = data[key]

        for key in kd.keys():
            if (key not in self.__reserved__ and '_' not in key):
                #Значение для key будет проигнорировано, если key — 
                #зарезервированное имя 
                self.__dict__[key] = kd[key]

    def get(self, key: str, default: Any) -> Any:
        if (key not in self.__reserved__ and '_' not in key):
            return self.__dict__.get(key, default)

    def toDict(self):
        return {k: v for k, v in self.__dict__.items() if (
            '_' not in k and k not in ['toDict', 'keys']
        )}


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
