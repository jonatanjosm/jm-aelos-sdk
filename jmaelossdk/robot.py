from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable

from .commands import SerialCommand
from .discovery import find_default_port, list_serial_ports
from .protocol import validate_byte_values
from .routine import MotionRoutine
from .types import SerialPortInfo


def _import_serial():
    try:
        import serial
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pyserial is required for robot connections. Install it with "
            "`python3 -m pip install pyserial` or install this package with "
            "`python3 -m pip install -e .`."
        ) from exc
    return serial


@dataclass
class AelosRobot:
    """Serial connection wrapper for an Aelos robot.

    This class deliberately starts small. The official app has several layers:
    a serial transport, low-level command framing, a motion compiler, and
    Blockly routines. This wrapper owns the transport and leaves protocol
    expansion to dedicated modules.
    """

    port: str | None = None
    baudrate: int = 115200
    timeout: float = 1.0
    write_timeout: float = 1.0
    auto_connect: bool = False

    def __post_init__(self) -> None:
        self._serial = None
        if self.auto_connect:
            self.connect()

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    @staticmethod
    def list_ports() -> list[SerialPortInfo]:
        return list_serial_ports()

    def resolve_port(self) -> str:
        if self.port:
            return self.port

        candidate = find_default_port()
        if candidate is None:
            raise RuntimeError(
                "No serial ports found. Connect the robot or pass port='/dev/cu...'."
            )

        self.port = candidate.device
        return self.port

    def connect(self) -> None:
        if self.is_connected:
            return

        port = self.resolve_port()
        serial = _import_serial()
        self._serial = serial.Serial(
            port=port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            write_timeout=self.write_timeout,
        )
        time.sleep(0.2)

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
        self._serial = None

    def __enter__(self) -> AelosRobot:
        self.connect()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def _require_connection(self):
        if not self.is_connected or self._serial is None:
            raise RuntimeError("Robot is not connected. Call connect() first.")
        return self._serial

    def write_bytes(self, data: bytes | bytearray | Iterable[int]) -> int:
        connection = self._require_connection()
        payload = bytes(data) if not isinstance(data, bytes) else data
        return connection.write(payload)

    def write_byte_values(self, values: list[int] | tuple[int, ...]) -> int:
        return self.write_bytes(validate_byte_values(values))

    def read(self, size: int = 1) -> bytes:
        connection = self._require_connection()
        return connection.read(size)

    def read_available(self) -> bytes:
        connection = self._require_connection()
        waiting = connection.in_waiting
        if waiting <= 0:
            return b""
        return connection.read(waiting)

    def flush(self) -> None:
        connection = self._require_connection()
        connection.flush()

    def reset_buffers(self) -> None:
        connection = self._require_connection()
        connection.reset_input_buffer()
        connection.reset_output_buffer()

    def send_command(self, command: SerialCommand, read_size: int = 64) -> bytes:
        """Send a low-level command payload and return the immediate response.

        This is intentionally conservative: it does not yet implement the full
        queueing/retry behavior from the Electron app. It gives us a clean
        testing hook for protocol discovery.
        """

        self.write_bytes(command.payload)
        if command.timeout is not None:
            connection = self._require_connection()
            previous_timeout = connection.timeout
            connection.timeout = command.timeout
            try:
                return self.read(read_size)
            finally:
                connection.timeout = previous_timeout
        return self.read(read_size)

    def run_routine(self, routine: MotionRoutine) -> None:
        """Run a migrated motion routine.

        Routine migration starts by preserving the official command sequence.
        Actual execution will be enabled after the motion compiler and download
        packet protocol are validated against the robot.
        """

        raise NotImplementedError(
            f"Routine execution is not wired yet. Routine {routine.name!r} "
            "is migrated and available through routine.to_script()."
        )
