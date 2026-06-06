from __future__ import annotations

from jmaelossdk.routine import MotionRoutine, RoutineRunner


STAND_UP = MotionRoutine.from_commands(
    name="Stand_up",
    commands=[
        "MOTOrigid16(60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60)",
        "MOTOsetspeed(30)",
        "MOTOmove16(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100)",
        "MOTOwait()",
    ],
)


def stand_up(robot: RoutineRunner | None = None) -> MotionRoutine:
    if robot is not None:
        STAND_UP.run(robot)
    return STAND_UP


__all__ = ["STAND_UP", "stand_up"]
