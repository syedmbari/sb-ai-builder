from __future__ import annotations
from typing import Callable, Any

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        self._tools[name] = fn

    def execute(self, name: str, **kwargs) -> Any:
        if name not in self._tools:
            raise ValueError(f"Tool not registered: {name}")
        return self._tools[name](**kwargs)

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())
