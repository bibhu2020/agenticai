"""Tests for Athena (deep-research-reporter) — Pydantic models and agent factories."""
import sys
import os
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# ── path setup ────────────────────────────────────────────────────────────────
_athena_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/deep-research-reporter"))
if _athena_path not in sys.path:
    sys.path.insert(0, _athena_path)

# Stub heavy external deps before importing anything from the project
for _mod in ["agents", "agents.mcp", "agents.exceptions", "agents.model_settings"]:
    sys.modules.setdefault(_mod, MagicMock())

sys.modules["agents"].Agent = MagicMock(return_value=MagicMock())
sys.modules["agents"].Runner = MagicMock()
sys.modules["agents"].function_tool = lambda f: f
sys.modules["agents"].input_guardrail = lambda f: f
sys.modules["agents"].GuardrailFunctionOutput = MagicMock()
sys.modules["agents.model_settings"].ModelSettings = MagicMock()
sys.modules["agents.mcp"].MCPServerStdio = MagicMock()
sys.modules["agents.mcp"].MCPServerStdioParams = MagicMock()
sys.modules["agents.mcp"].MCPServerManager = MagicMock()
sys.modules["agents.exceptions"].InputGuardrailTripwireTriggered = Exception

# Stub model_factory (uses API keys at import time)
_model_factory_mod = MagicMock()
_model_factory_mod.get_model = MagicMock(return_value=MagicMock())
sys.modules["model_factory"] = _model_factory_mod

import sendgrid  # may not be installed; stub it
sys.modules.setdefault("sendgrid", MagicMock())
sys.modules.setdefault("sendgrid.helpers", MagicMock())
sys.modules.setdefault("sendgrid.helpers.mail", MagicMock())

from research_agents import (
    WebSearchItem,
    WebSearchPlan,
    ReportData,
    create_planner_agent,
    create_search_agent,
    create_writer_agent,
    create_email_agent,
)


# ── WebSearchItem ─────────────────────────────────────────────────────────────

def test_web_search_item_fields():
    item = WebSearchItem(reason="understand the topic", query="AI in healthcare 2025")
    assert item.reason == "understand the topic"
    assert item.query == "AI in healthcare 2025"


def test_web_search_item_requires_both_fields():
    with pytest.raises(Exception):
        WebSearchItem(reason="only reason")


# ── WebSearchPlan ─────────────────────────────────────────────────────────────

def test_web_search_plan_empty_note_default():
    plan = WebSearchPlan(searches=[])
    assert plan.note == ""


def test_web_search_plan_with_searches():
    items = [
        WebSearchItem(reason="r1", query="q1"),
        WebSearchItem(reason="r2", query="q2"),
    ]
    plan = WebSearchPlan(searches=items)
    assert len(plan.searches) == 2
    assert plan.searches[0].query == "q1"


def test_web_search_plan_with_note():
    plan = WebSearchPlan(searches=[], note="Content blocked")
    assert plan.note == "Content blocked"


# ── ReportData ────────────────────────────────────────────────────────────────

def test_report_data_required_fields():
    rd = ReportData(
        short_summary="Brief summary.",
        markdown_report="# Report\n\nContent here.",
        follow_up_questions=["What next?", "Why?"],
    )
    assert rd.short_summary == "Brief summary."
    assert rd.markdown_report.startswith("# Report")
    assert len(rd.follow_up_questions) == 2


def test_report_data_serialisable():
    rd = ReportData(
        short_summary="s",
        markdown_report="m",
        follow_up_questions=["q"],
    )
    d = rd.model_dump()
    assert set(d.keys()) == {"short_summary", "markdown_report", "follow_up_questions"}


# ── Agent factories ───────────────────────────────────────────────────────────

def test_create_planner_agent_returns_agent():
    model = MagicMock()
    agent = create_planner_agent(model=model)
    assert agent is not None


def test_create_planner_agent_accepts_guardrail_and_mcp():
    model = MagicMock()
    guardrail = MagicMock()
    mcp = MagicMock()
    agent = create_planner_agent(model=model, guardrail=guardrail, mcp_server=mcp)
    assert agent is not None


def test_create_search_agent_returns_agent():
    model = MagicMock()
    agent = create_search_agent(model=model)
    assert agent is not None


def test_create_writer_agent_returns_agent():
    model = MagicMock()
    agent = create_writer_agent(model=model)
    assert agent is not None


def test_create_email_agent_returns_agent():
    model = MagicMock()
    agent = create_email_agent(model=model)
    assert agent is not None


def test_factories_accept_none_model():
    """Factories should fall back to _default() when model=None."""
    assert create_planner_agent(model=None) is not None
    assert create_search_agent(model=None) is not None
    assert create_writer_agent(model=None) is not None
    assert create_email_agent(model=None) is not None
