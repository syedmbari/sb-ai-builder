# System Design

## Objective
This repository contains AI-native operational systems that replace manual, multi-step workflows.
Each system is designed as:
- An agentic workflow orchestrator
- A bounded decision-maker
- A human-gated pipeline for regulated actions

## High-Level Components
- **UI Layer (Streamlit):** input + display only; no business logic.
- **Agent Layer:** orchestration, routing, stop conditions.
- **Tool Layer:** modular functions (extract/validate/draft/etc.).
- **State Layer:** persistence and audit logging.

## Decision Boundaries
AI may:
- Extract, classify, validate, draft, recommend, escalate

AI may NOT:
- Execute regulated actions
- Submit financial instructions
- Override compliance constraints

Human approval is mandatory at defined control points.

## Failure Handling
- Prefer deterministic checks
- Validate all model outputs against schemas
- On ambiguity or errors: escalate and preserve intermediate artifacts
