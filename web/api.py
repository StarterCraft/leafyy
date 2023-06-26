#coding=utf-8
from typing     import Annotated
from glob       import glob
from utillo     import fread, fwrite
from requests   import get
from packaging  import version as versioning
from re         import findall

from fastapi              import FastAPI, Request
from fastapi.templating   import Jinja2Templates
from starlette.templating import _TemplateResponse
from fastapi.responses    import Response, JSONResponse, HTMLResponse, FileResponse

from leafyy     import hardware as _hardware
from leafyy     import log as logging
from leafyy     import LeafyyComponent

from .template  import Template
from .responses import *
from models     import *


class LeafyyWebInterfaceApi(LeafyyComponent):
    def __init__(self) -> None:
        super().__init__('Web')

        self.jinja = Jinja2Templates('web/templates')

        self.pages: dict[str, Template] = {}

        self.loadWebPageTemplates()

    def __getitem__(self, key: str) -> Template:
        return self.pages[key]

    def loadWebPageTemplates(self):
        templateNames = [name.split('\\')[-1] for name in glob('web/templates/*')]

        for name in templateNames:
            self.pages.update({name: Template(self.jinja, f'{name}/{name}.jinja')})

    def assign(self, service: FastAPI):
        @service.get('/leafyy.css', response_class = CssResponse,   
            name = 'Получить глобальный CSS',
            description = 'Получает глобальный CSS-файл, необходимый для работы веб-сервиса.')
        def getGlobalCss() -> str:
            return fread('web/leafyy.css')

        @service.get('/{cssId}.css', response_class = CssResponse,
            name = 'Получить CSS по ID',
            description = 'Получает указанный CSS-файл на основе предоставленного ID.')
        def getCss(cssId: str) -> str:
            return fread(f'web/templates/{cssId}/{cssId}.css')

        @service.get('/leafyy.js', response_class = JsResponse,
            name = 'Получить глобальный JS',
            description = 'Получает глобальный JS-файл, необходимый для работы веб-сервиса.')
        def getGlobalJs() -> str:
            return fread('web/leafyy.js')

        @service.get('/{scriptId}.js', response_class = JsResponse,
            name = 'Получить JS по ID',
            description = 'Получает указанный JS-файл на основе предоставленного ID.')
        def getJs(scriptId: str) -> str:
            return fread(f'web/templates/{scriptId}/{scriptId}.js')

        @service.get('/site.webmanifest', response_class = Response,
            name = 'Получить веб манифест',
            description = 'Получает файл веб манифеста.')
        def getWebManifest() -> str:
            return fread('web/site.webmanifest')

        @service.get('/resources/{resourceId}', response_class = FileResponse,
            name = 'Получить ресурс по ID',
            description = 'Получает указанный ресурс на основе предоставленного ID.')
        def getResource(resourceId: str) -> FileResponse:
            return f'web/resources/{resourceId}'

        def getWebLibraryVersion(libraryId: str) -> versioning.Version:
            '''
            Метод получает версию библиотеки из API и парсит её с помощью модуля versioning.
            '''
            fetched = get(f'https://api.cdnjs.com/libraries/{libraryId}?fields=version').json()
            _version = fetched['version']
            return versioning.parse(_version)

        def getCachedLibraryVersion(libraryId: str) -> versioning.Version:
            '''
            Метод получает версию локальной копии библиотеки из файла, парсит её и возвращает.
            '''
            code = fread(f'web/libraries/{libraryId}.js')
            regexMatch = findall(r'(v([0-9A-Za-z][.]{0,1})+)|$', code)[0]
            version = 'undefined'

            if (regexMatch[0]):
                version = regexMatch[0][1:]

            return versioning.parse(version)

        @service.get('/libraries/web/{libraryId}.js', response_class = JsResponse,
            name = 'Получить актуальную JS-библиотеку')
        def getWebLibrary(libraryId: str, request: Request) -> str:
            '''
            Метод получает новую версию библиотеки из API, сохраняет её в файл и возвращает её в виде строки.
            '''
            fetched = get(f'https://api.cdnjs.com/libraries/{libraryId}?fields=latest,version').json()
            code = get(fetched['latest']).text
            version = fetched['version']

            #Проверка версии локальной библиотеки уже проведена,
            #поэтому здесь она не ведётся
            fwrite(f'web/libraries/{libraryId}.js', code)

            self.logger.info(
                f'Загружена локальная библиотека {libraryId} (версия {version})'
                f' для клиента {request.client.host}. Локальная библиотека обновлена'
            )

            return code

        @service.get('/libraries/cache/{libraryId}.js', response_class = JsResponse,
            name = 'Получить кэшированную JS-библиотеку')
        def getCachedLibrary(libraryId: str, request: Request) -> str:
            code = fread(f'web/libraries/{libraryId}.js')
            version = getCachedLibraryVersion(libraryId)

            self.logger.debug(
                f'Загружена локальная библиотека {libraryId} (версия {version})'
                f' для клиента {request.client.host}'
            )

            return code

        @service.get('/libraries/{libraryId}.js', response_class = JsResponse,
            name = 'Получить JS-библиотеку')
        def getLibrary(libraryId: str, request: Request) -> str:
            '''
            Метод получает библиотеку для клиента из API или из локальной копии
            в зависимости от того, какая версия библиотеки актуальна. Если 
            актуальность не удаётся проверить, метод подключит локальную копию и
            вернёт её.
            '''
            d = ''

            try: 
                #Если на сервере хранится актуальная версия библиотеки,
                #подключить её. Если вышла новая, скачать её и записать
                #в файл.
                if (getCachedLibraryVersion(libraryId) < getWebLibraryVersion(libraryId)):
                    d = getWebLibrary(libraryId, request)

                else:
                    d = getCachedLibrary(libraryId, request)
                
            except Exception as e:
                self.logger.error(
                    f'Не удалось подключить актуальную версию библиотеки {libraryId} '
                    f'для клиента {request.client.host}: {type(e).__name__}: {e}. Подключаю локальную '
                    'библиотеку...'
                ) 
                d = getCachedLibrary(libraryId, request)

            return d

        @service.get('/favicon.ico', response_class = FileResponse,
            name = 'Получить favicon',
            description = 'Получает favicon.')
        def getFavicon() -> FileResponse:
            return f'web/resources/favicon.svg'

        @service.get('/auth', response_class = HTMLResponse,
            name = 'Авторизация',
            description = 'Отрисовывает страницу авторизации.')
        def auth(request: Request) -> _TemplateResponse:
            return self['auth'].render(request)

        @service.get('/', response_class = HTMLResponse, 
            name = 'Главная страница',
            description = 'Отрисовывает главную страницу с информацией о грядках.')
        def index(request: Request) -> _TemplateResponse:
            return self['index'].render(
                request,
                hardware = _hardware().getDevices()
            )

        @service.get('/hardware', response_class = HTMLResponse,
            name = 'Страница оборудования',
            description = 'Отрисовывает страницу оборудования с информацией о нем.')
        def hardware(request: Request) -> _TemplateResponse:
            return self['hardware'].render(
                request,
                hardware = _hardware().getDevices()
            )
        
        @service.get('/hardware/config',
            name = 'Страница оборудования',
            description = 'Отрисовывает страницу оборудования с информацией о нем.')
        def hardware(request: Request) -> _TemplateResponse:
            return self['hardware'].render(
                request,
                hardware = _hardware().getDevices()
            )

        @service.get('/rules', response_class = HTMLResponse,
            name = 'Правила',
            description = 'Отрисовывает страницу с правилами.')
        def rules(request: Request) -> _TemplateResponse:
            return self['rules'].render(request)
        
        @service.get('/log', response_class = HTMLResponse,
            name = 'Журнал',
            description = 'Отрисовывает страницу доступа к консоли и журналу.')
        def log(request: Request) -> _TemplateResponse:
            return self['log'].render(
                request,
                hardware = _hardware().getDevices(),
                console = logging().getGeneralStack(),
                logConfig = logConfig(request)
            )
        
        @service.get('/log/update', response_model = list[str],
            name = 'Получить стек новых сообщений консоли')
        def logUpdate():
            return logging().getUpdateStack()
        
        @service.get('/log/view', response_class = HTMLResponse,
            name = 'Просмотр файла журнала',
            description = 'Отрисовывает страницу со списком файлов журнала.')
        def logList(request: Request, reversed = 0) -> _TemplateResponse:
            return self['logList'].render(
                request,
                logData = logging().getLogFolderSummary(reversed),
                reversed = reversed
            )
        
        @service.get('/log/{name}', response_class = FileStreamResponse,
            name = 'Скачивание файла журнала',
            description = 'Отправляет указанный файл журнала.')
        def logFile(request: Request, name: str) -> FileStreamResponse:
            return f'logs/{name}'
        
        @service.get('/log/view/{name}', response_class = HTMLResponse, response_model = LogFile,
            name = 'Просмотр файла журнала',
            description = 'Отрисовывает страницу просмотра указанного файла журнала.')
        def logFileView(request: Request, name: str) -> _TemplateResponse:
            return self['logView'].render(
                request,
                logFile = logging().getLogFile(name, html = True)
            )

        @service.post('/log',
            name = 'Опубликовать сообщение журнала сервера',
            description = 'Приказывает серверу опубликовать сообщение журнала от логгера Web.')
        def logReport(message: LogReport, request: Request, response: Response):
            self.logger.publish(message.level, message.message.replace(
                'USER_IP', f'{request.client.host}:{request.client.port}'
            ))

            response.status_code = 202
            return response
        
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
        def setLogConfig(config: LogConfig, request: Request):
            print(config)
            logging().setGlobalLogLevel(config.level)
            logging().configLogSources(config.sources)

        @service.get('/doc', response_class = HTMLResponse,
            name = 'Документация',
            description = 'Отрисовывает страницу с документацией.')
        def doc(request: Request) -> _TemplateResponse:
            return self['doc'].render(request)

        @service.post('/console')
        def testConsole(
            command: ConsoleCommand,
            response: Response):
            response.status_code = 202
            return response

