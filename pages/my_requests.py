"""
pages/my_requests.py  —  Staff view of their own submitted requests
"""

import streamlit as st
import json
from auth import current_user
from database import get_all_requests
from utils import fmt_date, status_label, priority_label, STATUSES


def show():
    user = current_user()
    st.title("📋 My Requests")

    with st.spinner("Loading…"):
        df_all = get_all_requests()

    df = df_all[df_all["submittedBy"] == user["username"]].copy()
    df = df.sort_values("createdAt", ascending=False).reset_index(drop=True)

    # ── Filters ───────────────────────────────────────────────────────────
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search", placeholder="ID or subject…", label_visibility="collapsed")
    with col2:
        status_filter = st.selectbox("Status", ["All"] + STATUSES, label_visibility="collapsed")

    if search:
        mask = (
            df["id"].str.contains(search, case=False, na=False) |
            df["subject"].str.contains(search, case=False, na=False)
        )
        df = df[mask]
    if status_filter != "All":
        df = df[df["status"] == status_filter]

    st.caption(f"{len(df)} request(s)")

    if df.empty:
        st.info("No requests match your filter.")
        return

    # ── List ──────────────────────────────────────────────────────────────
    for _, row in df.iterrows():
        with st.expander(f"{status_label(row['status'])}  |  {row['id']}  —  {row['subject']}"):
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Type:** {row['type']}")
            c2.markdown(f"**Priority:** {priority_label(row['priority'])}")
            c3.markdown(f"**Submitted:** {fmt_date(row['createdAt'])}")

            st.markdown(f"**Description:**  \n{row['description']}")

            # Dynamic fields
            if row["additionalInfo"]:
                try:
                    extra = json.loads(row["additionalInfo"])
                    if extra:
                        st.markdown("**Request details:**")
                        cols = st.columns(2)
                        for i, (k, v) in enumerate(extra.items()):
                            cols[i % 2].markdown(f"- **{k}:** {v}")
                except Exception:
                    pass

            # MIS response
            if row["misNotes"]:
                st.info(f"💬 **MIS Response:** {row['misNotes']}")
                if row["assignedTo"]:
                    st.caption(f"Handled by: {row['assignedTo']}")

            if row["closedAt"]:
                st.caption(f"Closed: {fmt_date(row['closedAt'])}")
