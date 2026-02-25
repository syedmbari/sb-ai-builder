from __future__ import annotations
import streamlit as st
import tempfile
import uuid

from core.llm_client import LLMClient
from core.tool_registry import ToolRegistry
from core.state_manager import StateManager
from core.mcp_router import MCPRouter

from .db import init_db, save_case, set_human_decision, list_cases, get_case
from .workflow import TransferAgent
from .tools import extract_text_from_pdf, normalize_text, extract_fields, validate_fields, generate_review

st.set_page_config(page_title="Transfer Orchestrator", layout="wide")
st.title("Transfer Orchestrator (Agentic Prototype)")
st.caption("AI orchestrates extraction + validation + drafting. Human approves regulated action.")

init_db()

# Sidebar - recent cases
with st.sidebar:
    st.header("Recent Cases")
    for c in list_cases():
        st.write(f"- **{c['case_id']}** ({c['source_name']})  \nPath: {c['path']}  \nDecision: {c['human_decision'] or '—'}")

# Build agent + tools
llm = LLMClient()
tools = ToolRegistry()
state = StateManager()

tools.register("extract_fields", lambda text: extract_fields(llm, text))
tools.register("validate_fields", lambda fields: validate_fields(fields))
tools.register("generate_review", lambda fields, validation: generate_review(llm, fields, validation))

agent = TransferAgent(llm, tools, state)
router = MCPRouter(agent)

st.divider()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1) Input")
    case_id = st.text_input("Case ID", value=str(uuid.uuid4())[:8])
    source_name = st.text_input("Source name", value="Transfer Form")

    uploaded = st.file_uploader("Upload PDF (text-based)", type=["pdf"])
    pasted = st.text_area("Or paste document text", height=240)

    run = st.button("Run Agent", type="primary")

with col2:
    st.subheader("2) Output")
    st.info("Run the agent to generate structured fields, validation, and drafts.")

if run:
    if not uploaded and not pasted.strip():
        st.error("Upload a PDF or paste text.")
        st.stop()

    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded.read())
            pdf_path = tmp.name
        text = extract_text_from_pdf(pdf_path)
        if not text.strip():
            st.error("Could not extract text (may be scanned). Paste text instead for now.")
            st.stop()
    else:
        text = pasted

    text = normalize_text(text)

    with st.spinner("Running agent workflow..."):
        state_out = router.route({"document_text": text})

    save_case(case_id, source_name, text, state_out)
    st.success(f"Saved case: {case_id}")

    a, b = st.columns([1, 1], gap="large")
    with a:
        st.markdown("### Extracted Fields")
        st.json(state_out.get("fields", {}), expanded=True)
        st.markdown("### Validation")
        st.json(state_out.get("validation", {}), expanded=True)

    with b:
        st.markdown("### Agent Review")
        st.json(state_out.get("review", {}), expanded=True)

        st.markdown("### Human Gate")
        st.warning("Only a human can approve proceeding with submission.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Approve to Proceed (Human Only)"):
                set_human_decision(case_id, "APPROVE_TO_PROCEED")
                st.success("Decision logged.")
        with c2:
            if st.button("Request More Info"):
                set_human_decision(case_id, "REQUEST_INFO_SENT")
                st.success("Decision logged.")

        st.markdown("### Customer Message Draft")
        st.text_area("Draft", value=state_out.get("review", {}).get("customer_message_draft", ""), height=140)

        st.markdown("### Internal Note")
        st.text_area("Note", value=state_out.get("review", {}).get("internal_note", ""), height=110)

st.divider()
st.subheader("Load existing case")
load_id = st.text_input("Enter case ID to load", value="")
if st.button("Load Case"):
    c = get_case(load_id.strip())
    if not c:
        st.error("Case not found.")
    else:
        st.write(f"**Case:** {c['case_id']}")
        st.write(f"**Source:** {c['source_name']}")
        st.write(f"**Path:** {c['path']}")
        st.write(f"**Decision:** {c['human_decision'] or '—'} at {c['human_decision_at'] or '—'}")
        st.markdown("**Fields**")
        st.code(c["fields_json"] or "{}", language="json")
        st.markdown("**Validation**")
        st.code(c["validation_json"] or "{}", language="json")
        st.markdown("**Review**")
        st.code(c["review_json"] or "{}", language="json")