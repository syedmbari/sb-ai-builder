EXTRACT_SYSTEM = (
    "You are a careful operations analyst. Extract fields from messy transfer document text. "
    "Never invent data. If a field is missing or uncertain, use null."
)

EXTRACT_USER = """Return JSON matching this schema exactly:
{
  "client_full_name": string|null,
  "client_email": string|null,
  "client_phone": string|null,
  "sending_institution": string|null,
  "receiving_institution": string|null,
  "transfer_type": "FULL"|"PARTIAL"|"CASH"|"IN_KIND"|"UNKNOWN",
  "account_type": "TFSA"|"RRSP"|"FHSA"|"NON_REGISTERED"|"UNKNOWN",
  "account_number_last4": string|null,
  "requested_date": string|null,
  "has_signature": boolean|null
}

TEXT:
---
{document_text}
---
"""

REVIEW_SYSTEM = (
    "You are an AI operations orchestrator for a financial transfer team. "
    "Recommend next actions, draft artifacts, and highlight risks. "
    "Do NOT approve submissions; that decision is human-only."
)

REVIEW_USER = """Given:
1) Extracted fields JSON:
{fields_json}

2) Validation findings:
{validation_json}

Return JSON:
{
  "case_summary": string,
  "checklist": [string],
  "recommended_next_step": "REQUEST_INFO"|"ESCALATE"|"READY_FOR_HUMAN_APPROVAL",
  "customer_message_draft": string,
  "internal_note": string,
  "human_must_decide": {
     "decision": "APPROVE_TO_PROCEED",
     "why": string
  }
}
"""