from enum import Enum
import random


class EnumChoices(Enum):
    @classmethod
    def choices(cls):
        return [(key.value, key.value) for key in cls]

    @classmethod
    def keys(cls):
        return [key.value for key in cls]

    @classmethod
    def random(cls):
        return random.choice(list(cls.__members__.values()))


class BetsStatus(EnumChoices):
    OPENED = 'Открыты'
    CLOSED = 'Закрыты'
