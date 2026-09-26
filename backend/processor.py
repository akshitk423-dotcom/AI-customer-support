"""
Glue between the AI layer and storage.

process_complaint() is called by the API: it runs the analysis, builds a
full ComplaintRecord, appends it to data/complaints.csv, and returns it.

load_complaints() is used by both the API (not required, but handy) and
the Streamlit frontend to read all stored complaints back as a DataFrame.
"""

import os
import uuid
from datetime import datetime, timezone

import pandas as pd

from ai.analyzer import analyze_complaint
from backend.models import ComplaintRecord, ComplaintRequest

# Path is relative to the project root, so this works no matter which
# directory uvicorn/streamlit was launched from, as long as it's the
# ResolveAI/ folder itself.
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CSV_PATH = os.path.join(DATA_DIR, "complaints.csv")

CSV_COLUMNS = [
    "id", "timestamp", "customer_name", "email", "complaint",
    "category", "urgency", "summary", "department",
    "suggested_action", "customer_reply",
]


def _ensure_csv_exists() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        pd.DataFrame(columns=CSV_COLUMNS).to_csv(CSV_PATH, index=False)


def process_complaint(request: ComplaintRequest) -> ComplaintRecord:
    """Runs the AI analysis on a complaint and saves the full record to CSV."""
    analysis = analyze_complaint(request.customer_name, request.complaint)

    record = ComplaintRecord(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        customer_name=request.customer_name,
        email=request.email,
        complaint=request.complaint,
        category=analysis.category,
        urgency=analysis.urgency,
        summary=analysis.summary,
        department=analysis.department,
        suggested_action=analysis.suggested_action,
        customer_reply=analysis.customer_reply,
    )

    _save_record(record)
    return record


def _save_record(record: ComplaintRecord) -> None:
    _ensure_csv_exists()
    row = pd.DataFrame([record.model_dump()])
    row.to_csv(CSV_PATH, mode="a", header=False, index=False)


def load_complaints() -> pd.DataFrame:
    """Returns all stored complaints as a DataFrame (empty if none yet)."""
    _ensure_csv_exists()
    df = pd.read_csv(CSV_PATH)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
