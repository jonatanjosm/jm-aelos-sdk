from __future__ import annotations

from .types import SerialPortInfo


def _import_list_ports():
    try:
        from serial.tools import list_ports
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pyserial is required for serial port discovery. Install it with "
            "`python3 -m pip install pyserial` or install this package with "
            "`python3 -m pip install -e .`."
        ) from exc
    return list_ports


def list_serial_ports() -> list[SerialPortInfo]:
    """Return serial ports visible to pyserial."""

    list_ports = _import_list_ports()
    ports: list[SerialPortInfo] = []
    for port in list_ports.comports():
        ports.append(
            SerialPortInfo(
                device=port.device,
                name=port.name,
                description=port.description,
                hwid=port.hwid,
                manufacturer=port.manufacturer,
                product=port.product,
                serial_number=port.serial_number,
                vid=port.vid,
                pid=port.pid,
            )
        )
    return ports


def find_default_port() -> SerialPortInfo | None:
    """Pick the most likely Aelos serial port.

    The official app uses serial communication. The exact USB/Bluetooth name can
    vary by adapter, so this prefers likely robot/USB serial descriptors while
    keeping selection deterministic.
    """

    ports = list_serial_ports()
    if not ports:
        return None
    return sorted(ports, key=lambda item: (item.score, item.device), reverse=True)[0]
