"""Tests for src/chatbot — content guardrail, specialist broadcast, and orchestrator."""
import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path setup — chatbot root must be first so bare-module imports resolve
# ---------------------------------------------------------------------------

_chatbot_path = str(Path(__file__).parent.parent / "src" / "nexus")
_src_path = str(Path(__file__).parent.parent / "src")

for _p in [_chatbot_path, _src_path]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Stub the agents SDK before any chatbot module is imported.
# The real package requires an API key at construction time.
# ---------------------------------------------------------------------------

_agents_mod = types.ModuleType("agents")
_agents_mod.Agent = MagicMock()
_agents_mod.OpenAIChatCompletionsModel = MagicMock()
_agents_mod.Runner = MagicMock()
_agents_mod.GuardrailFunctionOutput = MagicMock(
    side_effect=lambda output_info, tripwire_triggered: MagicMock(
        output_info=output_info, tripwire_triggered=tripwire_triggered
    )
)


def _passthrough_function_tool(fn=None, **_kwargs):
    """Let @function_tool be a no-op so the decorated functions stay callable."""
    return fn if fn is not None else (lambda f: f)


def _passthrough_input_guardrail(fn=None, **_kwargs):
    """Let @input_guardrail be a no-op so the decorated functions stay directly callable."""
    return fn if fn is not None else (lambda f: f)


_agents_mod.function_tool = _passthrough_function_tool
_agents_mod.input_guardrail = _passthrough_input_guardrail
sys.modules["agents"] = _agents_mod

# agents.mcp stub — MCPServerSse is lazy (no real connection on construction),
# but the import itself needs the submodule registered.
# Use direct assignment (not setdefault) so this overrides any real agents.mcp
# already loaded by pytest plugins before this module is collected.
_agents_mcp_mod = types.ModuleType("agents.mcp")
_agents_mcp_mod.MCPServerStdio = MagicMock()
_agents_mcp_mod.MCPServerStdioParams = MagicMock()
_agents_mcp_mod.MCPServerManager = MagicMock()
sys.modules["agents.mcp"] = _agents_mcp_mod

# ---------------------------------------------------------------------------
# Import from the new self-contained chatbot modules
# ---------------------------------------------------------------------------

from content_guardrail import (  # noqa: E402
    ContentValidationResult,
    content_policy_agent,
    enforce_content_policy,
)
from orchestrator import ai_research_orchestrator, broadcast_to_specialists  # noqa: E402

# ---------------------------------------------------------------------------
# Patch targets — test ordering can cause content_guardrail.py / orchestrator.py
# to import 'agents' before this file sets up _agents_mod (e.g. test_athena.py
# or test_agora.py run first and put a plain MagicMock in sys.modules["agents"]).
# When that happens, orchestrator.Runner / content_guardrail.Runner point to the
# OLD mock, not _agents_mod.Runner.  Patching sys.modules["agents"].Runner.run
# then has no effect on the already-bound module globals.
#
# Fix: import the modules themselves and patch Runner in *their* namespace so
# the patch always targets the object the module actually calls.
# ---------------------------------------------------------------------------
import orchestrator as _orch_mod          # noqa: E402
import content_guardrail as _cg_mod       # noqa: E402


# ===========================================================================
# ContentValidationResult (Pydantic model)
# ===========================================================================

class TestContentValidationResult:
    def test_valid_true(self):
        r = ContentValidationResult(is_valid=True, reasoning="Looks fine")
        assert r.is_valid is True
        assert r.reasoning == "Looks fine"

    def test_valid_false(self):
        r = ContentValidationResult(is_valid=False, reasoning="Contains profanity")
        assert r.is_valid is False

    def test_missing_reasoning_raises(self):
        with pytest.raises(Exception):
            ContentValidationResult(is_valid=True)

    def test_bool_coercion(self):
        r = ContentValidationResult(is_valid=1, reasoning="x")
        assert r.is_valid in (True, 1)

    def test_required_fields_present(self):
        fields = ContentValidationResult.model_fields
        assert "is_valid" in fields
        assert "reasoning" in fields


