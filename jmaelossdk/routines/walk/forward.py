from __future__ import annotations

from jmaelossdk.routine import MotionRoutine, RoutineRunner
from jmaelossdk.routines.basic import STAND_UP


_WALK_FORWARD_RIGID = (
    "MOTOrigid16(25,25,25,75,75,90,80,70,25,25,25,75,75,90,80,70)"
)

_WALK_FORWARD_START = [
    "MOTOsetspeed(45)",
    "MOTOmove16(80, 30, 100, 99, 93, 54, 122, 90, 120, 170, 100, 98, 107, 146, 75, 95)",
    "MOTOwait()",
    "MOTOsetspeed(60)",
    "MOTOmove16(80, 30, 80, 99, 115, 99, 103, 100, 120, 170, 80, 101, 109, 134, 91, 94)",
    "MOTOwait()",
    "MOTOsetspeed(70)",
    "MOTOmove16(80, 30, 80, 99, 110, 74, 121, 100, 120, 170, 80, 101, 114, 137, 91, 100)",
    "MOTOwait()",
    "MOTOsetspeed(80)",
    "MOTOmove16(80, 30, 80, 99, 110, 61, 126, 104, 120, 170, 80, 101, 100, 127, 94, 100)",
    "MOTOwait()",
    "MOTOsetspeed(80)",
    "MOTOmove16(80, 30, 120, 99, 91, 66, 109, 102, 120, 170, 120, 101, 85, 101, 97, 100)",
    "MOTOwait()",
    "MOTOsetspeed(80)",
    "MOTOmove16(80, 30, 120, 99, 86, 63, 110, 100, 120, 170, 120, 101, 90, 126, 79, 100)",
    "MOTOwait()",
    "MOTOsetspeed(80)",
    "MOTOmove16(80, 30, 120, 99, 100, 73, 106, 100, 120, 170, 120, 101, 90, 139, 74, 94)",
    "MOTOwait()",
]

_WALK_FORWARD_CONTINUE = [
    "MOTOsetspeed(75)",
    "MOTOmove16(80, 30, 80, 99, 115, 99, 103, 100, 120, 170, 80, 101, 109, 134, 89, 98)",
    "MOTOwait()",
    "MOTOsetspeed(80)",
    "MOTOmove16(80, 30, 80, 99, 110, 74, 121, 100, 120, 170, 80, 101, 114, 137, 89, 100)",
    "MOTOwait()",
    "MOTOsetspeed(80)",
    "MOTOmove16(80, 30, 80, 99, 110, 61, 126, 104, 120, 170, 80, 101, 100, 127, 94, 100)",
    "MOTOwait()",
    "MOTOsetspeed(75)",
    "MOTOmove16(80, 30, 120, 99, 91, 66, 111, 102, 120, 170, 120, 101, 85, 101, 97, 100)",
    "MOTOwait()",
    "MOTOsetspeed(80)",
    "MOTOmove16(80, 30, 120, 99, 86, 63, 111, 100, 120, 170, 120, 101, 90, 126, 79, 100)",
    "MOTOwait()",
    "MOTOsetspeed(80)",
    "MOTOmove16(80, 30, 120, 99, 100, 73, 106, 100, 120, 170, 120, 101, 90, 139, 74, 96)",
    "MOTOwait()",
]

_WALK_FORWARD_EXIT = [
    "MOTOsetspeed(65)",
    "MOTOmove16(80, 30, 120, 96, 95, 70, 110, 100, 120, 170, 120, 102, 109, 146, 75, 96)",
    "MOTOwait()",
    "MOTOsetspeed(45)",
    "MOTOmove16(80, 30, 100, 99, 93, 54, 122, 90, 120, 170, 100, 98, 107, 146, 75, 95)",
    "MOTOwait()",
    "MOTOsetspeed(15)",
    "MOTOmove16(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100)",
    "MOTOwait()",
]


def walk_forward(
    steps: int = 1,
    robot: RoutineRunner | None = None,
) -> MotionRoutine:
    if steps <= 0:
        raise ValueError("steps must be greater than 0")

    name = "Walk_forward" if steps == 1 else f"Walk_forward_{steps}_steps"
    routine = MotionRoutine.from_commands(
        name=name,
        timing_scale=1.0,
        min_wait=0.12,
        command_interval=0.001,
        final_read_delay=1.0,
        commands=[
            _WALK_FORWARD_RIGID,
            *_WALK_FORWARD_START,
            *(_WALK_FORWARD_CONTINUE * (steps - 1)),
            *_WALK_FORWARD_EXIT,
            *STAND_UP.commands,
        ],
    )
    if robot is not None:
        routine.run(robot)
    return routine


WALK_FORWARD = walk_forward()


__all__ = ["WALK_FORWARD", "walk_forward"]
