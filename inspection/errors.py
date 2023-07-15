from PySide6        import QtCore
from typing         import Iterator
from pydantic       import PositiveFloat
from autils         import fread, fwrite, lto

from leafyy.generic import LeafyyComponent
from .models        import ErrorRecord


class LeafyyErrors(
    LeafyyComponent,
    QtCore.QObject
    ):
    def __init__(self) -> None:
        super().__init__('Errors')

        self.errorBuffer = 'logs/buffer/.error'

        fwrite(self.errorBuffer, 'time;origin;message;\n') #csv стиль

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
        fwrite(self.errorBuffer, ';'.join(lto(str, error.dict().values())) + '\n', mode = 'a')

    def remove(self, key: int | str):
        if (isinstance(key, int)):
            stime = str(key)
            buf = fread(self.errorBuffer).splitlines()[1:]

            for line in buf[:]:
                if (line.split(';')[0] == stime):
                    buf.remove(line)

            fwrite(self.errorBuffer, '\n'.join(buf))

        if (isinstance(key, str)):
            buf = fread(self.errorBuffer).splitlines()[1:]

            for line in buf[:]:
                if (line.split(';')[1] == key):
                    buf.remove(line)

            fwrite(self.errorBuffer, '\n'.join(buf))
            
    def model(self) -> list[ErrorRecord]:
        return [
            ErrorRecord(
                time = ld.split(';')[0],
                origin = ld.split(';')[1],
                message = ld.split(';')[2]
                )
             for ld in fread(self.errorBuffer).splitlines()[1:]]
    
    def record(self, time: PositiveFloat, origin: str, message: str):
        self.append(ErrorRecord(time = time, origin = origin, message = message))

        self.logger.error(f'{origin} сообщил об ошибке: {message}', back = 2)
