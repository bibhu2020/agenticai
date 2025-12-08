import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent.agentic_workflow import GraphBuilder
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pydantic import BaseModel
import datetime
from typing import List

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for prod
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
        "service": "ai-trip-planner-api"
    }

@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        graph_agent = GraphBuilder(model_provider="groq")

        # Collect streamed output
        streamed_response: List[str] = []

        async def capture_stream():
            async for event in graph_agent.graph.astream(
                {"messages": [query.question]},
            ):
                if "messages" in event:
                    for msg in event["messages"]:
                        streamed_response.append(msg.content)

        # Ensure the graph is built
        graph_agent.build_graph()
        await capture_stream()

        return {"answer": streamed_response[-1] if streamed_response else "No response received."}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
