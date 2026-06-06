from __future__ import annotations

from dataclasses import dataclass

from .compiler import compile_routine
from .protocol import BasicSerialCommand, uint16_be, validate_byte_values
from .routine import MotionRoutine


DOWNLOAD_BLOCK_SIZE = 512
DOWNLOAD_COMMAND_OVERHEAD = 8
DOWNLOAD_HEADER_OVERHEAD = 11


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

    header = bytes([170, 170, len(name_bytes), *name_bytes])
    data_block_size = block_size - len(name_bytes) - DOWNLOAD_HEADER_OVERHEAD
    if data_block_size <= 0:
        raise ValueError("block_size is too small for file_name")

    packets: list[DownloadPacket] = []
    crc_bytes = bytes(uint16_be(crc16_xmodem(payload_data)))
    chunks = _generate_data_blocks(payload_data, data_block_size)

    for zero_based_index, chunk in enumerate(chunks):
        packet_index = zero_based_index + 1
        is_last = packet_index == len(chunks)
        if packet_index > 255:
            raise ValueError("download payload exceeds 256 packets")
        length = (
            len(payload_data) - data_block_size * (len(chunks) - 1) + len(name_bytes) + 3
            if is_last
            else block_size - DOWNLOAD_COMMAND_OVERHEAD
        )

        packet_values = [
            BasicSerialCommand.DOWNLOAD_FILE,
            255 if packet_index > 255 else packet_index,
            0,
            1 if is_last else 0,
            *uint16_be(length),
            *crc_bytes,
            *header,
            *chunk,
        ]
        packets.append(
            DownloadPacket(
                index=packet_index,
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


def _generate_data_blocks(data: bytes, block_size: int) -> list[bytes]:
    chunks = [data[index : index + block_size] for index in range(0, len(data), block_size)]
    last = chunks[-1]
    chunks[-1] = last + bytes(block_size - len(last))
    return chunks
