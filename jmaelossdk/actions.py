from __future__ import annotations

from .routine import MotionRoutine
from .routines.combat import KICK


_ACTIONS: dict[str, MotionRoutine] = {
    KICK.name: KICK,
}


def available_actions() -> tuple[str, ...]:
    return tuple(sorted(_ACTIONS))


def get_action(name: str) -> MotionRoutine:
    normalized = _normalize_name(name)
    for action_name, routine in _ACTIONS.items():
        if _normalize_name(action_name) == normalized:
            return routine
    raise ValueError(
        f"Unknown action {name!r}. Available actions: {', '.join(available_actions())}"
    )


def _normalize_name(name: str) -> str:
    return name.strip().replace("-", "_").lower()
