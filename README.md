# jmaelossdk

Personal, unofficial Python SDK by Jonatan Murcia for experimenting with Aelos robot control over serial.

This project is not affiliated with, endorsed by, or maintained by Aelos, LejuRobot, or any related manufacturer. It is an independent research and experimentation SDK for personal robotics projects.

This is an early foundation. It can discover likely serial ports, open/close a connection, send raw commands, and expose a clean place to add motion routines later.

## Quick start

```python
from jmaelossdk import AelosRobot

robot = AelosRobot()  # Auto-detects a likely serial port
robot.connect()

print(robot.port)

robot.close()
```

You can also provide the port explicitly:

```python
robot = AelosRobot(port="/dev/cu.usbserial-110")
```

## List candidate ports

```python
from jmaelossdk.discovery import list_serial_ports

for port in list_serial_ports():
    print(port)
```
