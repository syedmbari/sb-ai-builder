from __future__ import annotations
from typing import Any

class AgentBase:
    def __init__(self, llm_client, tool_registry, state_manager):
        self.llm = llm_client
        self.tools = tool_registry
        self.state = state_manager

    def run(self, input_payload: Any) -> dict:
        raise NotImplementedError("Agent must implement run()")
