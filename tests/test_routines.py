from jmaelossdk.routine import MotionRoutine
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
