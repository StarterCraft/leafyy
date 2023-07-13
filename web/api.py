#coding=utf-8
from typing     import Annotated
from glob       import glob
from autils     import fread, fwrite
from requests   import get
from packaging  import version as versioning
from re         import findall

from fastapi              import FastAPI, Request
from fastapi.templating   import Jinja2Templates
from starlette.templating import _TemplateResponse
from fastapi.responses    import Response, HTMLResponse, FileResponse

from leafyy               import devices as _devices
from leafyy               import log as logging
from leafyy               import web
from leafyy.generic       import LeafyyComponent
from webutils             import JsResponse, CssResponse

from .template import Template


class LeafyyWebInterface(LeafyyComponent):
    def __init__(self) -> None:
        super().__init__('WebUi')

        self.jinja = Jinja2Templates('web/templates')

        self.pages = self.loadTemplates()

    def __getitem__(self, key: str) -> Template:
        return self.pages[key]

    def loadTemplates(self) -> dict[str, Template]:
        td = {}        
        templateNames = [name.split('\\')[-1] for name in glob('web/templates/*')]

        for name in templateNames:
            td.update({name: Template(self.jinja, f'{name}/{name}.jinja')})

        return td
    
    def assignApi(self):
        self.assign()

    def assign(self):
        @web().get('/leafyy.css', response_class = CssResponse,   
            name = 'Получить глобальный CSS',
            description = 'Получает глобальный CSS-файл, необходимый для работы веб-сервиса.')
        def getGlobalCss() -> str:
            return fread('web/leafyy.css')

        @web().get('/{cssId}.css', response_class = CssResponse,
            name = 'Получить CSS по ID',
            description = 'Получает указанный CSS-файл на основе предоставленного ID.')
        def getCss(cssId: str) -> str:
            return fread(f'web/templates/{cssId}/{cssId}.css')

        @web().get('/leafyy.js', response_class = JsResponse,
            name = 'Получить глобальный JS',
            description = 'Получает глобальный JS-файл, необходимый для работы веб-сервиса.')
        def getGlobalJs() -> str:
            return fread('web/leafyy.js')

        @web().get('/{scriptId}.js', response_class = JsResponse,
            name = 'Получить JS по ID',
            description = 'Получает указанный JS-файл на основе предоставленного ID.')
        def getJs(scriptId: str) -> str:
            return fread(f'web/templates/{scriptId}/{scriptId}.js')

        @web().get('/site.webmanifest', response_class = Response,
            name = 'Получить веб манифест',
            description = 'Получает файл веб манифеста.')
        def getWebManifest() -> str:
            return fread('web/site.webmanifest')

        @web().get('/resources/{resourceId}', response_class = FileResponse,
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

        @web().get('/libraries/web/{libraryId}.js', response_class = JsResponse,
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

        @web().get('/libraries/cache/{libraryId}.js', response_class = JsResponse,
            name = 'Получить кэшированную JS-библиотеку')
        def getCachedLibrary(libraryId: str, request: Request) -> str:
            code = fread(f'web/libraries/{libraryId}.js')
            version = getCachedLibraryVersion(libraryId)

            self.logger.debug(
                f'Загружена локальная библиотека {libraryId} (версия {version})'
                f' для клиента {request.client.host}'
            )

            return code

        @web().get('/libraries/{libraryId}.js', response_class = JsResponse,
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

        @web().get('/favicon.ico', response_class = FileResponse,
            name = 'Получить favicon',
            description = 'Получает favicon.')
        def getFavicon() -> FileResponse:
            return f'web/resources/favicon.svg'

        @web().get('/auth', response_class = HTMLResponse,
            name = 'Авторизация',
            description = 'Отрисовывает страницу авторизации.')
        def auth(request: Request) -> _TemplateResponse:
            return self['auth'].render(request)

        @web().get('/', response_class = HTMLResponse, 
            name = 'Главная страница',
            description = 'Отрисовывает главную страницу с информацией о грядках.')
        def index(request: Request) -> _TemplateResponse:
            return self['index'].render(
                request,
                devices = _devices().model()
            )

        @web().get('/devices', response_class = HTMLResponse,
            name = 'Страница оборудования',
            description = 'Отрисовывает страницу оборудования с информацией о нем.')
        def devices(request: Request) -> _TemplateResponse:
            return self['devices'].render(
                request,
                devices = _devices().model()
            )

        @web().get('/rules', response_class = HTMLResponse,
            name = 'Правила',
            description = 'Отрисовывает страницу с правилами.')
        def rules(request: Request) -> _TemplateResponse:
            return self['rules'].render(request)

        @web().get('/log', response_class = HTMLResponse,
            name = 'Журнал',
            description = 'Отрисовывает страницу доступа к консоли и журналу.')
        def log(request: Request) -> _TemplateResponse:
            return self['log'].render(
                request,
                devices = _devices().model(),
                console = logging().getGeneralStack(),
                logConfig = logging().getConfig()
            )

        @web().get('/log/view', response_class = HTMLResponse,
            name = 'Просмотр файла журнала',
            description = 'Отрисовывает страницу со списком файлов журнала.')
        def logList(request: Request, reversed = 0) -> _TemplateResponse:
            return self['logList'].render(
                request,
                logData = logging().getLogFolderSummary(reversed),
                reversed = reversed
            )

        @web().get('/log/view/{name}', response_class = HTMLResponse,
            name = 'Просмотр файла журнала',
            description = 'Отрисовывает страницу просмотра указанного файла журнала.')
        def logFileView(request: Request, name: str) -> _TemplateResponse:
            return self['logView'].render(
                request,
                logFile = logging().getLogFile(name, html = True)
            )
        
        @web().get('/doc', response_class = HTMLResponse,
            name = 'Документация',
            description = 'Отрисовывает страницу с документацией.')
        def doc(request: Request) -> _TemplateResponse:
            return self['doc'].render(request)
