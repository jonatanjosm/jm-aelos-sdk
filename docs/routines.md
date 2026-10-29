# Routines

Technical notes for adding and maintaining migrated Aelos routines.

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

   For a parametrized routine, expose a factory that builds the `MotionRoutine`
   from arguments, and optionally keep a default one-step action constant:

   ```python
   def walk_forward(steps: int = 1) -> MotionRoutine:
       if steps <= 0:
           raise ValueError("steps must be greater than 0")
       return MotionRoutine.from_commands(
           name="Walk_forward" if steps == 1 else f"Walk_forward_{steps}_steps",
           commands=[INITIAL_COMMAND, *(STEP_COMMANDS * steps)],
       )


   WALK_FORWARD = walk_forward()
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

7. Run the tests.

   Run `python3 -m pytest -q`. `test_all_actions_compile` compiles every
   routine registered in `available_actions()`, so a badly migrated routine
   fails there. No per-routine test is needed; validate the movement on the
   robot instead.

8. Update the main README.

   Add the routine to the package list in `README.md` so the public inventory stays current.
