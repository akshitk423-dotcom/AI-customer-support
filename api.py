"""
FastAPI backend for ResolveAI.

Run it from the ResolveAI/ project root with:
    uvicorn backend.api:app --reload

Endpoints:
    GET  /health   -> simple liveness check
    POST /analyze  -> accepts {customer_name, email, complaint}, returns the
                       full analyzed + saved ComplaintRecord
"""

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from ai.analyzer import (
    InvalidAIResponseError,
    LLMRequestError,
    MissingAPIKeyError,
)
from backend.models import ComplaintRecord, ComplaintRequest
from backend.processor import process_complaint

app = FastAPI(
    title="ResolveAI",
    description="AI-powered customer support complaint analyzer",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict:
    """Basic liveness check — confirms the API is up and reachable."""
    return {"status": "ok"}


@app.post("/analyze", response_model=ComplaintRecord)
def analyze(request: ComplaintRequest) -> ComplaintRecord:
    """Analyzes a customer complaint and returns the structured result.

    FastAPI + Pydantic already reject malformed requests (missing fields,
    invalid email, empty complaint) with a 422 before this function even
    runs. The try/except below handles everything that can go wrong once
    we call the LLM.
    """
    try:
        return process_complaint(request)

    except MissingAPIKeyError as exc:
        # 500 because this is a server misconfiguration, not the caller's fault
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    except LLMRequestError as exc:
        # 502 = "we tried to reach an upstream service and it failed"
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    except InvalidAIResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
