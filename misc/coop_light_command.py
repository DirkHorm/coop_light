from enum import Enum, auto

class CoopLightCommand(Enum):
    DUSK = auto()
    DAWN = auto()
    ON = auto()
    OFF = auto()

    @classmethod
    def has_command(cls, command):
        return command in cls.__members__
