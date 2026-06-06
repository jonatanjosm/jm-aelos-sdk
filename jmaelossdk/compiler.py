from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .protocol import MotionOpcode, uint16_be, validate_byte_values
from .routine import MotionRoutine


_CALL_PATTERN = re.compile(r"^(?P<name>[A-Za-z0-9_]+)\((?P<args>.*)\)$")
_SERVO16_VALUE_COUNT = 16
_SERVO16_PAYLOAD_SIZE = 32


@dataclass(frozen=True)
class CompiledInstruction:
    """One motion source line compiled to the Aelos motion VM bytecode."""

    source: str
    opcode: MotionOpcode
    data: bytes


@dataclass(frozen=True)
class CompiledScript:
    """Compiled bytecode plus per-line traceability back to source commands."""

    instructions: tuple[CompiledInstruction, ...]
    name: str | None = None
    source: str | None = None

    @property
    def data(self) -> bytes:
        return b"".join(instruction.data for instruction in self.instructions)


def compile_line(line: str) -> CompiledInstruction:
    """Compile one Aelos Blockly motion command line to bytes."""

    source = line.strip()
    if not source:
        raise ValueError("motion command line cannot be empty")

    name, args = _parse_call(source)
    if name == "MOTOmove16":
        values = _parse_int_args(args, expected_count=_SERVO16_VALUE_COUNT)
        return _instruction(
            source, MotionOpcode.MOVE, [MotionOpcode.MOVE, _SERVO16_PAYLOAD_SIZE, *values]
        )
    if name == "MOTOrigid16":
        values = _parse_int_args(args, expected_count=_SERVO16_VALUE_COUNT)
        return _instruction(
            source, MotionOpcode.RIGID, [MotionOpcode.RIGID, _SERVO16_PAYLOAD_SIZE, *values]
        )
    if name == "MOTOsetspeed":
        values = _parse_int_args(args, expected_count=1, max_value=255)
        return _instruction(source, MotionOpcode.SPEED, [MotionOpcode.SPEED, values[0]])
    if name == "MOTOwait":
        _parse_int_args(args, expected_count=0)
        return _instruction(source, MotionOpcode.WAIT, [MotionOpcode.WAIT])
    if name == "DelayMs":
        values = _parse_int_args(args, expected_count=1, max_value=0xFFFF)
        return _instruction(source, MotionOpcode.DELAY, [MotionOpcode.DELAY, *uint16_be(values[0])])

    raise ValueError(f"unsupported motion command: {name}")


def compile_script(script: str | Iterable[str]) -> CompiledScript:
    lines = script.splitlines() if isinstance(script, str) else script
    instructions = tuple(compile_line(line) for line in lines if line.strip())
    if not instructions:
        raise ValueError("motion script cannot be empty")
    return CompiledScript(instructions=instructions)


def compile_routine(routine: MotionRoutine) -> CompiledScript:
    compiled = compile_script(routine.commands)
    return CompiledScript(
        instructions=compiled.instructions,
        name=routine.name,
        source=routine.source,
    )


def _instruction(
    source: str, opcode: MotionOpcode, values: list[int] | tuple[int, ...]
) -> CompiledInstruction:
    return CompiledInstruction(
        source=source,
        opcode=opcode,
        data=validate_byte_values(values),
    )


def _parse_call(line: str) -> tuple[str, str]:
    match = _CALL_PATTERN.match(line)
    if match is None:
        raise ValueError(f"invalid motion command syntax: {line}")
    return match.group("name"), match.group("args").strip()


def _parse_int_args(args: str, expected_count: int, max_value: int = 255) -> list[int]:
    if args:
        values = [int(part.strip(), 10) for part in args.split(",")]
    else:
        values = []

    if len(values) != expected_count:
        raise ValueError(f"expected {expected_count} args, got {len(values)}")
    for value in values:
        if not 0 <= value <= max_value:
            raise ValueError(f"argument out of range: {value}")
    return values
