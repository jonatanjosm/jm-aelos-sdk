from __future__ import annotations

from dataclasses import dataclass

from .compiler import compile_routine
from .protocol import BasicSerialCommand, uint16_be, validate_byte_values
from .routine import MotionRoutine


DOWNLOAD_BLOCK_SIZE = 512


@dataclass(frozen=True)
class DownloadPacket:
    """One serial download packet payload for a compiled motion byte stream."""

    index: int
    is_last: bool
    payload: bytes


def crc16_xmodem(data: bytes | bytearray) -> int:
    crc = 0
    for byte in bytes(data):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def build_download_packets(
    data: bytes | bytearray,
    file_name: str,
    *,
    block_size: int = DOWNLOAD_BLOCK_SIZE,
) -> list[DownloadPacket]:
    if block_size <= 0:
        raise ValueError("block_size must be positive")

    payload_data = bytes(data)
    if not payload_data:
        raise ValueError("download data cannot be empty")

    name_bytes = file_name.encode("utf-8")
    if not name_bytes or len(name_bytes) > 255:
        raise ValueError("file_name must encode to 1..255 bytes")

    header = bytes([len(name_bytes), *name_bytes, 0])
    packets: list[DownloadPacket] = []
    crc_bytes = bytes(uint16_be(crc16_xmodem(payload_data)))

    for index, offset in enumerate(range(0, len(payload_data), block_size)):
        chunk = payload_data[offset : offset + block_size]
        is_last = offset + block_size >= len(payload_data)
        if index > 255:
            raise ValueError("download payload exceeds 256 packets")

        packet_values = [
            BasicSerialCommand.DOWNLOAD_FILE,
            index,
            1 if is_last else 0,
            *uint16_be(len(chunk)),
            *crc_bytes,
            *header,
            *chunk,
        ]
        packets.append(
            DownloadPacket(
                index=index,
                is_last=is_last,
                payload=validate_byte_values(packet_values),
            )
        )

    return packets


def build_routine_download_packets(
    routine: MotionRoutine,
    *,
    file_name: str | None = None,
    block_size: int = DOWNLOAD_BLOCK_SIZE,
) -> list[DownloadPacket]:
    compiled = compile_routine(routine)
    return build_download_packets(
        compiled.data,
        file_name=file_name or routine.name,
        block_size=block_size,
    )
