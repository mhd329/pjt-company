from enum import IntEnum


class FrameType(IntEnum):
    NORMAL = 0
    GRAY = 1
    EDGE = 2

    @classmethod
    def get_name(cls, number) -> str | None:
        type_number = cls._value2member_map_.get(number)
        if type_number is not None:
            return type_number.name
        return