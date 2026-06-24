"""Tests for Waypoint (trip-planner-api) FastAPI application."""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# ── path setup ────────────────────────────────────────────────────────────────
_tp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/waypoint"))
if _tp_path not in sys.path:
    sys.path.insert(0, _tp_path)

# Stub the Phidata agent module so no real LLM calls happen at import time
_mock_agent_module = MagicMock()
sys.modules["agent"] = _mock_agent_module
sys.modules["agent.agentic_workflow"] = _mock_agent_module

from main import app  # noqa: E402
from fastapi.testclient import TestClient

client = TestClient(app)


# ── Health check ──────────────────────────────────────────────────────────────

def test_health_check_returns_200():
    resp = client.get("/")
    assert resp.status_code == 200


def test_health_check_status_is_healthy():
    resp = client.get("/")
    assert resp.json()["status"] == "healthy"


def test_health_check_service_name():
    resp = client.get("/")
    assert resp.json()["service"] == "ai-trip-planner-api"


def test_health_check_has_timestamp():
    resp = client.get("/")
    assert "timestamp" in resp.json()


# ── /query endpoint ───────────────────────────────────────────────────────────

def test_query_missing_question_returns_422():
    resp = client.post("/query", json={})
    assert resp.status_code == 422


def test_query_returns_answer_key():
    """Mocked agent.run() returns a response with .content — endpoint must return 'answer'."""
    mock_response = MagicMock()
    mock_response.content = "Your Paris itinerary is ready!"
    mock_agent = MagicMock()
    mock_agent.run.return_value = mock_response

    with patch("main.create_trip_agent", return_value=mock_agent):
        resp = client.post("/query", json={"question": "Plan a trip to Paris"})

    assert resp.status_code == 200
    assert resp.json()["answer"] == "Your Paris itinerary is ready!"


def test_query_none_content_returns_fallback():
    """When response.content is falsy, endpoint returns the fallback message."""
    mock_response = MagicMock()
    mock_response.content = ""
    mock_agent = MagicMock()
    mock_agent.run.return_value = mock_response

    with patch("main.create_trip_agent", return_value=mock_agent):
        resp = client.post("/query", json={"question": "?"})

    assert resp.status_code == 200
    assert resp.json()["answer"] == "No response received."


def test_query_agent_exception_returns_500():
    """If create_trip_agent or agent.run raises, endpoint must return HTTP 500."""
    with patch("main.create_trip_agent", side_effect=Exception("LLM unavailable")):
        resp = client.post("/query", json={"question": "Plan a trip"})

    assert resp.status_code == 500
    assert "error" in resp.json()
