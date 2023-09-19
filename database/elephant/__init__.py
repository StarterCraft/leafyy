# -*- coding: utf-8 -*-
from PySide6           import QtCore
from typing            import Any, Iterator, Iterable, Annotated
from os                import sep as psep
from glob              import glob

from psycopg2._psycopg import connection, cursor
from psycopg2          import connect
from psycopg2.sql      import SQL
from psycopg2.extras   import NamedTupleConnection, NamedTupleCursor

from autils            import fread

from leafyy            import properties


class LeafyyPostgresDatabase(
    QtCore.QObject
    ):
    credentialsChanged = QtCore.Signal()

    queries: dict[str, Annotated[str, SQL]] = {}

    dbName: str
    dbUser: str
    dbPassword: str
    dbHost: str

    def __init__(self) -> None:
        super().__init__()

        self.updateCredentials()
        self.updateQueries()

    def __getitem__(self, key: int | str) -> Annotated[str, SQL]:
        if (isinstance(key, str)):
            return self.queries[key]

        else:
            return self.queries.values()[key]

    def __iter__(self) -> Iterator[Annotated[str, SQL]]:
        return iter(self.queries.values())

    def __len__(self) -> int:
        return len(self.queries)

    def credentials(self) -> dict[str, str]:
        return {
            'dbname': self.dbName,
            'user': self.dbUser,
            'password': self.dbPassword,
            'host': self.dbHost
        }

    def updateCredentials(self) -> None:
        self.dbName = config('postgres.dbname', 'leafyy')
        self.dbUser = config('postgres.user', 'leafyy')
        self.dbPassword = config('postgres.password', 'debug')
        self.dbHost = config('postgres.host', 'localhost')

        self.credentialsChanged.emit()

    def updateQueries(self) -> None:
        fileNames = glob('**/sql/*.sql')

        for fileName in fileNames:
            qName = f'{fileName.split(psep)[-3]}.{fileName.split(psep)[-1][:-4]}'
            self.queries.update({qName: fread(fileName)})

    def connect(self) -> connection:
        return connect(
            connection_factory = NamedTupleConnection,
            cursor_factory = NamedTupleCursor,
            **self.credentials()
            )

    def execute(self, queryId: str, *args: Any) -> cursor:
        with self.connect() as _connection:
            with _connection.cursor() as _cursor:
                _cursor.execute(self[queryId], args)
                return _cursor

    def single(self, queryId: str, *args: Any) -> tuple:
        with self.connect() as _connection:
            with _connection.cursor() as _cursor:
                _cursor.execute(self[queryId], args)
                return _cursor.fetchone()

    def fetchone(self, queryId: str, *args: Any) -> tuple:
        return self.single(queryId, *args)

    def select(self, queryId: str, quantity: int, *args: Any) -> Iterable[tuple]:
        with self.connect() as _connection:
            with _connection.cursor() as _cursor:
                _cursor.execute(self[queryId], args)
                return _cursor.fetchmany(quantity) if (quantity > 0) else _cursor.fetchall()

    def fetchmany(self, queryId: str, quantity: int, *args: Any) -> Iterable[tuple]:
        with self.connect() as _connection:
            with _connection.cursor() as _cursor:
                _cursor.execute(self[queryId], args)
                return _cursor.fetchmany(quantity)

    def fetchall(self, queryId: str, *args: Any) -> Iterable[tuple]:
        with self.connect() as _connection:
            with _connection.cursor() as _cursor:
                _cursor.execute(self[queryId], args)
                return _cursor.fetchall()

    def insert(self, queryId: str, *args: Any) -> None:
        with self.connect() as _connection:
            with _connection.cursor() as _cursor:
                _cursor.execute(self[queryId], args)
                _connection.commit()
