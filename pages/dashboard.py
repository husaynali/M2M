"""
pages/dashboard.py  —  Dashboard page
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from auth import current_user, is_mis
from database import get_all_requests, get_activity_log
from utils import fmt_date, status_label, priority_label


def show():
    user = current_user()
    st.title("📊 Dashboard")

    with st.spinner("Loading data…"):
        df_all = get_all_requests()

    # Filter: staff sees only their own
    if is_mis():
        df = df_all.copy()
        st.caption("Showing all requests across all teams")
    else:
        df = df_all[df_all["submittedBy"] == user["username"]].copy()
        st.caption("Showing your submitted requests only")

    # ── Metric cards ──────────────────────────────────────────────────────
    total    = len(df)
    open_n   = len(df[df["status"] == "Open"])
    inprog_n = len(df[df["status"] == "In Progress"])
    closed_n = len(df[df["status"] == "Closed"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Requests", total)
    c2.metric("🔵 Open",        open_n)
    c3.metric("🟡 In Progress", inprog_n)
    c4.metric("🟢 Closed",      closed_n)

    st.divider()

    if df.empty:
        st.info("No requests found.")
        return

    # ── Charts ────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Requests by type")
        type_counts = df["type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]
        fig1 = px.bar(
            type_counts, x="Count", y="Type", orientation="h",
            color="Count", color_continuous_scale="Blues",
            height=320,
        )
        fig1.update_layout(showlegend=False, coloraxis_showscale=False,
                           margin=dict(l=0, r=0, t=10, b=0),
                           plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Requests by team")
        team_counts = df["team"].value_counts().reset_index()
        team_counts.columns = ["Team", "Count"]
        fig2 = px.bar(
            team_counts, x="Count", y="Team", orientation="h",
            color="Count", color_continuous_scale="Greens",
            height=320,
        )
        fig2.update_layout(showlegend=False, coloraxis_showscale=False,
                           margin=dict(l=0, r=0, t=10, b=0),
                           plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Status pie ────────────────────────────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Status breakdown")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig3 = px.pie(
            status_counts, values="Count", names="Status",
            color="Status",
            color_discrete_map={"Open": "#185FA5", "In Progress": "#BA7517", "Closed": "#3B6D11"},
            height=280,
        )
        fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Priority split")
        pri_counts = df["priority"].value_counts().reset_index()
        pri_counts.columns = ["Priority", "Count"]
        fig4 = px.pie(
            pri_counts, values="Count", names="Priority",
            color="Priority",
            color_discrete_map={"High": "#A32D2D", "Medium": "#BA7517", "Low": "#888780"},
            height=280,
        )
        fig4.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig4, use_container_width=True)

    # ── Activity log (MIS only) ───────────────────────────────────────────
    if is_mis():
        st.divider()
        st.subheader("Recent activity")
        with st.spinner("Loading log…"):
            log_df = get_activity_log(limit=20)
        if not log_df.empty:
            log_df["timestamp"] = log_df["timestamp"].apply(fmt_date)
            st.dataframe(log_df, use_container_width=True, hide_index=True)
        else:
            st.info("No activity recorded yet.")
