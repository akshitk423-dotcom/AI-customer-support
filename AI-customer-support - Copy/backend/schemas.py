from pydantic import BaseModel, Field
from typing import Literal

# This defines what a valid INCOMING request must look like.
# The frontend must send JSON matching this shape.
class ComplaintRequest(BaseModel):
    complaint_text: str = Field(..., min_length=3)
    customer_name: str = "Anonymous"

# This defines what our OUTGOING response will look like.
# FastAPI will auto-convert this into JSON for the frontend.
class ComplaintResponse(BaseModel):
    category: str
    urgency: Literal["Low", "Medium", "High", "Critical"]
    summary: str
    department: str
    suggested_action: str
    reply: str


class ComplaintRecord(ComplaintResponse):
    id: int
    complaint: str
    customer_name: str


class AnalyticsResponse(BaseModel):
    total: int
    high_priority: int
    pending: int
    resolved: int
    by_category: dict[str, int]
    by_urgency: dict[str, int]
    by_department: dict[str, int]
