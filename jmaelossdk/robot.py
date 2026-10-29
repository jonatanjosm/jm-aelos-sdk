from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Iterable

from .actions import get_action
from .commands import (
    SERVO_VALUE_RESPONSE_SIZE,
    SerialCommand,
    lock_servo,
    online_mode,
    parse_servo_value,
    send_download_request,
    set_all_servos,
    unlock_servo,
)
from .compiler import compile_routine
from .discovery import find_default_port, list_serial_ports
from .packaging import build_routine_download_packets
from .protocol import MotionOpcode, validate_byte_values
from .routine import MotionRoutine
from .routines.walk import walk_forward
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
        # The robot ignores lock/query commands until it is put in online
        # mode, as the Aelos Edu app does on connect (measured on the robot).
        self.enter_online_mode()

    def enter_online_mode(self) -> bool:
        """Put the robot controller in online mode. True if it confirmed."""

        self._require_connection().reset_input_buffer()
        command = online_mode()
        return command.is_success(self.send_command(command, read_size=9))

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

    def lock_servo(self, servo_id: int) -> int | None:
        """Energize one servo and return its position (None if no valid answer)."""

        response = self.send_command(
            lock_servo(servo_id), read_size=SERVO_VALUE_RESPONSE_SIZE
        )
        return parse_servo_value(response)

    def unlock_servo(self, servo_id: int) -> bool:
        """Release one servo so it can be moved by hand. True if the robot confirmed."""

        command = unlock_servo(servo_id)
        return command.is_success(self.send_command(command, read_size=9))

    def lock_all_servos(self) -> dict[int, int | None]:
        """Energize all 16 servos; a servo that does not answer does not stop the rest."""

        return {servo_id: self.lock_servo(servo_id) for servo_id in range(1, 17)}

    def action(
        self,
        name: str,
        *,
        timing_scale: float | None = None,
        min_wait: float | None = None,
        command_interval: float | None = None,
        final_read_delay: float | None = None,
        hold_servos: bool = True,
    ) -> list[bytes]:
        """Run a named migrated action, similar to the official SDK API.

        Timing arguments override the routine's own defaults for this call.
        """

        return self.run_routine(
            get_action(name),
            timing_scale=timing_scale,
            min_wait=min_wait,
            command_interval=command_interval,
            final_read_delay=final_read_delay,
            hold_servos=hold_servos,
        )

    def walk_forward(
        self,
        steps: int = 1,
        *,
        timing_scale: float | None = None,
        min_wait: float | None = None,
        command_interval: float | None = None,
        final_read_delay: float | None = None,
        hold_servos: bool = True,
    ) -> list[bytes]:
        """Walk forward a parametrized number of steps."""

        return self.run_routine(
            walk_forward(steps=steps),
            timing_scale=timing_scale,
            min_wait=min_wait,
            command_interval=command_interval,
            final_read_delay=final_read_delay,
            hold_servos=hold_servos,
        )

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
        timing_scale: float | None = None,
        min_wait: float | None = None,
        command_interval: float | None = None,
        final_read_delay: float | None = None,
        hold_servos: bool = True,
    ) -> list[bytes]:
        """Stream a migrated motion routine as direct servo commands."""

        timing_scale = routine.timing_scale if timing_scale is None else timing_scale
        min_wait = routine.min_wait if min_wait is None else min_wait
        command_interval = (
            routine.command_interval if command_interval is None else command_interval
        )
        final_read_delay = (
            routine.final_read_delay if final_read_delay is None else final_read_delay
        )

        # Validate before sending anything: a bad value must not leave the
        # robot halfway through a posture.
        if timing_scale <= 0:
            raise ValueError("timing_scale must be greater than 0")
        if min_wait < 0:
            raise ValueError("min_wait cannot be negative")
        if command_interval < 0:
            raise ValueError("command_interval cannot be negative")
        if final_read_delay < 0:
            raise ValueError("final_read_delay cannot be negative")

        # Drop leftovers from a previous run so they don't count as ACKs.
        self._require_connection().reset_input_buffer()

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
        # Read the movement ACKs first so the lock answers don't get mixed in.
        final_response = self.read_available()
        if frames_sent and hold_servos:
            self.lock_all_servos()
        return [final_response] if frames_sent else []

    def download_routine(self, routine: MotionRoutine) -> list[bytes]:
        """Download a routine file using the Aelos app download flow."""

        responses: list[bytes] = [self.send_command(send_download_request(), read_size=64)]
        for packet in build_routine_download_packets(routine):
            self.write_bytes(packet.payload)
            responses.append(self.read(64))
        return responses
