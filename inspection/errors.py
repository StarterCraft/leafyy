# -*- coding: utf-8 -*-
from PySide6        import QtCore
from typing         import Iterator
from datetime       import datetime
from pydantic       import PositiveFloat
from autils         import fread, fwrite, lto

from leafyy.generic import LeafyyComponent
from leafyy         import postgres
from .models        import ErrorRecord


class LeafyyErrors(
    LeafyyComponent,
    QtCore.QObject
    ):
    def __init__(self) -> None:
        super().__init__('Errors')

        #Очищаем таблицу в базе данных для текущего журнала
        postgres('inspection.truncateError')

    def __getitem__(self, key: int | str) -> list[ErrorRecord] | ErrorRecord:
        if (isinstance(key, str)):
            try:
                return [r for r in self.model() if (r['origin'] == key)]
            except IndexError as e:
                raise KeyError(f'Записей об ошибках из этого источника не найдено', key) from e

        else:
            return [r for r in self.model() if (r['time'] == int)]

    def __iter__(self) -> Iterator[ErrorRecord]:
        return iter(self.model())

    def __len__(self) -> int:
        return len(fread(self.errorBuffer).splitlines()[1:])

    def append(self, error: ErrorRecord):
        postgres().insert('inspection.insertError', tuple(error.dict().values()))

    def remove(self, key: datetime | str):
        if (isinstance(key, datetime)):
            postgres('inspection.deleteErrorByStamp', key)

        if (isinstance(key, str)):
            postgres('inspection.deleteErrorByOrigin', key)

    def model(self) -> list[ErrorRecord]:
        return [
            ErrorRecord(
                stamp = tu[0].timestamp(),
                origin = tu[1],
                caller = tu[2],
                message = tu[3]
                )
            for tu in postgres().fetchall('inspection.selectError', datetime.fromtimestamp(1))]

    def record(self, stamp: datetime, origin: str, caller: str, message: str):
        self.append(ErrorRecord(stamp = stamp, origin = origin, caller = caller, message = message))

    def format(self, errors: list[ErrorRecord] = None) -> list[str]:
        output = []

        if (not errors):
            errors = self.model()

        for error in errors:
            timeChunk = '<span style="color: gray; text-decoration: underlined;">'
            timeChunk += error.stamp.strftime('%m.%d %H:%M:%S.%f')
            timeChunk += '</span>'

            sourceChunk = f'[<span class="bold" style="color:darkorange;">{error.caller.split(".")[0]}</span>.'
            sourceChunk += f'<span style="color:blue;">{error.caller.split(".")[1]}</span>'

            if (error.origin):
                sourceChunk += f' (<span style="color: green;">{error.origin}</span>)'

            sourceChunk += ']:'

            line = ' '.join((timeChunk, sourceChunk, error.message))

            output.append(line)

        return output
