from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SerialPortInfo:
    """Serializable view of a serial port candidate."""

    device: str
    name: str | None = None
    description: str | None = None
    hwid: str | None = None
    manufacturer: str | None = None
    product: str | None = None
    serial_number: str | None = None
    vid: int | None = None
    pid: int | None = None

    @property
    def score(self) -> int:
        text = " ".join(
            value or ""
            for value in (
                self.device,
                self.name,
                self.description,
                self.hwid,
                self.manufacturer,
                self.product,
            )
        ).lower()

        score = 0
        for keyword, value in (
            ("aelos", 100),
            ("leju", 90),
            ("robot", 40),
            ("usbserial", 30),
            ("usbmodem", 30),
            ("bluetooth", 15),
            ("wchusbserial", 20),
            ("ch340", 20),
            ("cp210", 20),
        ):
            if keyword in text:
                score += value

        if self.device.startswith("/dev/cu."):
            score += 10
        return score
