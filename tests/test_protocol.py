from jmaelossdk.commands import check_robot_type, high_precision_preview
from jmaelossdk.protocol import MotionOpcode, validate_byte_values


def test_motion_opcode_values() -> None:
    assert MotionOpcode.MOVE == 128
    assert MotionOpcode.SPEED == 129
    assert MotionOpcode.WAIT == 130
    assert MotionOpcode.RIGID == 133


def test_validate_byte_values() -> None:
    assert validate_byte_values([128, 32, 1]) == b"\x80 \x01"


def test_check_robot_type_payload() -> None:
    assert check_robot_type().payload == bytes([71, 0, 0, 0, 0, 0, 0, 0])


def test_high_precision_preview_length() -> None:
    command = high_precision_preview([0] * 32)
    assert len(command.payload) == 40
