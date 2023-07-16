from fastapi import FastAPI, Request


class LeafyyConsoleApi:
    api = FastAPI(
        name = 'API Листочка: подсистема моментальных команд'
    )

    def assignApi(self):
        @self.api.post('/', status_code = 202,
            name = 'Исполнить команду',
            description = 'Исполняет команду, находящуюся в теле запроса.')
        def postExecCmd(request: Request, exec: str):
            self[exec.split()[0]](exec.split()[1:])
