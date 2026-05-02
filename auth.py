"""
auth.py  —  Login / session helpers
"""

import streamlit as st
from database import authenticate_user, log_activity


def login_page():
    """Render the login form. Returns True when a user successfully signs in."""

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("## 🏢 eand CX Solutions")
        st.markdown("**MIS Request Management Portal**")
        st.divider()

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g. mis.admin")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in", use_container_width=True)

        if submitted:
            user = authenticate_user(username.strip(), password.strip())
            if user:
                st.session_state.user = user
                log_activity(user["username"], "Login", f"{user['fullName']} signed in")
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.caption("Default admin: `mis.admin` / `admin123`")


def require_login():
    """Call at the top of every page. Redirects to login if not authenticated."""
    if "user" not in st.session_state or not st.session_state.user:
        login_page()
        st.stop()


def current_user() -> dict:
    return st.session_state.get("user", {})


def is_mis() -> bool:
    return current_user().get("role") == "MIS"


def logout():
    u = current_user()
    if u:
        log_activity(u["username"], "Logout", f"{u['fullName']} signed out")
    st.session_state.clear()
    st.rerun()
