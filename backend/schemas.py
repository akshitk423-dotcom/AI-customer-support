from pydantic import BaseModel
from typing import Literal

# This defines what a valid INCOMING request must look like.
# The frontend must send JSON matching this shape.
class ComplaintRequest(BaseModel):
    complaint_text: str          # the raw complaint from the customer
    customer_name: str = "Anonymous"   # optional, defaults if not provided

# This defines what our OUTGOING response will look like.
# FastAPI will auto-convert this into JSON for the frontend.
class ComplaintResponse(BaseModel):
    category: str
    urgency: Literal["Low", "Medium", "High"]
    summary: str
    department: str
    reply: str
