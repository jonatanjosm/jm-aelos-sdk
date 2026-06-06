# jmaelossdk

Personal, unofficial Python SDK by Jonatan Murcia for experimenting with Aelos robot control over serial.

This project is not affiliated with, endorsed by, or maintained by Aelos, LejuRobot, or any related manufacturer. It is an independent research and experimentation SDK for personal robotics projects.

This is an early foundation. It can discover likely serial ports, open/close a connection, send raw commands, compile migrated motion routines, and build serial download packets.

## Quick start

```python
import jmaelossdk

robot = jmaelossdk.init()  # Auto-detects a likely serial port and connects

print(robot.port)

robot.close()
```

You can also provide the port explicitly:

```python
robot = jmaelossdk.init(port="/dev/cu.usbserial-110")
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
import jmaelossdk

robot = jmaelossdk.init()
robot.action("Kick")
robot.close()
```

Equivalent lower-level form:

```python
from jmaelossdk import AelosRobot, build_routine_download_packets
from jmaelossdk.routines.combat import KICK

with AelosRobot(auto_connect=True) as robot:
    for packet in build_routine_download_packets(KICK):
        robot.write_bytes(packet.payload)
```

If auto-detection chooses the wrong port, pass it explicitly:

```python
robot = jmaelossdk.init(port="/dev/cu.usbserial-110")
robot.action("Kick")
robot.close()
```

## Available routines

Routines are grouped by package under `jmaelossdk.routines`.

### Basic

- `Push-up`
  - Import: `from jmaelossdk.routines.basic import PUSH_UP, push_up`
  - Execute: `robot.action("Push-up")`

### Combat

- `Kick`
  - Import: `from jmaelossdk.routines.combat import KICK, kick`
  - Execute: `robot.action("Kick")`

### Walk

- No migrated routines yet.

## Add a routine manually

1. Choose the package for the routine.

   Use an existing group when it fits:

   - `jmaelossdk/routines/basic/`
   - `jmaelossdk/routines/combat/`
   - `jmaelossdk/routines/walk/`

   Create a new package only when the routine belongs to a new category.

2. Create one file per routine.

   Example for a basic routine:

   ```text
   jmaelossdk/routines/basic/new_routine.py
   ```

3. Define the routine as a `MotionRoutine`.

   ```python
   from __future__ import annotations

   from jmaelossdk.routine import MotionRoutine, RoutineRunner


   NEW_ROUTINE = MotionRoutine.from_commands(
       name="New_Routine",
       timing_scale=2.0,
       min_wait=0.25,
       command_interval=0.12,
       final_read_delay=1.5,
       commands=[
           "MOTOrigid16(...)",
           "MOTOsetspeed(...)",
           "MOTOmove16(...)",
           "MOTOwait()",
       ],
   )


   def new_routine(robot: RoutineRunner | None = None) -> MotionRoutine:
       if robot is not None:
           NEW_ROUTINE.run(robot)
       return NEW_ROUTINE


   __all__ = ["NEW_ROUTINE", "new_routine"]
   ```

4. Export it from the package `__init__.py`.

   Example:

   ```python
   from .new_routine import NEW_ROUTINE, new_routine

   __all__ = ["NEW_ROUTINE", "new_routine"]
   ```

5. Export it from `jmaelossdk/routines/__init__.py`.

   This makes the routine available from the top-level routines package.

6. Register it in `jmaelossdk/actions.py`.

   Import the routine and add it to `_ACTIONS`:

   ```python
   from .routines.basic import NEW_ROUTINE

   _ACTIONS: dict[str, MotionRoutine] = {
       NEW_ROUTINE.name: NEW_ROUTINE,
   }
   ```

   Once registered, it can be executed with:

   ```python
   robot.action("New_Routine")
   ```

7. Add or update tests.

   At minimum, verify:

   - the routine is a `MotionRoutine`
   - the command count
   - the `MOTOmove16` count
   - the routine is registered in `available_actions()`

8. Update this README.

   Add the routine to the package list above so the public inventory stays current.
