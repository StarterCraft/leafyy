from PySide6         import QtCore, QtWidgets
from fastapi         import FastAPI
from typing          import Any, overload


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
    steps = key.split(sep)
    container = self

    for stepKey in steps[:-1]:
        container = container.get(stepKey)

    container.update({steps[-1]: value})

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

def web() -> FastAPI:
    return app().web

def devices():
    return app().devices

def rules():
    return app().rules

def ui():
    return app().ui

def cli(cmd = None):
    if (cmd):
        return app().cli(cmd)
    
    return app().cli
