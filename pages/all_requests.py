"""
pages/all_requests.py  —  MIS Admin: view and manage all requests
"""

import streamlit as st
import json
from database import get_all_requests, update_request, get_all_users, log_activity
from auth import current_user
from utils import fmt_date, status_label, priority_label, REQUEST_TYPES, STATUSES, TEAMS


def show():
    st.title("🗂️ All Requests")

    with st.spinner("Loading…"):
        df = get_all_requests()
        users_df = get_all_users()

    mis_members = users_df[users_df["role"] == "MIS"]["fullName"].tolist()

    df = df.sort_values("createdAt", ascending=False).reset_index(drop=True)

    # ── Filters ───────────────────────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        search = st.text_input("🔍 Search", placeholder="ID, subject, user…", label_visibility="collapsed")
    with fc2:
        f_status = st.selectbox("Status", ["All"] + STATUSES, label_visibility="collapsed")
    with fc3:
        f_type = st.selectbox("Type", ["All types"] + REQUEST_TYPES, label_visibility="collapsed")
    with fc4:
        f_team = st.selectbox("Team", ["All teams"] + TEAMS, label_visibility="collapsed")

    filtered = df.copy()
    if search:
        mask = (
            filtered["id"].str.contains(search, case=False, na=False) |
            filtered["subject"].str.contains(search, case=False, na=False) |
            filtered["submittedBy"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]
    if f_status != "All":
        filtered = filtered[filtered["status"] == f_status]
    if f_type != "All types":
        filtered = filtered[filtered["type"] == f_type]
    if f_team != "All teams":
        filtered = filtered[filtered["team"] == f_team]

    st.caption(f"Showing {len(filtered)} of {len(df)} requests")

    if filtered.empty:
        st.info("No requests match your filters.")
        return

    # ── Table + inline update ─────────────────────────────────────────────
    for _, row in filtered.iterrows():
        header = (
            f"{status_label(row['status'])}  |  "
            f"`{row['id']}`  —  **{row['subject']}**  "
            f"[{row['team']}]"
        )
        with st.expander(header):
            col_info, col_update = st.columns([1.2, 1])

            # Left: request details
            with col_info:
                st.markdown(f"**Type:** {row['type']}  \n**Priority:** {priority_label(row['priority'])}  \n**Submitted by:** `{row['submittedBy']}`  \n**Team:** {row['team']}  \n**Created:** {fmt_date(row['createdAt'])}")
                st.markdown(f"**Description:**  \n{row['description']}")

                if row["additionalInfo"]:
                    try:
                        extra = json.loads(row["additionalInfo"])
                        if extra:
                            st.markdown("**Request details:**")
                            for k, v in extra.items():
                                st.markdown(f"- **{k}:** {v}")
                    except Exception:
                        pass

            # Right: update form
            with col_update:
                st.markdown("**Update request**")
                key_prefix = row["id"]

                new_status = st.selectbox(
                    "Status", STATUSES,
                    index=STATUSES.index(row["status"]) if row["status"] in STATUSES else 0,
                    key=f"status_{key_prefix}"
                )
                assign_opts = ["— Unassigned —"] + mis_members
                current_assign = row["assignedTo"] if row["assignedTo"] in mis_members else "— Unassigned —"
                new_assign = st.selectbox(
                    "Assign to", assign_opts,
                    index=assign_opts.index(current_assign),
                    key=f"assign_{key_prefix}"
                )
                new_notes = st.text_area(
                    "MIS Notes", value=row["misNotes"],
                    height=100, key=f"notes_{key_prefix}"
                )

                if st.button("💾 Save changes", key=f"save_{key_prefix}", type="primary"):
                    assigned = "" if new_assign == "— Unassigned —" else new_assign
                    update_request(row["id"], new_status, assigned, new_notes)
                    log_activity(
                        current_user()["username"],
                        "Update",
                        f"Updated {row['id']} → {new_status}"
                    )
                    st.success("Saved!")
                    st.rerun()

            if row["closedAt"]:
                st.caption(f"Closed at: {fmt_date(row['closedAt'])}")
