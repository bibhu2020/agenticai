"""
api.py — FastAPI Backend

Responsibility:
    - Expose the agentic RAG framework as a REST API
    - POST /query  — accept a natural language query, return agent response
    - GET  /health — liveness check

The agent is initialised once at startup and reused across requests.
Run with:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from agent import get_agent
except ImportError:
    from src.salesdata.agent import get_agent

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="InsightPulse Sales Agent API",
    description="Agentic RAG over sales data powered by LlamaIndex + Gemini",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Agent (initialised once at startup) ───────────────────────────────────────
agent = None


@app.on_event("startup")
async def startup_event():
    global agent
    logger.info("Initialising agent...")
    agent = get_agent()
    logger.info("Agent ready.")


# ── Request / Response schemas ────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    query: str
    response: str
    elapsed_ms: float


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Liveness check."""
    return {"status": "ok", "agent_ready": agent is not None}


@app.post("/query", response_model=QueryResponse)
async def query_sales(request: QueryRequest):
    """
    Submit a natural language query against the sales data.

    The agent uses semantic search (VectorStoreIndex) and direct
    statistical computation (FunctionTool) to answer.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    logger.info(f"Received query: {request.query}")
    start = time.perf_counter()
    try:
        handler = agent.run(user_msg=request.query)
        response = await handler
        answer = str(response.response)
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(f"Query answered in {elapsed_ms:.1f}ms")
    return QueryResponse(query=request.query, response=answer, elapsed_ms=elapsed_ms)
