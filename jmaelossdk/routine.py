from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


class RoutineRunner(Protocol):
    def run_routine(self, routine: "MotionRoutine") -> None:
        ...


@dataclass(frozen=True)
class MotionRoutine:
    """A migrated Aelos motion routine.

    Commands are stored in the same textual motion language used by the Aelos
    Edu Blockly generators. Keeping the source commands intact makes migration
    auditable while we finish the binary transport layer.
    """

    name: str
    commands: tuple[str, ...]
    source: str = "Aelos Edu"
    timing_scale: float = 1.2
    min_wait: float = 0.08
    command_interval: float = 0.15
    final_read_delay: float = 1.0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("routine name cannot be empty")
        if not self.commands:
            raise ValueError("routine commands cannot be empty")

    @classmethod
    def from_commands(
        cls,
        name: str,
        commands: Iterable[str],
        source: str = "Aelos Edu",
        timing_scale: float = 1.2,
        min_wait: float = 0.08,
        command_interval: float = 0.15,
        final_read_delay: float = 1.0,
    ) -> "MotionRoutine":
        normalized = tuple(command.strip() for command in commands if command.strip())
        return cls(
            name=name,
            commands=normalized,
            source=source,
            timing_scale=timing_scale,
            min_wait=min_wait,
            command_interval=command_interval,
            final_read_delay=final_read_delay,
        )

    def to_script(self) -> str:
        return "\n".join(self.commands)

    def run(self, robot: RoutineRunner) -> None:
        robot.run_routine(self)
