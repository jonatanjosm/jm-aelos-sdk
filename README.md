# jmaelossdk

Personal, unofficial Python SDK by Jonatan Murcia for experimenting with Aelos robot control over serial.

This project is not affiliated with, endorsed by, or maintained by Aelos, LejuRobot, or any related manufacturer. It is an independent research and experimentation SDK for personal robotics projects.

This is an early foundation. It can discover likely serial ports, open/close a connection, send raw commands, compile migrated motion routines, and build serial download packets.

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

## Compile the Kick routine

```python
from jmaelossdk import compile_routine
from jmaelossdk.routines.combat import KICK

compiled = compile_routine(KICK)

print(KICK.to_script())
print(len(compiled.data), "bytes")
print(compiled.data.hex(" "))
```

## Send Kick packets over serial

Experimental: this sends the compiled `Kick` routine as Aelos download packets over the serial port. The packet format is based on the Aelos Edu app, but the full robot-side handshake and final execution trigger still need validation on the physical robot.

```python
from jmaelossdk import AelosRobot, build_routine_download_packets
from jmaelossdk.routines.combat import KICK

packets = build_routine_download_packets(KICK)

with AelosRobot() as robot:
    print("Connected to", robot.port)

    for packet in packets:
        robot.write_bytes(packet.payload)
        response = robot.read_available()
        print(
            "sent packet",
            packet.index,
            "last=",
            packet.is_last,
            "response=",
            response.hex(" "),
        )
```

If auto-detection chooses the wrong port, pass it explicitly:

```python
with AelosRobot(port="/dev/cu.usbserial-110") as robot:
    for packet in build_routine_download_packets(KICK):
        robot.write_bytes(packet.payload)
```
