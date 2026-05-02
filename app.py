"""
app.py  —  Entry point for the eand CX Solutions MIS Request Portal
Run:  streamlit run app.py
"""

import streamlit as st
from database import init_sheets
from auth import require_login, current_user, is_mis, logout

st.set_page_config(
    page_title="eand MIS Portal",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
  /* Sidebar branding */
  section[data-testid="stSidebar"] { background: #0f2744; }
  section[data-testid="stSidebar"] * { color: #e8f0fe !important; }
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stTextInput label { color: #a8c4f0 !important; }

  /* Metric cards */
  div[data-testid="metric-container"] {
    background: #f0f4fa;
    border: 1px solid #d0dff5;
    border-radius: 10px;
    padding: 12px 16px;
  }

  /* Hide default Streamlit menu in prod */
  #MainMenu { visibility: hidden; }
  footer    { visibility: hidden; }

  /* Wider content area */
  .block-container { padding-top: 1.5rem; max-width: 1200px; }
</style>
""", unsafe_allow_html=True)

# ── Bootstrap sheets on first run ─────────────────────────────────────────

if "sheets_ready" not in st.session_state:
    with st.spinner("Connecting to database…"):
        init_sheets()
    st.session_state.sheets_ready = True

# ── Auth gate ──────────────────────────────────────────────────────────────

require_login()
user = current_user()

# ── Sidebar ────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🏢 eand CX")
    st.markdown("**MIS Request Portal**")
    st.divider()

    st.markdown(f"👤 **{user['fullName']}**  \n`{user['team']}` · `{user['role']}`")
    st.divider()

    pages = {
        "📊 Dashboard":       "dashboard",
        "✉️ Submit Request":   "submit",
        "📋 My Requests":      "myrequests",
    }
    if is_mis():
        pages["🗂️ All Requests"] = "allrequests"
        pages["👥 Users"]         = "users"

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    for label, key in pages.items():
        if st.button(label, use_container_width=True,
                     type="primary" if st.session_state.page == key else "secondary"):
            st.session_state.page = key
            st.rerun()

    st.divider()
    if st.button("🚪 Sign out", use_container_width=True):
        logout()

# ── Page routing ───────────────────────────────────────────────────────────

page = st.session_state.get("page", "dashboard")

if page == "dashboard":
    from pages.dashboard import show
elif page == "submit":
    from pages.submit import show
elif page == "myrequests":
    from pages.my_requests import show
elif page == "allrequests" and is_mis():
    from pages.all_requests import show
elif page == "users" and is_mis():
    from pages.users import show
else:
    from pages.dashboard import show

show()
