"""Personal Python SDK for Aelos robot control."""

from .robot import AelosRobot
from .types import SerialPortInfo

__all__ = ["AelosRobot", "SerialPortInfo"]
