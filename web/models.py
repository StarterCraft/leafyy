# -*- coding: utf-8 -*-
from pydantic import BaseModel, constr


class User(BaseModel):
    username: str
    enabled:  bool
    warden:   bool
    master:   bool

class AccessibleUser(User):
    password: str
    _password: constr(
        min_length = 96,
        max_length = 96,
        strip_whitespace = True,
        to_upper = True,
        pattern = r'\b[A-Fa-f0-9]{96}\b'
        )

class UserForPasswordChange(BaseModel):
    username: str
    password: str

class UserForPasswordChange(BaseModel):
    username: str
    enabled:  str

class TokenString(BaseModel):
    token: constr(strip_whitespace = True)

class TokenPair(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str

