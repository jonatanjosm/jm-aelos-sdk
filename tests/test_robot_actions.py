import jmaelossdk
from jmaelossdk import AelosRobot
from jmaelossdk.packaging import build_routine_download_packets
from jmaelossdk.routines.combat import KICK


class FakeSerial:
    is_open = True
    in_waiting = 0

    def __init__(self) -> None:
        self.writes: list[bytes] = []

    def write(self, payload: bytes) -> int:
        self.writes.append(payload)
        return len(payload)

    def read(self, size: int = 1) -> bytes:
        return b""

    def close(self) -> None:
        self.is_open = False


def test_init_returns_robot_without_auto_connect_when_disabled() -> None:
    robot = jmaelossdk.init(auto_connect=False)

    assert isinstance(robot, AelosRobot)
    assert robot.is_connected is False


def test_action_sends_named_routine_packets() -> None:
    robot = AelosRobot()
    fake_serial = FakeSerial()
    robot._serial = fake_serial

    responses = robot.action("Kick")

    expected_packets = build_routine_download_packets(KICK)
    assert responses == [b""]
    assert fake_serial.writes == [packet.payload for packet in expected_packets]


def test_action_rejects_unknown_routine() -> None:
    robot = AelosRobot()
    robot._serial = FakeSerial()

    try:
        robot.action("Right_Kick_hit")
    except ValueError as exc:
        assert "Unknown action" in str(exc)
    else:
        raise AssertionError("unknown action should fail")
