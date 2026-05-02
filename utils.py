"""
utils.py  —  Shared constants, request type config, and formatting helpers
"""

from datetime import datetime

# ── Request types ──────────────────────────────────────────────────────────

REQUEST_TYPES = [
    "Shift Swap",
    "Schedule Change",
    "New Report Request",
    "Agent Performance Issue",
    "IT/System Issue",
    "Other",
]

PRIORITIES = ["High", "Medium", "Low"]
STATUSES   = ["Open", "In Progress", "Closed"]
TEAMS      = ["Operations", "Quality", "Training", "HR", "IT", "MIS"]

REPORT_FORMATS = ["Excel", "Sheets", "PDF", "Dashboard"]

# ── Dynamic field definitions per request type ─────────────────────────────
# Each field: { "id": str, "label": str, "type": "text"|"date"|"number"|"select", "options": [...] }

DYNAMIC_FIELDS: dict[str, list[dict]] = {
    "Shift Swap": [
        {"id": "agentName",        "label": "Agent Name",         "type": "text"},
        {"id": "swapWith",         "label": "Swap With (Agent)",   "type": "text"},
        {"id": "originalShiftDate","label": "Original Shift Date", "type": "date"},
        {"id": "newShiftDate",     "label": "New Shift Date",      "type": "date"},
    ],
    "Schedule Change": [
        {"id": "agentName",    "label": "Agent Name",    "type": "text"},
        {"id": "effectiveDate","label": "Effective Date", "type": "date"},
        {"id": "reason",       "label": "Reason",         "type": "text"},
    ],
    "New Report Request": [
        {"id": "reportFormat",    "label": "Report Format",          "type": "select", "options": REPORT_FORMATS},
        {"id": "requiredByDate",  "label": "Required By Date",        "type": "date"},
        {"id": "dataSourceMetrics","label": "Data Source & Metrics",  "type": "text"},
    ],
    "Agent Performance Issue": [
        {"id": "agentName",   "label": "Agent Name",  "type": "text"},
        {"id": "agentId",     "label": "Agent ID",     "type": "text"},
        {"id": "incidentDate","label": "Incident Date","type": "date"},
    ],
    "IT/System Issue": [
        {"id": "systemAffected","label": "System / Tool Affected",   "type": "text"},
        {"id": "usersAffected", "label": "Number of Users Affected", "type": "number"},
    ],
    "Other": [],
}

# ── Formatting helpers ─────────────────────────────────────────────────────

STATUS_COLORS = {
    "Open":        "🔵",
    "In Progress": "🟡",
    "Closed":      "🟢",
}

PRIORITY_COLORS = {
    "High":   "🔴",
    "Medium": "🟠",
    "Low":    "⚪",
}


def fmt_date(iso: str) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%d %b %Y, %H:%M")
    except Exception:
        return iso


def status_label(s: str) -> str:
    return f"{STATUS_COLORS.get(s, '')} {s}"


def priority_label(p: str) -> str:
    return f"{PRIORITY_COLORS.get(p, '')} {p}"
