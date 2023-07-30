# -*- coding: utf-8 -*-
from fastapi  import APIRouter, Request, Response

from leafyy   import web

from .models  import *
from webutils import FileStreamResponse


class LeafyyLoggingApi:
    api = APIRouter(
        prefix = '/log',
        tags = ['log']
    )

    def assignApi(self):
        @self.api.post('',
            name = 'Опубликовать сообщение журнала сервера',
            description = 'Приказывает серверу опубликовать сообщение журнала от логгера Web.')
        def postLogReport(request: Request, response: Response, message: LogRecord):
            self[message.logger].publish(message.level, message.message.replace(
                'USER_IP', f'{request.client.host}:{request.client.port}'
            ))

            response.status_code = 202
            return response

        @self.api.get('/update', response_model = list[str],
            name = 'Получить стек новых сообщений консоли, начиная с времени stamp')
        def getLogUpdate(request: Request, begin: PositiveFloat):
            return self.format(begin = begin)

        @self.api.get('/{name}', response_class = FileStreamResponse,
            name = 'Скачивание файла журнала',
            description = 'Отправляет указанный файл журнала.')
        def getLogFile(request: Request, name: str) -> FileStreamResponse:
            return f'logs/{name}'

        @self.api.get('/config', response_model = LogConfig,
            name = 'Получить настройки журналирования',
            description = '')
        def getLogConfig(request: Request):
            c = {
                'level': self.globalLevel.name,
                'sources': self.getLogSources()
                }

            return c

        @self.api.put('/config',
            name = 'Записать настройки журналирования',
            description = '')
        def putLogConfig(config: LogConfig, request: Request):
            self.setGlobalLogLevel(config.level)
            self.configLogSources(config.sources)

        web().include_router(self.api)
