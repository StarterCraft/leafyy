# -*- coding: utf-8 -*-
from PySide6 import QtCore
from typing  import Iterator, Any

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


class LeafyyIterableComponent(LeafyyComponent):
    def __getitem__(self, key) -> Any:
        ...

    def __iter__(self) -> Iterator[Any]:
        ...

    def __len__(self) -> int:
        ...

    def model(self) -> Any:
        ...

    def append(self, obj):
        ...

    def remove(self, obj):
        ...


class LeafyyWorker(QtCore.QObject):
    def __init__(self, f, *a, **kw):
        super().__init__()
        self.f = f
        self.a = a
        self.kw = kw

    def run(self):
        self.f(*self.a, **self.kw)


class LeafyyThreadedWorker(QtCore.QObject):
    def __init__(self, f, *a, **kw) -> None:
        super().__init__()
        self.f = f
        self.a = a
        self.kw = kw
        self.t = QtCore.QThread()

    def _exec(self):
        self.f(*self.a, **self.kw)

    def run(self):
        self.moveToThread(self.t)
        self.t.finished.connect(self.deleteLater)
        self.t.started.connect(self._exec)
        self.t.start()

    def exit(self):
        self.t.requestInterruption()
