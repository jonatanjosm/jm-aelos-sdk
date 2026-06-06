"""Personal Python SDK for Aelos robot control."""

from .compiler import (
    CompiledInstruction,
    CompiledScript,
    compile_line,
    compile_routine,
    compile_script,
)
from .packaging import (
    DownloadPacket,
    build_download_packets,
    build_routine_download_packets,
)
from .robot import AelosRobot
from .routine import MotionRoutine
from .types import SerialPortInfo

__all__ = [
    "AelosRobot",
    "CompiledInstruction",
    "CompiledScript",
    "DownloadPacket",
    "MotionRoutine",
    "SerialPortInfo",
    "build_download_packets",
    "build_routine_download_packets",
    "compile_line",
    "compile_routine",
    "compile_script",
]
