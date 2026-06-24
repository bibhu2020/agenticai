"""Langfuse tracing integration for the OpenAI Agents SDK.

When LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY are set, installs a custom
TracingProcessor that forwards every SDK span to Langfuse, producing a clean
waterfall view: trace → agent spans → LLM generations → tool calls.

Call setup_langfuse_tracing() once at app startup.
If credentials are absent, tracing is disabled so the SDK doesn't send 401 noise
to OpenAI's tracing endpoint.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any

from agents.tracing import TracingProcessor, set_trace_processors, set_tracing_disabled

log = logging.getLogger(__name__)


def setup_langfuse_tracing() -> bool:
    """Install Langfuse as the sole tracing backend.  Returns True if installed."""
    if not (os.getenv("LANGFUSE_SECRET_KEY") and os.getenv("LANGFUSE_PUBLIC_KEY")):
        set_tracing_disabled(True)
        return False
    try:
        from langfuse import Langfuse
        lf = Langfuse()
        set_trace_processors([_LangfuseProcessor(lf)])
        log.info("Langfuse tracing → %s", os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"))
        return True
    except Exception as exc:
        log.warning("Langfuse setup failed (%s) — tracing disabled", exc)
        set_tracing_disabled(True)
        return False


class _LangfuseProcessor(TracingProcessor):
    """Maps Agents SDK spans → Langfuse observations in a waterfall hierarchy."""

    def __init__(self, lf: Any) -> None:
        self._lf = lf
        self._traces: dict[str, Any] = {}   # trace_id → langfuse trace object

    # ------------------------------------------------------------------
    # TracingProcessor interface
    # ------------------------------------------------------------------

    def on_trace_start(self, trace: Any) -> None:
        try:
            self._traces[trace.trace_id] = self._lf.trace(
                id=trace.trace_id,
                name=trace.name or "agent-run",
            )
        except Exception as exc:
            log.debug("on_trace_start: %s", exc)

    def on_trace_end(self, trace: Any) -> None:
        try:
            self._traces.pop(trace.trace_id, None)
            self._lf.flush()
        except Exception as exc:
            log.debug("on_trace_end: %s", exc)

    def on_span_start(self, span: Any) -> None:
        pass  # all data available at span_end

    def on_span_end(self, span: Any) -> None:
        try:
            lf_trace = self._traces.get(span.trace_id)
            if lf_trace is None:
                return
            # span.parent_id == the parent's span_id which we also used as the
            # Langfuse observation id, so it doubles as parent_observation_id.
            self._emit(lf_trace, span, parent_id=span.parent_id)
        except Exception as exc:
            log.debug("on_span_end: %s", exc)

    def force_flush(self) -> None:
        try:
            self._lf.flush()
        except Exception:
            pass

    def shutdown(self) -> None:
        try:
            self._lf.flush()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Span → Langfuse observation
    # ------------------------------------------------------------------

    def _emit(self, trace: Any, span: Any, parent_id: str | None) -> None:
        from agents.tracing.span_data import (
            AgentSpanData, FunctionSpanData, GenerationSpanData,
            GuardrailSpanData, HandoffSpanData, MCPListToolsSpanData,
        )

        d     = span.span_data
        err   = str(span.error) if span.error else None
        level = "ERROR" if span.error else "DEFAULT"
        start = _ts(span.started_at)
        end   = _ts(span.ended_at)
        sid   = span.span_id

        if isinstance(d, GenerationSpanData):
            usage = None
            if d.usage:
                usage = {
                    "input":  d.usage.get("input_tokens", 0),
                    "output": d.usage.get("output_tokens", 0),
                    "total":  d.usage.get("total_tokens", 0),
                }
            trace.generation(
                id=sid, parent_observation_id=parent_id,
                name=f"llm · {d.model or 'unknown'}",
                model=d.model, input=d.input, output=d.output,
                usage=usage, start_time=start, end_time=end,
                level=level, status_message=err,
            )

        elif isinstance(d, FunctionSpanData):
            prefix = "mcp" if d.mcp_data else "tool"
            trace.span(
                id=sid, parent_observation_id=parent_id,
                name=f"{prefix} · {d.name or '?'}",
                input=_parse(d.input), output=_parse(d.output),
                start_time=start, end_time=end,
                level=level, status_message=err,
            )

        elif isinstance(d, AgentSpanData):
            trace.span(
                id=sid, parent_observation_id=parent_id,
                name=f"agent · {d.name or '?'}",
                metadata={"tools": d.tools, "handoffs": d.handoffs},
                start_time=start, end_time=end, level=level,
            )

        elif isinstance(d, GuardrailSpanData):
            trace.span(
                id=sid, parent_observation_id=parent_id,
                name=f"guardrail · {d.name or '?'}",
                metadata={"triggered": d.triggered},
                start_time=start, end_time=end, level=level,
            )

        elif isinstance(d, HandoffSpanData):
            trace.span(
                id=sid, parent_observation_id=parent_id,
                name=f"handoff → {d.to_agent or '?'}",
                start_time=start, end_time=end,
            )

        elif isinstance(d, MCPListToolsSpanData):
            trace.span(
                id=sid, parent_observation_id=parent_id,
                name=f"mcp list-tools · {d.server or '?'}",
                output=d.result, start_time=start, end_time=end,
            )

        else:
            trace.span(
                id=sid, parent_observation_id=parent_id,
                name=getattr(d, "name", d.type),
                start_time=start, end_time=end,
            )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _ts(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def _parse(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        import json
        try:
            return json.loads(value)
        except Exception:
            return value
    return value
