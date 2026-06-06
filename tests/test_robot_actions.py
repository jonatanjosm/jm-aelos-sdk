import jmaelossdk
from jmaelossdk import AelosRobot
from jmaelossdk.protocol import BasicSerialCommand
from jmaelossdk.routine import MotionRoutine
from jmaelossdk.routines.combat import KICK


class FakeSerial:
    is_open = True

    def __init__(self) -> None:
        self.writes: list[bytes] = []
        self.timeout = 1.0
        self.read_calls = 0
        self.in_waiting = 0

    def write(self, payload: bytes) -> int:
        self.writes.append(payload)
        return len(payload)

    def read(self, size: int = 1) -> bytes:
        self.read_calls += 1
        return b""

    def close(self) -> None:
        self.is_open = False


def test_init_returns_robot_without_auto_connect_when_disabled() -> None:
    robot = jmaelossdk.init(auto_connect=False)

    assert isinstance(robot, AelosRobot)
    assert robot.is_connected is False


def test_action_streams_named_routine_servo_moves() -> None:
    robot = AelosRobot(sleeper=lambda _: None)
    fake_serial = FakeSerial()
    robot._serial = fake_serial

    responses = robot.action("Kick")

    assert responses == [b""]
    assert fake_serial.read_calls == 0
    assert len(fake_serial.writes) == 13
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


def test_push_up_action_is_registered() -> None:
    assert jmaelossdk.get_action("Push-up").name == "Push-up"


def test_run_routine_waits_after_move_until_motowait() -> None:
    sleeps: list[float] = []
    routine = MotionRoutine.from_commands(
        name="Timing",
        commands=[
            "MOTOsetspeed(20)",
            "MOTOmove16(80, 30, 100, 100, 100, 100, 100, 100, 120, 170, 100, 100, 100, 100, 100, 100)",
            "MOTOwait()",
            "MOTOmove16(80, 30, 100, 110, 100, 100, 100, 100, 120, 170, 100, 100, 100, 100, 100, 100)",
            "MOTOwait()",
            "DelayMs(200)",
        ],
    )
    robot = AelosRobot(sleeper=sleeps.append)
    robot._serial = FakeSerial()

    robot.run_routine(routine, timing_scale=2.0, min_wait=0.05)

    assert sleeps == [0.15, 0.175, 0.15, 0.1, 0.2, 1.0]


def test_run_routine_reads_available_once_after_stream() -> None:
    robot = AelosRobot(sleeper=lambda _: None)
    fake_serial = FakeSerial()
    fake_serial.in_waiting = 9
    robot._serial = fake_serial

    responses = robot.run_routine(KICK)

    assert fake_serial.read_calls == 1
    assert responses == [b""]


def test_calculate_move_wait_respects_speed_and_bounds() -> None:
    robot = AelosRobot()

    assert robot.calculate_move_wait(10, distance=0) == 0.08
    assert robot.calculate_move_wait(10, distance=10) == 0.08
    assert robot.calculate_move_wait(10, distance=10, timing_scale=2.0) == 0.16
    assert robot.calculate_move_wait(255, distance=10, min_wait=0.02) == 0.02
