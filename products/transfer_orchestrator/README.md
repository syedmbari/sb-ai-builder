# Transfer Orchestrator

## Problem
Transfers are document-heavy and manually coordinated:
- extract key fields
- check completeness
- request missing info
- draft customer updates
- document an audit trail

## Solution
An agentic workflow orchestrator that:
- Extracts structured fields from transfer documents
- Runs deterministic validation
- Produces a structured “case review” with next steps and drafts
- Enforces a **human-only approval gate** for “Approve to Proceed”

## Human Decision Boundary
Only a human can approve proceeding with a transfer submission because it is a regulated operational action with financial and identity risk.