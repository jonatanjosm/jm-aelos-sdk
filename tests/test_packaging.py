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
    assert packets[0].index == 1
    assert packets[0].is_last is True
    assert packets[0].payload[0] == 112
    assert packets[0].payload[1] == 1
    assert packets[0].payload[2:4] == bytes([0, 1])
    assert packets[0].payload[4:6] == bytes([0, 17])
    assert packets[0].payload[8:15] == bytes([170, 170, 4, 75, 105, 99, 107])
    assert packets[0].payload[15:25] == bytes(range(10))
    assert len(packets[0].payload) == 512


def test_build_routine_download_packets_compiles_and_packages_kick() -> None:
    packets = build_routine_download_packets(KICK)

    assert len(packets) == 1
    assert packets[0].payload[0] == 112
    assert packets[0].payload[1] == 1
    assert packets[0].payload[2:4] == bytes([0, 1])
    assert packets[0].payload[4:6] == bytes([1, 51])
    assert packets[0].payload[8:15] == bytes([170, 170, 4, 75, 105, 99, 107])
