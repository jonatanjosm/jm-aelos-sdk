from jmaelossdk.compiler import compile_line, compile_routine, compile_script
from jmaelossdk.protocol import MotionOpcode
from jmaelossdk.routines.combat import KICK


def test_compile_basic_motion_lines() -> None:
    assert compile_line("MOTOsetspeed(12)").data == bytes([MotionOpcode.SPEED, 12])
    assert compile_line("MOTOwait()").data == bytes([MotionOpcode.WAIT])
    assert compile_line("DelayMs(200)").data == bytes([MotionOpcode.DELAY, 0, 200])


def test_compile_move_and_rigid_lines() -> None:
    assert compile_line(
        "MOTOrigid16(65,65,65,70,70,70,70,70,65,65,65,50,50,50,50,50)"
    ).data == bytes(
        [MotionOpcode.RIGID, 32, 65, 65, 65, 70, 70, 70, 70, 70, 65, 65, 65, 50, 50, 50, 50, 50]
    )
    assert compile_line(
        "MOTOmove16(80, 30, 100, 97, 93, 55, 124, 95, 120, 170, 100, 103, 107, 145, 76, 105)"
    ).data == bytes(
        [MotionOpcode.MOVE, 32, 80, 30, 100, 97, 93, 55, 124, 95, 120, 170, 100, 103, 107, 145, 76, 105]
    )


def test_compile_kick_script_to_bytes() -> None:
    compiled = compile_script(KICK.to_script())

    assert len(compiled.instructions) == 43
    assert compiled.data[:18] == bytes(
        [MotionOpcode.RIGID, 32, 65, 65, 65, 70, 70, 70, 70, 70, 65, 65, 65, 50, 50, 50, 50, 50]
    )
    assert compiled.data[-1:] == bytes([MotionOpcode.WAIT])
    assert len(compiled.data) == 300


def test_compile_routine_preserves_metadata() -> None:
    compiled = compile_routine(KICK)

    assert compiled.name == "Kick"
    assert compiled.source == "Aelos Edu"
    assert compiled.data == compile_script(KICK.to_script()).data


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
