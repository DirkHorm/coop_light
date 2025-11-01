from enum import Enum, auto

class CoopLightCommand(Enum):
    DUSK = auto()
    DAWM = auto()

    @classmethod
    def has_command(cls, command):
        return command in cls.__members__
