from __future__ import annotations
import os
import json
import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join("data", "cases.db")

def _conn():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with _conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            created_at TEXT,
            source_name TEXT,
            document_text TEXT,
            fields_json TEXT,
            validation_json TEXT,
            review_json TEXT,
            path TEXT,
            human_decision TEXT,
            human_decision_at TEXT
        )
        """)
        con.commit()

def save_case(case_id: str, source_name: str, document_text: str, state: dict):
    with _conn() as con:
        con.execute("""
        INSERT INTO cases(case_id, created_at, source_name, document_text, fields_json, validation_json, review_json, path, human_decision, human_decision_at)
        VALUES(?,?,?,?,?,?,?,?,NULL,NULL)
        ON CONFLICT(case_id) DO UPDATE SET
            source_name=excluded.source_name,
            document_text=excluded.document_text,
            fields_json=excluded.fields_json,
            validation_json=excluded.validation_json,
            review_json=excluded.review_json,
            path=excluded.path
        """, (
            case_id,
            datetime.utcnow().isoformat(),
            source_name,
            document_text,
            json.dumps(state.get("fields", {}), indent=2),
            json.dumps(state.get("validation", {}), indent=2),
            json.dumps(state.get("review", {}), indent=2),
            state.get("path"),
        ))
        con.commit()

def set_human_decision(case_id: str, decision: str):
    with _conn() as con:
        con.execute("""
        UPDATE cases
        SET human_decision=?, human_decision_at=?
        WHERE case_id=?
        """, (decision, datetime.utcnow().isoformat(), case_id))
        con.commit()

def list_cases(limit: int = 20) -> list[dict]:
    with _conn() as con:
        cur = con.execute("""
            SELECT case_id, created_at, source_name, path, human_decision, human_decision_at
            FROM cases
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

def get_case(case_id: str) -> Optional[dict]:
    with _conn() as con:
        cur = con.execute("SELECT * FROM cases WHERE case_id=?", (case_id,))
        row = cur.fetchone()
        if not row:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))