from jmaelossdk.packaging import (
    build_download_packets,
    build_routine_download_packets,
    crc16_xmodem,
)
from jmaelossdk.routines.combat import KICK


def test_crc16_xmodem_known_vector() -> None:
    assert crc16_xmodem(b"123456789") == 0x31C3


def test_build_download_packets_uses_app_download_command_shape() -> None:
    packets = build_download_packets(bytes(range(10)), file_name="Kick")

    assert len(packets) == 1
    assert packets[0].index == 0
    assert packets[0].is_last is True
    assert packets[0].payload[0] == 112
    assert packets[0].payload[1] == 0
    assert packets[0].payload[2] == 1
    assert packets[0].payload[3:5] == bytes([0, 10])
    assert packets[0].payload[7:13] == bytes([4, 75, 105, 99, 107, 0])


def test_build_routine_download_packets_compiles_and_packages_kick() -> None:
    packets = build_routine_download_packets(KICK)

    assert len(packets) == 1
    assert packets[0].payload[0] == 112
    assert packets[0].payload[3:5] == bytes([1, 44])
    assert packets[0].payload[7:13] == bytes([4, 75, 105, 99, 107, 0])
