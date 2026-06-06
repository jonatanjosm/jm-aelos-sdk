from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Iterable

from .actions import get_action
from .commands import SerialCommand, send_download_request, set_all_servos
from .compiler import compile_routine
from .discovery import find_default_port, list_serial_ports
from .packaging import build_routine_download_packets
from .protocol import MotionOpcode, validate_byte_values
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


def init(
    port: str | None = None,
    *,
    auto_connect: bool = True,
    baudrate: int = 115200,
    timeout: float = 1.0,
    write_timeout: float = 1.0,
) -> "AelosRobot":
    return AelosRobot(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        write_timeout=write_timeout,
        auto_connect=auto_connect,
    )


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
    sleeper: Callable[[float], None] = time.sleep

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

    def action(self, name: str) -> list[bytes]:
        """Run a named migrated action, similar to the official SDK API."""

        return self.run_routine(get_action(name))

    @staticmethod
    def calculate_move_wait(
        speed: int,
        *,
        distance: int,
        timing_scale: float = 1.0,
        min_wait: float = 0.08,
        distance_factor: float = 0.025,
    ) -> float:
        if speed <= 0:
            raise ValueError("speed must be greater than 0")
        if distance < 0:
            raise ValueError("distance cannot be negative")
        if timing_scale <= 0:
            raise ValueError("timing_scale must be greater than 0")
        if min_wait < 0:
            raise ValueError("min_wait cannot be negative")
        return max(min_wait, distance * distance_factor / speed) * timing_scale

    def run_routine(
        self,
        routine: MotionRoutine,
        *,
        timing_scale: float = 1.2,
        min_wait: float = 0.08,
        command_interval: float = 0.15,
        final_read_delay: float = 1.0,
    ) -> list[bytes]:
        """Stream a migrated motion routine as direct servo commands."""

        frames_sent = 0
        speed = 15
        previous_servos: list[int] | None = None
        pending_distance = 0
        has_pending_move = False
        for instruction in compile_routine(routine).instructions:
            if instruction.opcode == MotionOpcode.SPEED:
                speed = instruction.data[1]
            elif instruction.opcode == MotionOpcode.MOVE:
                servos = list(instruction.data[2:])
                self.write_bytes(set_all_servos(servos, speed).payload)
                frames_sent += 1
                if command_interval > 0:
                    self.sleeper(command_interval)
                if previous_servos is not None:
                    pending_distance = max(
                        abs(current - previous)
                        for current, previous in zip(servos, previous_servos)
                    )
                else:
                    pending_distance = max(
                        abs(current - 100)
                        for current in servos
                    )
                previous_servos = servos
                has_pending_move = True
            elif instruction.opcode == MotionOpcode.WAIT and has_pending_move:
                self.sleeper(
                    self.calculate_move_wait(
                        speed,
                        distance=pending_distance,
                        timing_scale=timing_scale,
                        min_wait=min_wait,
                    )
                )
                has_pending_move = False
            elif instruction.opcode == MotionOpcode.DELAY:
                delay_ms = (instruction.data[1] << 8) + instruction.data[2]
                self.sleeper(delay_ms / 1000)
        if final_read_delay > 0:
            self.sleeper(final_read_delay)
        final_response = self.read_available()
        return [final_response] if frames_sent else []

    def download_routine(self, routine: MotionRoutine) -> list[bytes]:
        """Download a routine file using the Aelos app download flow."""

        responses: list[bytes] = [self.send_command(send_download_request(), read_size=64)]
        for packet in build_routine_download_packets(routine):
            self.write_bytes(packet.payload)
            responses.append(self.read(64))
        return responses
