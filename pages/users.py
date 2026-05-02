"""
pages/users.py  —  MIS Admin: manage user accounts
"""

import streamlit as st
from database import get_all_users, add_user, log_activity
from auth import current_user
from utils import TEAMS


def show():
    st.title("👥 User Management")

    # ── Add new user ──────────────────────────────────────────────────────
    st.subheader("Add new user")
    with st.form("add_user_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Full name *")
            username  = st.text_input("Username *", placeholder="e.g. ops.ahmed")
        with c2:
            password  = st.text_input("Password *", type="password")
            team      = st.selectbox("Team *", TEAMS)

        role = st.radio("Role", ["Staff", "MIS"], horizontal=True)
        submitted = st.form_submit_button("➕ Add User", type="primary")

    if submitted:
        if not all([full_name.strip(), username.strip(), password.strip()]):
            st.error("All fields are required.")
        else:
            success = add_user(
                username   = username.strip(),
                password   = password.strip(),
                full_name  = full_name.strip(),
                team       = team,
                role       = role,
            )
            if success:
                log_activity(
                    current_user()["username"],
                    "Add User",
                    f"Created account for {username.strip()}"
                )
                st.success(f"✅ User **{full_name.strip()}** (`{username.strip()}`) added.")
            else:
                st.error(f"Username `{username.strip()}` already exists.")

    # ── User table ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("All users")

    with st.spinner("Loading users…"):
        df = get_all_users()

    if df.empty:
        st.info("No users found.")
        return

    display_df = df[["fullName", "username", "team", "role", "status"]].copy()
    display_df.columns = ["Full Name", "Username", "Team", "Role", "Status"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.caption(f"{len(df)} user account(s) total")
