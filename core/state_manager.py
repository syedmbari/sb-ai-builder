from __future__ import annotations
from typing import Any

class StateManager:
    def __init__(self):
        self._state: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def snapshot(self) -> dict:
        return dict(self._state)
