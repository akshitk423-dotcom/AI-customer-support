"""
This module is the ONLY place that talks to the LLM API.

It takes a customer name + complaint text, sends it to the model with our
prompt template, and returns a validated AnalysisResult. Any problem along
the way (missing key, network error, bad JSON, bad fields) is raised as one
of the clear exceptions below so backend/api.py can turn it into a clean
HTTP error instead of a crash.
"""

import json
import os

from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError

from ai.prompts import SYSTEM_PROMPT, build_user_prompt
from backend.models import AnalysisResult

load_dotenv()  # reads .env into environment variables, if present

MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


class MissingAPIKeyError(Exception):
    """Raised when GROQ_API_KEY is not set."""


class LLMRequestError(Exception):
    """Raised when the call to the LLM API itself fails (network, auth, etc.)."""


class InvalidAIResponseError(Exception):
    """Raised when the LLM's reply isn't valid JSON or doesn't match our schema."""


def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise MissingAPIKeyError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return Groq(api_key=api_key)


def _extract_json(raw_text: str) -> dict:
    """Best-effort extraction of a JSON object from the model's raw text output.

    Models sometimes wrap JSON in ```json ... ``` fences even when told not to,
    so we strip those before parsing.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidAIResponseError(
            f"The AI did not return valid JSON. Raw output was:\n{raw_text}"
        ) from exc


def analyze_complaint(customer_name: str, complaint: str) -> AnalysisResult:
    """Sends the complaint to the LLM and returns a validated AnalysisResult.

    Raises:
        MissingAPIKeyError: if no API key is configured.
        LLMRequestError: if the API call itself fails.
        InvalidAIResponseError: if the response isn't valid JSON or doesn't
            match the AnalysisResult schema.
    """
    client = _get_client()

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=600,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(customer_name, complaint)},
            ],
        )
    except Exception as exc:  # network errors, auth errors, rate limits, etc.
        raise LLMRequestError(f"Call to the LLM API failed: {exc}") from exc

    raw_text = response.choices[0].message.content or ""
    parsed = _extract_json(raw_text)

    try:
        return AnalysisResult(**parsed)
    except ValidationError as exc:
        raise InvalidAIResponseError(
            f"The AI's JSON did not match the expected fields: {exc}"
        ) from exc
