from jmaelossdk.actions import available_actions, get_action
from jmaelossdk.compiler import compile_routine
from jmaelossdk.protocol import MotionOpcode
from jmaelossdk.routines.combat import KICK


def test_all_actions_compile() -> None:
    for name in available_actions():
        compiled = compile_routine(get_action(name))
        assert compiled.instructions, name


def test_kick_lines_match_app_js_compiler_behavior_line_by_line() -> None:
    expected_by_source = []
    for line in KICK.commands:
        if line.startswith("MOTOrigid16"):
            values = _parse_args(line)
            expected_by_source.append(bytes([MotionOpcode.RIGID, 32, *values]))
        elif line.startswith("MOTOmove16"):
            values = _parse_args(line)
            expected_by_source.append(bytes([MotionOpcode.MOVE, 32, *values]))
        elif line.startswith("MOTOsetspeed"):
            expected_by_source.append(bytes([MotionOpcode.SPEED, *_parse_args(line)]))
        elif line == "MOTOwait()":
            expected_by_source.append(bytes([MotionOpcode.WAIT]))
        elif line.startswith("DelayMs"):
            delay = _parse_args(line)[0]
            expected_by_source.append(bytes([MotionOpcode.DELAY, delay >> 8, delay & 0xFF]))
        else:
            raise AssertionError(f"unmapped JS compiler expectation for line: {line}")

    actual = [instruction.data for instruction in compile_routine(KICK).instructions]

    assert actual == expected_by_source


def _parse_args(line: str) -> list[int]:
    start = line.index("(") + 1
    end = line.rindex(")")
    args = line[start:end].strip()
    if not args:
        return []
    return [int(arg.strip()) for arg in args.split(",")]
