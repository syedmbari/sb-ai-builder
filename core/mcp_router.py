from __future__ import annotations
from typing import Any

class MCPRouter:
    """
    Minimal MCP-style router:
    - takes a payload
    - delegates to an agent
    - returns final structured state
    """
    def __init__(self, agent):
        self.agent = agent

    def route(self, payload: Any) -> dict:
        return self.agent.run(payload)
