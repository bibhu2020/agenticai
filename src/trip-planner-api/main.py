import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent.agentic_workflow import create_trip_agent

app = FastAPI(title="Waypoint Trip Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "ai-trip-planner-api",
    }


@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        agent = create_trip_agent()
        response = agent.run(query.question)
        answer = response.content if hasattr(response, "content") else str(response)
        return {"answer": answer or "No response received."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
