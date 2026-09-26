"""
Basic tests for the ResolveAI API.

Run from the project root with:
    pytest

We mock ai.analyzer.analyze_complaint so these tests don't need a real
GROQ_API_KEY or an internet connection — they test our own code (request
validation, error handling, CSV saving), not the LLM itself.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.analyzer import InvalidAIResponseError, LLMRequestError, MissingAPIKeyError
from backend.api import app
from backend.models import AnalysisResult

client = TestClient(app)


FAKE_ANALYSIS = AnalysisResult(
    category="Billing",
    urgency="Medium",
    summary="Customer was charged twice for the same order.",
    department="Billing",
    suggested_action="Verify the duplicate charge and issue a refund.",
    customer_reply="Hi there, we're looking into the duplicate charge now.",
)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_success(monkeypatch, tmp_path):
    # Redirect CSV storage to a temp file so this test doesn't touch real data
    monkeypatch.setattr("backend.processor.CSV_PATH", str(tmp_path / "complaints.csv"))
    monkeypatch.setattr("backend.processor.analyze_complaint", lambda name, text: FAKE_ANALYSIS)

    response = client.post("/analyze", json={
        "customer_name": "Jane Doe",
        "email": "jane@example.com",
        "complaint": "I was charged twice for my order.",
    })

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Billing"
    assert body["urgency"] == "Medium"
    assert body["customer_name"] == "Jane Doe"
    assert "id" in body and "timestamp" in body


def test_analyze_rejects_empty_complaint():
    response = client.post("/analyze", json={
        "customer_name": "Jane Doe",
        "email": "jane@example.com",
        "complaint": "   ",
    })
    # Pydantic validation should reject this before it ever reaches the AI
    assert response.status_code == 422


def test_analyze_rejects_invalid_email():
    response = client.post("/analyze", json={
        "customer_name": "Jane Doe",
        "email": "not-an-email",
        "complaint": "Something is wrong with my order.",
    })
    assert response.status_code == 422


def test_analyze_missing_api_key(monkeypatch, tmp_path):
    monkeypatch.setattr("backend.processor.CSV_PATH", str(tmp_path / "complaints.csv"))

    def raise_missing_key(name, text):
        raise MissingAPIKeyError("GROQ_API_KEY is not set.")

    monkeypatch.setattr("backend.processor.analyze_complaint", raise_missing_key)

    response = client.post("/analyze", json={
        "customer_name": "Jane Doe",
        "email": "jane@example.com",
        "complaint": "Something is wrong with my order.",
    })
    assert response.status_code == 500


def test_analyze_llm_request_failure(monkeypatch, tmp_path):
    monkeypatch.setattr("backend.processor.CSV_PATH", str(tmp_path / "complaints.csv"))

    def raise_request_error(name, text):
        raise LLMRequestError("Network error talking to the LLM.")

    monkeypatch.setattr("backend.processor.analyze_complaint", raise_request_error)

    response = client.post("/analyze", json={
        "customer_name": "Jane Doe",
        "email": "jane@example.com",
        "complaint": "Something is wrong with my order.",
    })
    assert response.status_code == 502


def test_analyze_invalid_ai_response(monkeypatch, tmp_path):
    monkeypatch.setattr("backend.processor.CSV_PATH", str(tmp_path / "complaints.csv"))

    def raise_invalid_response(name, text):
        raise InvalidAIResponseError("The AI did not return valid JSON.")

    monkeypatch.setattr("backend.processor.analyze_complaint", raise_invalid_response)

    response = client.post("/analyze", json={
        "customer_name": "Jane Doe",
        "email": "jane@example.com",
        "complaint": "Something is wrong with my order.",
    })
    assert response.status_code == 502
