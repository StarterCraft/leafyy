import logging
from enum import Enum


class LeafyyLogLevel(Enum):
    'Объект для представления уровня журналирования'

    #Возможные уровни журналирования:
    DEBUG = logging.DEBUG       #Уровень ОТЛАДКА (все сообщения, по умолчанию)
    INFO = logging.INFO         #Уровень ИНФОРМАЦИЯ (важные сообщения)
    WARNING = logging.WARNING   #Уровень ПРЕДУПРЕЖДЕНИЯ (сообщения важностью
                                #ПРЕДУПРЕЖДЕНИЕ и выше)
    ERROR = logging.ERROR       #Уровень ОШИБКИ (только сообщения об ошибках и
                                #критические сообщения)
    CRITICAL = logging.CRITICAL #Уровень ТОЛЬКО КРИТИЧЕСКИЕ (только критические
                                #сообщения)

    #Спасибо ChatGPT
    def __lt__(self, other):
        if isinstance(other, LeafyyLogLevel):
            return self.value < other.value
        elif isinstance(other, int):
            return self.value < other
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, LeafyyLogLevel):
            return self.value <= other.value
        elif isinstance(other, int):
            return self.value <= other
        return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, LeafyyLogLevel):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, LeafyyLogLevel):
            return self.value != other.value
        elif isinstance(other, int):
            return self.value != other
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, LeafyyLogLevel):
            return self.value > other.value
        elif isinstance(other, int):
            return self.value > other
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, LeafyyLogLevel):
            return self.value >= other.value
        elif isinstance(other, int):
            return self.value >= other
        return NotImplemented
