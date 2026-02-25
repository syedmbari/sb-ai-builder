# sb-ai-builder
# This is an AI systems engineering lab

# SB AI Builder Lab  
### Agentic AI Systems for modernizing legacy (pre AI era) processes

---

## Overview

**sb-ai-builder** is a systems engineering repository dedicated to building AI-native operational products.

This repository is not a collection of chatbot experiments.  
It is a structured lab for designing, implementing, and iterating on:

- Agentic AI systems  
- Tool-using workflows  
- Model Context Protocol (MCP)-style orchestration  
- Human-in-the-loop financial controls  
- State-aware AI pipelines  
- Production-oriented architecture patterns  

Each product in this repository represents a fully scoped AI system that replaces or restructures a traditionally manual, multi-step operational process.

---

## Purpose

Modern enterprises still operate through:

- Document-heavy workflows  
- Spreadsheet reconciliation  
- Manual compliance validation  
- Ticket routing bottlenecks  
- Cross-team dependency chains  

The purpose of this lab is to:

1. Identify a legacy operational workflow  
2. Redesign it as an AI-orchestrated system  
3. Enforce strict decision boundaries  
4. Preserve regulatory and compliance controls  
5. Demonstrate scalable architecture  

This repository demonstrates how AI systems can operate as bounded decision-makers — not uncontrolled automation layers.

---

## Design Philosophy

### 1. AI as Workflow Orchestrator — Not Chat Interface

AI systems in this repo:

- Maintain execution state  
- Select and invoke tools  
- Evaluate structured outputs  
- Route execution paths  
- Escalate when appropriate  

They do not:

- Execute regulated actions autonomously  
- Override compliance controls  
- Replace human accountability  

---

### 2. Explicit Human Control Points

Every system enforces:

- Clear escalation logic  
- Bounded authority  
- Defined human approval gates  
- Audit logging  

AI may analyze and recommend.  
Humans authorize irreversible or regulated actions.

---

### 3. Tool-Based Architecture (MCP-Style Routing)

Each product uses:

- A Tool Registry  
- An Agent Layer  
- A State Manager  
- Deterministic validation components  
- LLM reasoning modules  

Agents decide *which tool to call*, not just what text to generate.

This architecture enables:

- Multi-step workflows  
- Conditional execution  
- Scalable extension  
- Reusability across products  

---

## Repository Structure
- sb-ai-builder/
- │
- ├── README.md
- ├── architecture/
- │ ├── system_design.md
- │ ├── agent_framework.md
- │
- ├── core/
- │ ├── llm_client.py
- │ ├── tool_registry.py
- │ ├── agent_base.py
- │ ├── state_manager.py
- │ ├── mcp_router.py
- │
- ├── products/
- │ ├── transfer_orchestrator/
- │ ├── reconciliation_agent/
- │ ├── (future systems)
- │
- ├── data/
- ├── requirements.txt
- ├── .env.example
- └── .gitignore


---

## Core Infrastructure Layer

The `core/` directory provides reusable AI system primitives.

### LLM Abstraction Layer
Encapsulates:
- Model selection  
- Temperature control  
- JSON enforcement  
- Structured responses  

Prevents product-level logic from coupling directly to a specific API vendor.

---

### Tool Registry
Central registry for:

- Extraction tools  
- Validation tools  
- Drafting tools  
- Escalation handlers  
- External integrations  

Tools are modular and composable.

---

### Agent Base Class
Defines:

- Decision loop  
- Execution sequencing  
- State updates  
- Stop conditions  

Products extend this base to implement domain logic.

---

### State Management
Persists:

- Workflow state  
- Execution artifacts  
- Audit logs  
- Human decisions  

Ensures traceability and replayability.

---

## Products

Each product under `products/` is a standalone AI system built on the shared core.

Examples include:

- Transfer Orchestrator (financial transfer workflow)  
- Reconciliation Automation Agent  
- KYC Risk Evaluation Agent  
- Compliance Escalation Router  

Each product contains:

- Its own README  
- Workflow logic  
- Domain-specific tools  
- Validation schemas  
- UI layer (Streamlit)  
- Database persistence  

---

## Engineering Principles

### Structured Outputs Only

All LLM calls:

- Return JSON  
- Validate against schemas  
- Fail loudly on format mismatch  

No brittle string parsing.

---

### Deterministic + Probabilistic Hybrid

Systems combine:

- Rule-based validation  
- Deterministic checks  
- LLM reasoning  
- Escalation logic  

LLMs assist reasoning — they do not replace hard constraints.

---

### Fail Safe, Not Silent

If:

- Extraction confidence is low  
- Validation fails  
- Schema mismatches occur  
- Tool invocation errors happen  

The system escalates rather than guessing.

---

### Compliance Awareness

All products:

- Explicitly define risk boundaries  
- Log human approval events  
- Separate recommendation from execution  

---

## Technology Stack

Core stack:

- Python 3.11  
- OpenAI API (JSON mode)  
- Streamlit (UI prototyping)  
- SQLite (local persistence)  
- Pydantic (schema enforcement)  
- python-dotenv (environment configuration)  

Optional expansions:

- Vector databases (for RAG)  
- Redis (workflow queues)  
- FastAPI (API deployment)  
- Cloud deployment (GCP / AWS)  

