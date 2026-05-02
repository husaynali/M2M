"""
pages/submit.py  —  Submit a new request
"""

import streamlit as st
import json
from datetime import date
from auth import current_user
from database import submit_request, log_activity
from utils import REQUEST_TYPES, PRIORITIES, DYNAMIC_FIELDS


def show():
    user = current_user()
    st.title("✉️ Submit a Request")
    st.caption("Fill in the form — the MIS team will be notified immediately.")

    with st.form("submit_form", clear_on_submit=True):

        # ── Type & priority ───────────────────────────────────────────────
        col1, col2 = st.columns(2)
        with col1:
            req_type = st.selectbox("Request type *", REQUEST_TYPES)
        with col2:
            priority = st.selectbox("Priority *", PRIORITIES, index=1)

        subject = st.text_input("Subject *", placeholder="Brief one-line summary")

        # ── Dynamic fields ────────────────────────────────────────────────
        dynamic_values: dict = {}
        fields = DYNAMIC_FIELDS.get(req_type, [])

        if fields:
            st.markdown("**Request-specific details**")
            cols = st.columns(2)
            for i, field in enumerate(fields):
                with cols[i % 2]:
                    fid   = field["id"]
                    label = field["label"]
                    ftype = field["type"]

                    if ftype == "text":
                        dynamic_values[fid] = st.text_input(label)
                    elif ftype == "date":
                        val = st.date_input(label, value=None)
                        dynamic_values[fid] = val.isoformat() if val else ""
                    elif ftype == "number":
                        dynamic_values[fid] = str(st.number_input(label, min_value=0, step=1))
                    elif ftype == "select":
                        dynamic_values[fid] = st.selectbox(label, field["options"])

        # ── Description & notes ───────────────────────────────────────────
        description = st.text_area("Description *", placeholder="Describe your request in detail…", height=120)
        extra_notes = st.text_area("Additional notes (optional)", height=80)

        submitted = st.form_submit_button("📤 Submit Request", use_container_width=True, type="primary")

    # ── Handle submission ─────────────────────────────────────────────────
    if submitted:
        if not subject.strip() or not description.strip():
            st.error("Subject and Description are required.")
            return

        if extra_notes.strip():
            dynamic_values["additionalNotes"] = extra_notes.strip()

        req_id = submit_request(
            req_type       = req_type,
            submitted_by   = user["username"],
            team           = user["team"],
            priority       = priority,
            subject        = subject.strip(),
            description    = description.strip(),
            additional_info= json.dumps(dynamic_values),
        )
        log_activity(user["username"], "Submit", f"Submitted {req_id}: {subject.strip()}")
        st.success(f"✅ Request **{req_id}** submitted successfully! The MIS team has been notified.")
        st.balloons()
