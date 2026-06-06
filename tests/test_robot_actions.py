import jmaelossdk
from jmaelossdk import AelosRobot
from jmaelossdk.protocol import BasicSerialCommand
from jmaelossdk.routines.combat import KICK


class FakeSerial:
    is_open = True
    in_waiting = 0

    def __init__(self) -> None:
        self.writes: list[bytes] = []
        self.timeout = 1.0

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


def test_action_streams_named_routine_servo_moves() -> None:
    robot = AelosRobot()
    fake_serial = FakeSerial()
    robot._serial = fake_serial

    responses = robot.action("Kick")

    assert len(responses) == 13
    assert fake_serial.writes[0] == bytes(
        [
            BasicSerialCommand.SET_ALL_SERVOS,
            0,
            0,
            0,
            0,
            16,
            0,
            0,
            80,
            30,
            100,
            97,
            93,
            55,
            124,
            95,
            120,
            170,
            100,
            103,
            107,
            145,
            76,
            105,
            12,
        ]
    )


def test_download_routine_keeps_app_download_flow() -> None:
    robot = AelosRobot()
    fake_serial = FakeSerial()
    robot._serial = fake_serial

    responses = robot.download_routine(KICK)

    assert responses == [b"", b""]
    assert fake_serial.writes[0] == bytes(
        [BasicSerialCommand.SEND_DOWNLOAD_REQUEST, 0, 0, 0, 0, 0, 0, 0]
    )
    assert fake_serial.writes[1][0] == BasicSerialCommand.DOWNLOAD_FILE


def test_action_rejects_unknown_routine() -> None:
    robot = AelosRobot()
    robot._serial = FakeSerial()

    try:
        robot.action("Right_Kick_hit")
    except ValueError as exc:
        assert "Unknown action" in str(exc)
    else:
        raise AssertionError("unknown action should fail")
