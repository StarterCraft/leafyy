from collections import deque, namedtuple


LeafyyErrorRecord = namedtuple(
    'LeafyyErrorRecord',
    ['origin', 'error'])


class LeafyyErrors:
    def __init__(self) -> None:
        self.stack = deque(maxlen = 64)

        
