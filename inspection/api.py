from fastapi             import FastAPI, Request, Response

from leafyy.generic    import LeafyyComponent

from .models import LogReport

class LeafyyLoggingApi(LeafyyComponent):
    def assign(self, logging, service: FastAPI):
        @service.post('/log',
            name = 'Опубликовать сообщение журнала сервера',
            description = 'Приказывает серверу опубликовать сообщение журнала от логгера Web.')
        def logReport(message: LogReport, request: Request, response: Response):
            self.logger.publish(message.level, message.message.replace(
                'USER_IP', f'{request.client.host}:{request.client.port}'
            ))

            response.status_code = 202
            return response
        
        @service.get('/log/update', response_model = list[str],
            name = 'Получить стек новых сообщений консоли')
        def logUpdate():
            return logging().getUpdateStack()
                
        @service.get('/log/{name}', response_class = FileStreamResponse,
            name = 'Скачивание файла журнала',
            description = 'Отправляет указанный файл журнала.')
        def logFile(request: Request, name: str) -> FileStreamResponse:
            return f'logs/{name}'
        
        
        @service.get('/log/config', response_model = LogConfig,
            name = 'Получить настройки журналирования',
            description = '')
        def logConfig(request: Request):
            c = {
                'level': logging().globalLevel._name_,
                'sources': logging().getLogSources()
                }
            
            return c
        
        @service.put('/log/config',
            name = 'Записать настройки журналирования',
            description = '')
        def putLogConfig(config: LogConfig, request: Request):
            print(config)
            logging().setGlobalLogLevel(config.level)
            logging().configLogSources(config.sources)
