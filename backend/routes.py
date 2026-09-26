from fastapi import APIRouter
from backend.schemas import ComplaintRequest, ComplaintResponse
from backend.ai_connector import analyze_complaint

# APIRouter lets us define endpoints in this file, then "plug them in" to app.py
router = APIRouter()

@router.post("/submit-complaint", response_model=ComplaintResponse)
def submit_complaint(request: ComplaintRequest):
    # 1. request is already validated by Pydantic at this point
    # 2. pass it to the AI connector
    result = analyze_complaint(request)
    # 3. FastAPI automatically turns `result` into JSON for the response
    return result
