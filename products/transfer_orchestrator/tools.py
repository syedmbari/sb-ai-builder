from __future__ import annotations
import json
import re
from datetime import datetime, timedelta
import pdfplumber

from core.llm_client import LLMClient
from .schemas import TransferFormFields
from .prompts import EXTRACT_SYSTEM, EXTRACT_USER, REVIEW_SYSTEM, REVIEW_USER

def extract_text_from_pdf(file_path: str) -> str:
    texts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t.strip():
                texts.append(t)
    return "\n\n".join(texts).strip()

def normalize_text(s: str) -> str:
    return " ".join(s.replace("\t", " ").split())

def extract_fields(llm: LLMClient, text: str) -> dict:
    prompt = EXTRACT_USER.format(document_text=text)
    raw = llm.chat(
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        json_mode=True,
    )
    data = json.loads(raw)
    fields = TransferFormFields(**data)  # schema validation
    return fields.model_dump()

def _is_email(s: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s.strip()))

def validate_fields(fields: dict) -> dict:
    f = TransferFormFields(**fields)
    issues = []
    warnings = []

    if not f.client_full_name:
        issues.append("Missing client full name.")
    if f.client_email and not _is_email(f.client_email):
        issues.append("Client email appears invalid format.")
    if not f.sending_institution:
        issues.append("Missing sending institution.")
    if f.transfer_type == "UNKNOWN":
        issues.append("Transfer type is unknown.")
    if f.account_type == "UNKNOWN":
        issues.append("Account type is unknown.")
    if not f.account_number_last4:
        issues.append("Missing account number last 4 digits.")
    else:
        if not re.match(r"^\d{4}$", f.account_number_last4.strip()):
            issues.append("Account number last4 must be exactly 4 digits.")

    if f.has_signature is False:
        issues.append("Missing signature.")
    if f.has_signature is None:
        warnings.append("Signature presence unclear.")

    if f.requested_date:
        try:
            dt = datetime.strptime(f.requested_date.strip(), "%Y-%m-%d")
            if dt < datetime.now() - timedelta(days=60):
                warnings.append("Requested date older than 60 days; may require re-authorization.")
        except Exception:
            warnings.append("Requested date not YYYY-MM-DD; could not validate freshness.")

    status = "PASS" if len(issues) == 0 else "FAIL"
    return {"status": status, "issues": issues, "warnings": warnings}

def generate_review(llm: LLMClient, fields: dict, validation: dict) -> dict:
    prompt = REVIEW_USER.format(
        fields_json=json.dumps(fields, indent=2),
        validation_json=json.dumps(validation, indent=2),
    )
    raw = llm.chat(
        messages=[
            {"role": "system", "content": REVIEW_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        json_mode=True,
    )
    return json.loads(raw)