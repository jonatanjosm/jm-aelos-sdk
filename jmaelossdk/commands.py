from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .protocol import BasicSerialCommand, validate_byte_values


SuccessVerifier = Callable[[bytes], bool]


@dataclass(frozen=True)
class SerialCommand:
    """Low-level command payload plus optional response verification."""

    name: str
    payload: bytes
    verifier: SuccessVerifier | None = None
    timeout: float | None = None

    def is_success(self, response: bytes) -> bool:
        if self.verifier is None:
            return bool(response)
        return self.verifier(response)


def command_payload(values: list[int] | tuple[int, ...]) -> bytes:
    return validate_byte_values(values)


def offline_mode() -> SerialCommand:
    return SerialCommand(
        name="offline_mode",
        payload=command_payload([BasicSerialCommand.OFFLINE_MODE]),
        verifier=lambda response: response.startswith(bytes([255])),
    )


def online_mode() -> SerialCommand:
    return SerialCommand(
        name="online_mode",
        payload=command_payload([BasicSerialCommand.ONLINE_MODE]),
        verifier=lambda response: response.startswith(bytes([255])),
    )


def check_robot_type() -> SerialCommand:
    return SerialCommand(
        name="check_robot_type",
        payload=command_payload([BasicSerialCommand.CHECK_ROBOT_TYPE, 0, 0, 0, 0, 0, 0, 0]),
        verifier=lambda response: response[:1] == bytes([BasicSerialCommand.CHECK_ROBOT_TYPE]),
    )


def send_download_request() -> SerialCommand:
    return SerialCommand(
        name="send_download_request",
        payload=command_payload([BasicSerialCommand.SEND_DOWNLOAD_REQUEST, 0, 0, 0, 0, 0, 0, 0]),
        verifier=lambda response: response == bytes([133, 0, 0, 0, 0, 0, 0, 0]),
    )


def set_all_servos(servos: list[int] | tuple[int, ...], speed: int) -> SerialCommand:
    if len(servos) != 16:
        raise ValueError("set_all_servos expects 16 servo values")
    return SerialCommand(
        name="set_all_servos",
        payload=command_payload(
            [BasicSerialCommand.SET_ALL_SERVOS, 0, 0, 0, 0, 16, 0, 0, *servos, speed]
        ),
        verifier=lambda response: len(response) >= 9
        and response[0] == 255
        and response[8] == BasicSerialCommand.SET_ALL_SERVOS,
    )


def high_precision_preview(servos: list[int] | tuple[int, ...]) -> SerialCommand:
    if len(servos) != 32:
        raise ValueError("high_precision_preview expects 32 servo bytes")
    return SerialCommand(
        name="high_precision_preview",
        payload=command_payload(
            [BasicSerialCommand.HIGH_PRECISION_PREVIEW, 0, 0, 0, 0, 32, 0, 0, *servos]
        ),
    )
