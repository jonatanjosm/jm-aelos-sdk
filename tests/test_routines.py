from jmaelossdk.routine import MotionRoutine
from jmaelossdk.routines.basic import PUSH_UP, STAND_UP, push_up, stand_up
from jmaelossdk.routines.combat import KICK, kick


def test_kick_routine_metadata() -> None:
    assert isinstance(KICK, MotionRoutine)
    assert KICK.name == "Kick"
    assert KICK.source == "Aelos Edu"


def test_kick_routine_commands_match_migration() -> None:
    assert len(KICK.commands) == 43
    assert KICK.commands[0] == (
        "MOTOrigid16(65,65,65,70,70,70,70,70,65,65,65,50,50,50,50,50)"
    )
    assert KICK.commands[-1] == "MOTOwait()"
    assert "DelayMs(200)" in KICK.commands
    assert KICK.to_script().count("MOTOmove16") == 13


def test_kick_function_returns_routine_without_robot() -> None:
    assert kick() is KICK


def test_push_up_routine_commands_match_migration() -> None:
    assert isinstance(PUSH_UP, MotionRoutine)
    assert PUSH_UP.name == "Push-up"
    assert len(PUSH_UP.commands) == 71
    assert PUSH_UP.commands[0] == (
        "MOTOrigid16(90,90,90,40,40,40,40,40,90,90,90,40,40,40,40,40)"
    )
    assert PUSH_UP.commands[-1] == "MOTOwait()"
    assert PUSH_UP.to_script().count("MOTOmove16") == 23
    assert (
        "MOTOmove16(90, 15, 155, 100, 162, 175, 35, 100, 110, 185, 45, "
        "100, 38, 25, 165, 100)"
    ) in PUSH_UP.commands
    assert (
        "MOTOmove16(80, 30, 100, 100, 142, 145, 77, 100, 120, 170, 100, "
        "100, 58, 55, 123, 100)"
    ) in PUSH_UP.commands
    assert PUSH_UP.timing_scale == 2.0
    assert PUSH_UP.min_wait == 0.25


def test_push_up_function_returns_routine_without_robot() -> None:
    assert push_up() is PUSH_UP


def test_stand_up_routine_commands_match_migration() -> None:
    assert isinstance(STAND_UP, MotionRoutine)
    assert STAND_UP.name == "Stand_up"
    assert len(STAND_UP.commands) == 4
    assert STAND_UP.commands == (
        "MOTOrigid16(60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60)",
        "MOTOsetspeed(30)",
        "MOTOmove16(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100)",
        "MOTOwait()",
    )
    assert STAND_UP.to_script().count("MOTOmove16") == 1


def test_stand_up_function_returns_routine_without_robot() -> None:
    assert stand_up() is STAND_UP
