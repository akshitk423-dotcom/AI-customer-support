"""
All Pydantic models for ResolveAI live here.

- ComplaintRequest  -> what the frontend/API caller sends in
- AnalysisResult    -> what we expect (and validate) back from the LLM
- ComplaintRecord   -> what actually gets saved to data/complaints.csv
                       (request fields + analysis fields + metadata)
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class ComplaintRequest(BaseModel):
    """Incoming payload for POST /analyze."""

    customer_name: str = Field(..., min_length=1, description="Customer's full name")
    email: EmailStr = Field(..., description="Customer's email address")
    complaint: str = Field(..., min_length=1, description="The complaint text")

    @field_validator("customer_name", "complaint")
    @classmethod
    def not_just_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be empty or just whitespace.")
        return value.strip()


class AnalysisResult(BaseModel):
    """The structured result we require the LLM's output to match.

    Pydantic validates this for us: if the LLM returns a malformed field
    (e.g. urgency = "urgent" instead of "High"), this raises a ValidationError
    that analyzer.py turns into a clear, catchable error.
    """

    category: str = Field(..., min_length=1)
    urgency: Literal["Low", "Medium", "High"]
    summary: str = Field(..., min_length=1)
    department: str = Field(..., min_length=1)
    suggested_action: str = Field(..., min_length=1)
    customer_reply: str = Field(..., min_length=1)


class ComplaintRecord(BaseModel):
    """A full row as stored in data/complaints.csv and returned by the API."""

    id: str
    timestamp: datetime
    customer_name: str
    email: str
    complaint: str
    category: str
    urgency: Literal["Low", "Medium", "High"]
    summary: str
    department: str
    suggested_action: str
    customer_reply: str
