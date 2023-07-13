from fastapi  import FastAPI, Request, Response

from .models  import * 
from webutils import FileStreamResponse

class LeafyyLoggingApi:
    api: FastAPI

    def assign(self):
        @self.api.post('/log',
            name = 'Опубликовать сообщение журнала сервера',
            description = 'Приказывает серверу опубликовать сообщение журнала от логгера Web.')
        def logReport(message: LogReport, request: Request, response: Response):
            self.logger.publish(message.level, message.message.replace(
                'USER_IP', f'{request.client.host}:{request.client.port}'
            ))

            response.status_code = 202
            return response
        
        @self.api.get('/update', response_model = list[str],
            name = 'Получить стек новых сообщений консоли')
        def logUpdate():
            return self.getUpdateStack()
                
        @self.api.get('/{name}', response_class = FileStreamResponse,
            name = 'Скачивание файла журнала',
            description = 'Отправляет указанный файл журнала.')
        def logFile(request: Request, name: str) -> FileStreamResponse:
            return f'logs/{name}'
        
        
        @self.api.get('/config', response_model = LogConfig,
            name = 'Получить настройки журналирования',
            description = '')
        def logConfig(request: Request):
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
