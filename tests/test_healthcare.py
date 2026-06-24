"""Tests for Remedy (healthcare-rag-advisor) — ChatManager with LangGraph backend."""
import sys
import os
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# ── path setup ────────────────────────────────────────────────────────────────
_hc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/healthcare-rag-advisor"))
if _hc_path not in sys.path:
    sys.path.insert(0, _hc_path)

# Stub LangChain / LangGraph deps so no API calls happen at import time
for _mod in [
    "langchain_core", "langchain_core.messages",
    "langchain_openai",
    "langchain_community", "langchain_community.tools",
    "langgraph", "langgraph.graph", "langgraph.prebuilt",
    "rag", "tools", "tools.rag_tool",
]:
    sys.modules.setdefault(_mod, MagicMock())

# HumanMessage needs to be constructable
from unittest.mock import MagicMock as _MM
sys.modules["langchain_core.messages"].HumanMessage = _MM

from chat import ChatManager


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mgr():
    graph = MagicMock()
    return ChatManager(graph=graph)


# ── Initialisation ────────────────────────────────────────────────────────────

def test_init_empty_history(mgr):
    assert mgr.get_conversation_history() == []


def test_init_has_session_id(mgr):
    assert mgr.session_id and len(mgr.session_id) > 0


# ── add_message ───────────────────────────────────────────────────────────────

def test_add_user_message(mgr):
    mgr.add_message("user", "Hello doctor")
    h = mgr.get_conversation_history()
    assert len(h) == 1
    assert h[0]["role"] == "user"
    assert h[0]["content"] == "Hello doctor"


def test_add_assistant_message(mgr):
    mgr.add_message("assistant", "How can I help?")
    assert mgr.get_conversation_history()[0]["role"] == "assistant"


def test_add_message_includes_timestamp(mgr):
    mgr.add_message("user", "Test")
    assert "timestamp" in mgr.get_conversation_history()[0]


def test_add_message_with_metadata(mgr):
    mgr.add_message("assistant", "Done", metadata={"source": "RAG"})
    assert mgr.get_conversation_history()[0]["metadata"] == {"source": "RAG"}


def test_multiple_messages_preserve_order(mgr):
    mgr.add_message("user", "Hi")
    mgr.add_message("assistant", "Hello")
    mgr.add_message("user", "Thanks")
    h = mgr.get_conversation_history()
    assert len(h) == 3
    assert h[2]["content"] == "Thanks"


# ── clear_history ─────────────────────────────────────────────────────────────

def test_clear_removes_all_messages(mgr):
    mgr.add_message("user", "first")
    mgr.add_message("user", "second")
    mgr.clear_history()
    assert mgr.get_conversation_history() == []


def test_clear_resets_session_id(mgr):
    mgr.clear_history()
    assert mgr.session_id and len(mgr.session_id) > 0


# ── export_conversation ───────────────────────────────────────────────────────

def test_export_json_is_valid(mgr):
    mgr.add_message("user", "What is aspirin?")
    raw = mgr.export_conversation(format="json")
    data = json.loads(raw)
    assert isinstance(data, list)
    assert data[0]["content"] == "What is aspirin?"


def test_export_markdown_has_header(mgr):
    mgr.add_message("user", "Hello")
    md = mgr.export_conversation(format="markdown")
    assert "# Healthcare Chat Session" in md
    assert "Hello" in md


def test_export_text_has_session_header(mgr):
    mgr.add_message("user", "Hi")
    txt = mgr.export_conversation(format="text")
    assert "Healthcare Chat Session" in txt


def test_export_default_is_text(mgr):
    mgr.add_message("user", "Hi")
    assert "Healthcare Chat Session" in mgr.export_conversation()


# ── get_response_async (LangGraph graph.ainvoke) ──────────────────────────────

async def test_get_response_async_success(mgr):
    last_msg = MagicMock()
    last_msg.content = "Take two tablets."

    mgr.graph.ainvoke = AsyncMock(return_value={"messages": [last_msg]})

    result = await mgr.get_response_async("What is the dosage for aspirin?")

    assert result["success"] is True
    assert "Take two tablets." in result["content"]
    history = mgr.get_conversation_history()
    assert any(m["role"] == "user" for m in history)
    assert any(m["role"] == "assistant" for m in history)


async def test_get_response_async_on_error_returns_failure(mgr):
    mgr.graph.ainvoke = AsyncMock(side_effect=Exception("LLM unavailable"))
    result = await mgr.get_response_async("crash test")
    assert result["success"] is False
    assert "error" in result


async def test_get_response_async_records_user_message(mgr):
    last_msg = MagicMock()
    last_msg.content = "answer"
    mgr.graph.ainvoke = AsyncMock(return_value={"messages": [last_msg]})

    await mgr.get_response_async("my question")

    user_msgs = [m for m in mgr.get_conversation_history() if m["role"] == "user"]
    assert user_msgs[0]["content"] == "my question"
