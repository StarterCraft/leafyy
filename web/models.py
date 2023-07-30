from pydantic import BaseModel, constr


class User(BaseModel):
    username: str
    password: constr(
        min_length = 96, 
        max_length = 96,
        strip_whitespace = True,
        to_upper = True,
        regex = r'\b[A-Fa-f0-9]{96}\b')
    admin:    bool
