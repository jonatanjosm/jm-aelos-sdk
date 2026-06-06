from __future__ import annotations

from enum import IntEnum


class MotionOpcode(IntEnum):
    """Motion VM opcodes found in the Aelos Edu Electron bundle."""

    DELAY = 74
    MOVE = 128
    SPEED = 129
    WAIT = 130
    RIGID = 133


class BasicSerialCommand(IntEnum):
    """Low-level command ids found in the Aelos Edu Electron bundle."""

    OFFLINE_MODE = 204
    ONLINE_MODE = 131
    CHECK_ROBOT_1S = 51
    CHECK_ROBOT_TYPE = 71
    GET_SERVOS_VALUE = 121
    UNLOCK_SERVO = 120
    UPDATE_SERVO = 118
    GET_ALL_SERVOS = 167
    SET_ALL_SERVOS = 145
    SEND_DOWNLOAD_REQUEST = 132
    DOWNLOAD_FILE = 112
    HIGH_PRECISION_PREVIEW = 35


def uint16_be(value: int) -> list[int]:
    if not 0 <= value <= 0xFFFF:
        raise ValueError(f"uint16 out of range: {value}")
    return [(value >> 8) & 0xFF, value & 0xFF]


def validate_byte_values(values: list[int] | tuple[int, ...]) -> bytes:
    for value in values:
        if not isinstance(value, int) or not 0 <= value <= 255:
            raise ValueError(f"invalid byte value: {value!r}")
    return bytes(values)
