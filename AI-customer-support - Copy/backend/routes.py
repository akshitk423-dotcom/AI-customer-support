import csv
from pathlib import Path
from fastapi import APIRouter
from backend.schemas import AnalyticsResponse, ComplaintRecord, ComplaintRequest, ComplaintResponse
from backend.ai_connector import analyze_complaint

# APIRouter lets us define endpoints in this file, then "plug them in" to app.py
router = APIRouter()
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "data" / "complaints.csv"
complaints: list[ComplaintRecord] = []


def load_complaints():
    with DATA_FILE.open(newline="", encoding="utf-8") as file:
        return [ComplaintRecord(id=int(row["id"]), complaint=row["complaint"], customer_name="Customer", suggested_action="Review the case and follow the department workflow.", reply="", summary=row["complaint"], category=row["category"], urgency=row["urgency"], department=row["department"]) for row in csv.DictReader(file)]


complaints.extend(load_complaints())

@router.post("/submit-complaint", response_model=ComplaintResponse)
def submit_complaint(request: ComplaintRequest):
    # 1. request is already validated by Pydantic at this point
    # 2. pass it to the AI connector
    result = analyze_complaint(request)
    result_data = result.model_dump() if hasattr(result, "model_dump") else result.dict()
    complaints.insert(0, ComplaintRecord(id=max((item.id for item in complaints), default=0) + 1, complaint=request.complaint_text, customer_name=request.customer_name, **result_data))
    return result


@router.get("/complaints", response_model=list[ComplaintRecord])
def get_complaints():
    return complaints


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics():
    total = len(complaints)
    return AnalyticsResponse(
        total=total,
        high_priority=sum(item.urgency in ("High", "Critical") for item in complaints),
        pending=total,
        resolved=0,
        by_category=_counts(item.category for item in complaints),
        by_urgency=_counts(item.urgency for item in complaints),
        by_department=_counts(item.department for item in complaints),
    )


def _counts(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
