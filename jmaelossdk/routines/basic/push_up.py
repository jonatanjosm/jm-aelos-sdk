from __future__ import annotations

from jmaelossdk.routine import MotionRoutine, RoutineRunner


_PUSH_UP_REPEAT = [
    "MOTOsetspeed(50)",
    "MOTOmove16(77, 32, 168, 99, 109, 50, 154, 100, 120, 168, 35, 101, 91, 151, 46, 100)",
    "MOTOwait()",
    "MOTOsetspeed(50)",
    "MOTOmove16(10, 93, 177, 99, 109, 50, 154, 100, 183, 104, 27, 101, 91, 151, 46, 100)",
    "MOTOwait()",
]


PUSH_UP = MotionRoutine.from_commands(
    name="Push-up",
    timing_scale=2.0,
    min_wait=0.25,
    command_interval=0.12,
    final_read_delay=1.5,
    commands=[
        "MOTOrigid16(90,90,90,40,40,40,40,40,90,90,90,40,40,40,40,40)",
        "MOTOmove16(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100)",
        "MOTOwait()",
        "MOTOmove16(80, 41, 154, 100, 110, 140, 55, 100, 120, 159, 46, 100, 90, 60, 145, 100)",
        "MOTOwait()",
        "MOTOmove16(80, 41, 157, 98, 156, 150, 44, 100, 120, 159, 43, 99, 43, 49, 156, 99)",
        "MOTOwait()",
        "MOTOsetspeed(35)",
        "MOTOsetspeed(12)",
        "MOTOmove16(100, 10, 185, 100, 160, 150, 35, 100, 100, 190, 15, 100, 40, 50, 165, 100)",
        "MOTOwait()",
        "MOTOsetspeed(53)",
        "MOTOmove16(15, 80, 190, 99, 109, 50, 154, 100, 185, 120, 10, 101, 91, 151, 46, 100)",
        "MOTOwait()",
        "MOTOrigid16(65,65,65,60,60,60,60,60,65,65,65,60,60,60,60,60)",
        *(_PUSH_UP_REPEAT * 6),
        "MOTOsetspeed(53)",
        "MOTOmove16(15, 80, 190, 100, 120, 90, 45, 100, 185, 120, 10, 100, 80, 110, 155, 100)",
        "MOTOwait()",
        "MOTOsetspeed(53)",
        "MOTOmove16(90, 15, 155, 100, 162, 175, 35, 100, 110, 185, 45, 100, 38, 25, 165, 100)",
        "MOTOwait()",
        "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)",
        "DelayMs(50)",
        "MOTOsetspeed(42)",
        "MOTOmove16(90, 15, 140, 100, 162, 175, 50, 100, 110, 185, 60, 100, 38, 25, 150, 100)",
        "MOTOwait()",
        "MOTOsetspeed(28)",
        "MOTOmove16(80, 30, 113, 100, 155, 175, 62, 100, 120, 170, 87, 100, 45, 25, 138, 100)",
        "MOTOwait()",
        "DelayMs(100)",
        "MOTOmove16(80, 30, 100, 100, 142, 145, 77, 100, 120, 170, 100, 100, 58, 55, 123, 100)",
        "MOTOwait()",
        "MOTOsetspeed(35)",
        "MOTOmove16(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100)",
        "MOTOwait()",
    ],
)


def push_up(robot: RoutineRunner | None = None) -> MotionRoutine:
    if robot is not None:
        PUSH_UP.run(robot)
    return PUSH_UP


__all__ = ["PUSH_UP", "push_up"]
