from __future__ import annotations
from core.agent_base import AgentBase

class TransferAgent(AgentBase):
    """
    Agentic orchestrator:
    - calls tools in sequence
    - routes based on validation status
    - halts at human approval boundary
    """

    def run(self, input_payload: dict) -> dict:
        document_text = input_payload["document_text"]

        fields = self.tools.execute("extract_fields", text=document_text)
        self.state.set("fields", fields)

        validation = self.tools.execute("validate_fields", fields=fields)
        self.state.set("validation", validation)

        if validation["status"] == "FAIL":
            path = "REQUEST_INFO"
        else:
            path = "READY_FOR_HUMAN_APPROVAL"

        review = self.tools.execute("generate_review", fields=fields, validation=validation)
        self.state.set("path", path)
        self.state.set("review", review)

        # explicit human gate (agent declares it)
        self.state.set("human_gate", {
            "decision": "APPROVE_TO_PROCEED",
            "required": True,
            "why": "Regulated operational action with financial/identity risk; requires human authorization."
        })

        return self.state.snapshot()