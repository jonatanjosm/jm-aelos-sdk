from jmaelossdk.packaging import build_routine_download_packets, crc16_xmodem
from jmaelossdk.routines.combat import KICK


def test_crc16_xmodem_known_vector() -> None:
    assert crc16_xmodem(b"123456789") == 0x31C3


def test_build_routine_download_packets_compiles_and_packages_kick() -> None:
    packets = build_routine_download_packets(KICK)

    assert len(packets) == 1
    assert packets[0].payload[0] == 112
    assert packets[0].payload[1] == 1
    assert packets[0].payload[2:4] == bytes([0, 1])
    assert packets[0].payload[4:6] == bytes([1, 51])
    assert packets[0].payload[8:15] == bytes([170, 170, 4, 75, 105, 99, 107])
