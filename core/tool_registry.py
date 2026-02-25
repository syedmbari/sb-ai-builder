from __future__ import annotations
from typing import Callable, Any
import time

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable[..., Any]] = {}
        self._log: list[dict] = []

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        self._tools[name] = fn

    def execute(self, name: str, **kwargs) -> Any:
        if name not in self._tools:
            raise ValueError(f"Tool not registered: {name}")

        start = time.time()
        status = "OK"
        err = None

        try:
            result = self._tools[name](**kwargs)
            return result
        except Exception as e:
            status = "ERROR"
            err = repr(e)
            raise
        finally:
            elapsed_ms = int((time.time() - start) * 1000)
            # store a light log (no huge blobs)
            self._log.append({
                "tool": name,
                "status": status,
                "elapsed_ms": elapsed_ms,
                "inputs_keys": sorted(list(kwargs.keys())),
                "error": err,
            })

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def get_log(self) -> list[dict]:
        return list(self._log)

    def clear_log(self) -> None:
        self._log = []