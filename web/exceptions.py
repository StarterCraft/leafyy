# -*- coding: utf-8 -*-
class UsernameNotFoundException(Exception):
    def __init__(self, arg: str) -> None:
        super().__init__(f'Пользователь {arg} не существует')


class UserDisabledException(Exception):
    def __init__(self, arg: str) -> None:
        super().__init__(
            f'Профиль пользователя {arg} не может '
            'быть использован, так как он отключен')
