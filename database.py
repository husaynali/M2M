"""
database.py  —  Google Sheets backend for eand MIS Portal
All read/write operations go through this module.
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import random
import string

# ── Google Sheets setup ────────────────────────────────────────────────────

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_USERS     = "Users"
SHEET_REQUESTS  = "Requests"
SHEET_ACTIVITY  = "ActivityLog"

USERS_HEADERS = [
    "username", "password", "fullName", "team", "status", "role"
]
REQUESTS_HEADERS = [
    "id", "type", "submittedBy", "team", "priority", "subject",
    "description", "additionalInfo", "status", "assignedTo",
    "misNotes", "createdAt", "updatedAt", "closedAt"
]
ACTIVITY_HEADERS = ["timestamp", "user", "action", "detail"]


@st.cache_resource(show_spinner=False)
def get_client():
    """Authenticate and return a gspread client (cached for the session)."""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(creds)


def get_spreadsheet():
    client = get_client()
    return client.open_by_key(st.secrets["SPREADSHEET_ID"])


def get_or_create_sheet(spreadsheet, title: str, headers: list):
    """Return a worksheet by name, creating it with headers if missing."""
    try:
        ws = spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=title, rows=1000, cols=len(headers))
        ws.append_row(headers)
    return ws


def init_sheets():
    """Ensure all required worksheets exist. Call once at app startup."""
    ss = get_spreadsheet()
    get_or_create_sheet(ss, SHEET_USERS,    USERS_HEADERS)
    get_or_create_sheet(ss, SHEET_REQUESTS, REQUESTS_HEADERS)
    get_or_create_sheet(ss, SHEET_ACTIVITY, ACTIVITY_HEADERS)

    # Seed a default MIS admin if Users sheet is empty
    ws_users = ss.worksheet(SHEET_USERS)
    rows = ws_users.get_all_records()
    if not rows:
        ws_users.append_row([
            "mis.admin", "admin123", "MIS Administrator",
            "MIS", "active", "MIS"
        ])


# ── ID generation ──────────────────────────────────────────────────────────

def generate_request_id() -> str:
    date_str = datetime.utcnow().strftime("%Y%m%d")
    suffix   = "".join(random.choices(string.digits, k=4))
    return f"REQ-{date_str}-{suffix}"


# ── Users ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def get_all_users() -> pd.DataFrame:
    ss  = get_spreadsheet()
    ws  = ss.worksheet(SHEET_USERS)
    data = ws.get_all_records()
    return pd.DataFrame(data, columns=USERS_HEADERS) if data else pd.DataFrame(columns=USERS_HEADERS)


def authenticate_user(username: str, password: str) -> dict | None:
    df = get_all_users()
    match = df[
        (df["username"] == username) &
        (df["password"] == password) &
        (df["status"]   == "active")
    ]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def add_user(username: str, password: str, full_name: str,
             team: str, role: str) -> bool:
    """Returns False if username already exists."""
    df = get_all_users()
    if username in df["username"].values:
        return False
    ss = get_spreadsheet()
    ws = ss.worksheet(SHEET_USERS)
    ws.append_row([username, password, full_name, team, "active", role])
    get_all_users.clear()
    return True


# ── Requests ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def get_all_requests() -> pd.DataFrame:
    ss   = get_spreadsheet()
    ws   = ss.worksheet(SHEET_REQUESTS)
    data = ws.get_all_records()
    return pd.DataFrame(data, columns=REQUESTS_HEADERS) if data else pd.DataFrame(columns=REQUESTS_HEADERS)


def submit_request(
    req_type: str,
    submitted_by: str,
    team: str,
    priority: str,
    subject: str,
    description: str,
    additional_info: str,   # JSON string
) -> str:
    req_id = generate_request_id()
    now    = datetime.utcnow().isoformat()
    ss     = get_spreadsheet()
    ws     = ss.worksheet(SHEET_REQUESTS)
    ws.append_row([
        req_id, req_type, submitted_by, team, priority,
        subject, description, additional_info,
        "Open", "", "", now, now, ""
    ])
    get_all_requests.clear()
    return req_id


def update_request(req_id: str, status: str, assigned_to: str, mis_notes: str):
    ss   = get_spreadsheet()
    ws   = ss.worksheet(SHEET_REQUESTS)
    data = ws.get_all_values()        # includes header row
    headers = data[0]
    now  = datetime.utcnow().isoformat()

    col = {h: i + 1 for i, h in enumerate(headers)}

    for i, row in enumerate(data[1:], start=2):
        if row[col["id"] - 1] == req_id:
            ws.update_cell(i, col["status"],     status)
            ws.update_cell(i, col["assignedTo"], assigned_to)
            ws.update_cell(i, col["misNotes"],   mis_notes)
            ws.update_cell(i, col["updatedAt"],  now)
            if status == "Closed" and not row[col["closedAt"] - 1]:
                ws.update_cell(i, col["closedAt"], now)
            elif status != "Closed":
                ws.update_cell(i, col["closedAt"], "")
            break
    get_all_requests.clear()


# ── Activity log ───────────────────────────────────────────────────────────

def log_activity(user: str, action: str, detail: str):
    ss  = get_spreadsheet()
    ws  = ss.worksheet(SHEET_ACTIVITY)
    now = datetime.utcnow().isoformat()
    ws.append_row([now, user, action, detail])


@st.cache_data(ttl=30, show_spinner=False)
def get_activity_log(limit: int = 50) -> pd.DataFrame:
    ss   = get_spreadsheet()
    ws   = ss.worksheet(SHEET_ACTIVITY)
    data = ws.get_all_records()
    df   = pd.DataFrame(data, columns=ACTIVITY_HEADERS) if data else pd.DataFrame(columns=ACTIVITY_HEADERS)
    return df.tail(limit).iloc[::-1].reset_index(drop=True)