# ===========================================================================
# enforce_content_policy (guardrail function)
# ===========================================================================

class TestEnforceContentPolicy:

    def _ctx(self, context=None):
        ctx = MagicMock()
        ctx.context = context or {}
        return ctx

    @pytest.mark.asyncio
    async def test_clean_input_passes_through(self):
        valid = ContentValidationResult(is_valid=True, reasoning="All good")
        mock_result = MagicMock(final_output=valid)

        with patch.object(_cg_mod.Runner, "run", new=AsyncMock(return_value=mock_result)):
            result = await enforce_content_policy(self._ctx(), MagicMock(), "hello world")

        assert result.tripwire_triggered is False
        assert result.output_info.is_valid is True

    @pytest.mark.asyncio
    async def test_offensive_input_triggers_tripwire(self):
        invalid = ContentValidationResult(is_valid=False, reasoning="Contains profanity")
        mock_result = MagicMock(final_output=invalid)

        with patch.object(_cg_mod.Runner, "run", new=AsyncMock(return_value=mock_result)):
            result = await enforce_content_policy(self._ctx(), MagicMock(), "bad word")

        assert result.tripwire_triggered is True
        assert result.output_info.is_valid is False

    @pytest.mark.asyncio
    async def test_unexpected_output_type_triggers_tripwire(self):
        mock_result = MagicMock(final_output="not a ContentValidationResult")

        with patch.object(_cg_mod.Runner, "run", new=AsyncMock(return_value=mock_result)):
            result = await enforce_content_policy(self._ctx(), MagicMock(), "some input")

        assert result.tripwire_triggered is True
        assert "Unexpected guardrail output type" in result.output_info.reasoning

    @pytest.mark.asyncio
    async def test_context_forwarded_to_runner(self):
        valid = ContentValidationResult(is_valid=True, reasoning="ok")
        mock_result = MagicMock(final_output=valid)
        ctx = self._ctx(context={"user_id": "u42"})

        mock_run = AsyncMock(return_value=mock_result)
        with patch.object(_cg_mod.Runner, "run", new=mock_run):
            await enforce_content_policy(ctx, MagicMock(), "hello")

        _, kwargs = mock_run.call_args
        assert kwargs.get("context") == {"user_id": "u42"}

    @pytest.mark.asyncio
    async def test_content_policy_agent_is_passed_to_runner(self):
        valid = ContentValidationResult(is_valid=True, reasoning="ok")
        mock_result = MagicMock(final_output=valid)

        mock_run = AsyncMock(return_value=mock_result)
        with patch.object(_cg_mod.Runner, "run", new=mock_run):
            await enforce_content_policy(self._ctx(), MagicMock(), "test input")

        first_arg = mock_run.call_args[0][0]
        assert first_arg is content_policy_agent


# ===========================================================================
# broadcast_to_specialists (fan-out tool)
# ===========================================================================

