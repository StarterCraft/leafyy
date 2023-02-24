import enum


class GreenyyStatus(enum.Enum):
    Active = 0
    Disabled = 1
    Failed = 2


class GreenyyObject(object):
    def __init__(self, name: str, description: str, status: GreenyyStatus):
        super().__init__()
        self.displayName = name
        self.description = description
        self.status = status
