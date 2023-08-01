# -*- coding: utf-8 -*-
from leafyy           import postgres

from .models          import AccessibleUser
from .exceptions      import UsernameNotFoundException, UserDisabledException


class LeafyyUserHandler:
    @staticmethod
    def getUser(username: str) -> AccessibleUser:
        thisUser = postgres().fetchone('web.selectUser', username)

        if (not thisUser):
            raise UsernameNotFoundException(username)
        elif (not thisUser.enabled):
            raise UserDisabledException(username)
        else:
            return AccessibleUser(**thisUser.asdict())