class TestBroadcastToSpecialists:

    def _result(self, text):
        return MagicMock(final_output=text)

    @pytest.mark.asyncio
    async def test_all_three_specialists_called_by_default(self):
        mock_run = AsyncMock(side_effect=[
            self._result("finance report"),
            self._result("news report"),
            self._result("web report"),
        ])
        with patch.object(_orch_mod.Runner, "run", new=mock_run):
            output = await broadcast_to_specialists("AAPL stock")

        assert mock_run.call_count == 3
        assert "finance report" in output
        assert "news report" in output
        assert "web report" in output

    @pytest.mark.asyncio
    async def test_finance_only(self):
        mock_run = AsyncMock(return_value=self._result("finance only"))
        with patch.object(_orch_mod.Runner, "run", new=mock_run):
            output = await broadcast_to_specialists(
                "stock price", include_news=False, include_web_search=False
            )

        assert mock_run.call_count == 1
        assert "finance only" in output

    @pytest.mark.asyncio
    async def test_news_and_web_only(self):
        mock_run = AsyncMock(side_effect=[self._result("news"), self._result("web")])
        with patch.object(_orch_mod.Runner, "run", new=mock_run):
            output = await broadcast_to_specialists("latest news", include_finance=False)

        assert mock_run.call_count == 2
        assert "news" in output

    @pytest.mark.asyncio
    async def test_no_specialists_returns_message(self):
        mock_run = AsyncMock()
        with patch.object(_orch_mod.Runner, "run", new=mock_run):
            output = await broadcast_to_specialists(
                "q",
                include_finance=False,
                include_news=False,
                include_web_search=False,
            )

        mock_run.assert_not_called()
        assert "No specialist agents were selected" in output

    @pytest.mark.asyncio
    async def test_finance_failure_falls_back_to_web(self):
        # finance fails → web fallback called → output contains fallback result
        mock_run = AsyncMock(side_effect=[
            Exception("Finance API down"),  # finance
            self._result("news ok"),        # news
            self._result("web ok"),         # web (include_web_search)
            self._result("web fallback"),   # web fallback for finance
        ])
        with patch.object(_orch_mod.Runner, "run", new=mock_run):
            output = await broadcast_to_specialists("query")

        assert mock_run.call_count == 4
        assert "web fallback" in output
        assert "Fallback" in output or "fallback" in output.lower()

    @pytest.mark.asyncio
    async def test_news_failure_falls_back_to_web(self):
        # news fails → web fallback called
        mock_run = AsyncMock(side_effect=[
            self._result("finance ok"),     # finance
            Exception("NewsAPI down"),      # news
            self._result("web ok"),         # web (include_web_search)
            self._result("web fallback"),   # web fallback for news
        ])
        with patch.object(_orch_mod.Runner, "run", new=mock_run):
            output = await broadcast_to_specialists("query")

        assert mock_run.call_count == 4
        assert "web fallback" in output

    @pytest.mark.asyncio
    async def test_both_specialist_failures_fall_back_to_web(self):
        # finance and news both fail → two web fallbacks
        mock_run = AsyncMock(side_effect=[
            Exception("Finance down"),      # finance
            Exception("News down"),         # news
            self._result("web ok"),         # web (include_web_search)
            self._result("fb finance"),     # web fallback for finance
            self._result("fb news"),        # web fallback for news
        ])
        with patch.object(_orch_mod.Runner, "run", new=mock_run):
            output = await broadcast_to_specialists("query")

        assert mock_run.call_count == 5
        assert "fb finance" in output
        assert "fb news" in output

    @pytest.mark.asyncio
    async def test_web_specialist_error_not_replaced_by_fallback(self):
        # web itself fails — no further fallback (avoids infinite loop)
        mock_run = AsyncMock(side_effect=[
            self._result("finance ok"),
            self._result("news ok"),
            Exception("Web search down"),
        ])
        with patch.object(_orch_mod.Runner, "run", new=mock_run):
            output = await broadcast_to_specialists("query")

        assert mock_run.call_count == 3
        assert "Web search down" in output or "Error" in output

    @pytest.mark.asyncio
    async def test_report_boundary_markers_present(self):
        mock_run = AsyncMock(return_value=self._result("data"))
        with patch.object(_orch_mod.Runner, "run", new=mock_run):
            output = await broadcast_to_specialists("q")

        assert "SPECIALIST REPORTS BEGIN" in output
        assert "SPECIALIST REPORTS END" in output

    @pytest.mark.asyncio
    async def test_successful_specialist_marked_with_checkmark(self):
        mock_run = AsyncMock(return_value=self._result("report"))
        with patch.object(_orch_mod.Runner, "run", new=mock_run):
            output = await broadcast_to_specialists(
                "q", include_news=False, include_web_search=False
            )

        assert "✅" in output


# ===========================================================================
# ai_research_orchestrator object
# ===========================================================================

class TestAiResearchOrchestrator:
    def test_orchestrator_is_created(self):
        assert ai_research_orchestrator is not None

    def test_orchestrator_has_description(self):
        assert hasattr(ai_research_orchestrator, "description")
        assert ai_research_orchestrator.description

    def test_description_references_specialists(self):
        assert "specialist" in ai_research_orchestrator.description.lower()
