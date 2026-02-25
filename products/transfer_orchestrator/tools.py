from __future__ import annotations
import re
from typing import Any, Dict
import pdfplumber
from products.transfer_orchestrator.prompts import EXTRACT_SYSTEM, EXTRACT_USER, REVIEW_SYSTEM, REVIEW_USER


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[\d\-\s\(\)]+$")
LAST4_RE = re.compile(r"^\d{4}$")


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a text-based PDF.
    NOTE: Scanned PDFs will likely return empty text.
    """
    chunks: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t.strip():
                chunks.append(t)
    return "\n\n".join(chunks).strip()


def normalize_text(text: str) -> str:
    """
    Lightweight normalization to reduce extraction variance.
    """
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # collapse excessive whitespace while keeping line breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _looks_ocr_noisy(text: str) -> bool:
    """
    Heuristic: if the text has a suspicious amount of digit substitutions / weird punctuation,
    treat as noisy and require human verification.
    """
    if not text:
        return False

    weird_chars = "@#$%^&*_=+~<>"
    weird_ratio = sum(1 for ch in text if ch in weird_chars) / max(len(text), 1)
    digit_ratio = sum(1 for ch in text if ch.isdigit()) / max(len(text), 1)

    # Tune thresholds as needed
    return weird_ratio > 0.01 or digit_ratio > 0.12


def _name_has_unusual_chars(name: str) -> bool:
    if not name:
        return False
    return any(ch in name for ch in "@#$%^&*_=+~<>") or any(ch.isdigit() for ch in name)


def _coerce_bool(v: Any) -> Any:
    """
    Try to interpret common string values into bool; otherwise return original.
    """
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in {"y", "yes", "true", "signed", "present"}:
        return True
    if s in {"n", "no", "false", "not signed", "absent"}:
        return False
    return v

def extract_fields(llm, text: str) -> Dict[str, Any]:
    """
    Uses the LLM to extract structured fields from document text.
    Returns a dict. Includes `_raw_text` so validation can evaluate source quality.
    """
    messages = [
        {"role": "system", "content": EXTRACT_SYSTEM},
        {"role": "user", "content": EXTRACT_USER.format(document_text=text)},
    ]

    raw = llm.chat(messages, temperature=0.1, json_mode=True)

    # llm.chat(json_mode=True) should return a JSON object string.
    # We keep parsing inside this function so upstream callers always get dict.
    import json
    fields = json.loads(raw)

    # Attach raw text for validation heuristics (not for display)
    fields["_raw_text"] = text

    # Normalize/clean common fields if present
    if "client_email" in fields and fields["client_email"]:
        fields["client_email"] = str(fields["client_email"]).strip()
    if "client_phone" in fields and fields["client_phone"]:
        fields["client_phone"] = str(fields["client_phone"]).strip()
    if "account_number_last4" in fields and fields["account_number_last4"]:
        fields["account_number_last4"] = str(fields["account_number_last4"]).strip()

    if "has_signature" in fields:
        fields["has_signature"] = _coerce_bool(fields.get("has_signature"))

    return fields


def validate_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic validation: produces PASS/WARN/FAIL with human-readable reasons.
    """

    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}

    # Required fields (tune to your schema)
    required = [
        "client_full_name",
        "receiving_institution",
        "transfer_type",
        "account_type",
    ]
    missing = [k for k in required if not fields.get(k)]
    if missing:
        errors.extend([f"Missing required field: {k}" for k in missing])

    # Format checks
    email = fields.get("client_email")
    if email and not EMAIL_RE.match(str(email).strip()):
        warnings.append("Email format looks invalid.")

    phone = fields.get("client_phone")
    if phone and not PHONE_RE.match(str(phone).strip()):
        warnings.append("Phone format looks unusual (verify).")

    last4 = fields.get("account_number_last4")
    if last4 and not LAST4_RE.match(str(last4).strip()):
        warnings.append("Account last4 should be exactly 4 digits.")

    # Signature / authorization signal
    has_sig = fields.get("has_signature")
    if has_sig is False:
        errors.append("Signature explicitly missing.")
    elif has_sig is None:
        warnings.append("Signature presence uncertain (verify).")
    elif isinstance(has_sig, str):
        # If coercion didn’t convert it, it’s ambiguous
        warnings.append("Signature indicator is ambiguous (verify).")

    # OCR/noise red flags
    raw_text = fields.get("_raw_text", "")
    if _looks_ocr_noisy(raw_text):
        warnings.append("Source text appears OCR/noisy. Recommend human verification of extracted fields.")

    # Suspicious name characters
    name = str(fields.get("client_full_name") or "")
    if _name_has_unusual_chars(name):
        warnings.append("Client name contains unusual characters (OCR/noise risk).")

    # Optional: if transfer_type or account_type unknown, warn
    transfer_type = str(fields.get("transfer_type") or "").upper()
    if transfer_type in {"UNKNOWN", ""}:
        warnings.append("Transfer type is UNKNOWN or missing confidence.")

    account_type = str(fields.get("account_type") or "").upper()
    if account_type in {"UNKNOWN", ""}:
        warnings.append("Account type is UNKNOWN or missing confidence.")

    # Decide status
    if errors:
        status = "FAIL"
    elif warnings:
        status = "WARN"
    else:
        status = "PASS"

    checks["required_fields_present"] = (len(missing) == 0)
    checks["errors_count"] = len(errors)
    checks["warnings_count"] = len(warnings)

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }


def generate_review(llm, fields: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Draft agent review + customer message + internal note in JSON.
    """
    import json

    # Remove raw text from what we send back to the model (avoid bloating prompt)
    fields_for_model = {k: v for k, v in fields.items() if k != "_raw_text"}

    messages = [
        {"role": "system", "content": REVIEW_SYSTEM},
        {
            "role": "user",
            "content": REVIEW_USER.format(
                fields_json=json.dumps(fields_for_model, ensure_ascii=False),
                validation_json=json.dumps(validation, ensure_ascii=False),
            ),
        },
    ]

    raw = llm.chat(messages, temperature=0.2, json_mode=True)
    review = json.loads(raw)
    return review