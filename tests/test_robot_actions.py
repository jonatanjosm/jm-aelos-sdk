from jmaelossdk import AelosRobot
from jmaelossdk.protocol import BasicSerialCommand


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

    def reset_input_buffer(self) -> None:
        pass

    def close(self) -> None:
        self.is_open = False


def test_action_streams_named_routine_servo_moves() -> None:
    robot = AelosRobot(sleeper=lambda _: None)
    fake_serial = FakeSerial()
    robot._serial = fake_serial

    responses = robot.action("Kick")

    assert responses == [b""]
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
