from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import os
import sys
from typing import AsyncGenerator

from utility.autogen_model_factory import AutoGenModelFactory
from teams.team import get_analyst_team, get_decision_team, extract_json
from tools.news_data import get_sentiment_pipeline

app = FastAPI(title="Agora API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track active analyses for cancellation
active_analyses = {}

@app.on_event("startup")
async def startup_event():
    print("Warming up FinBERT...")
    get_sentiment_pipeline()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/cancel/{analysis_id}")
async def cancel_analysis(analysis_id: str):
    if analysis_id in active_analyses:
        active_analyses[analysis_id] = True
        return {"status": "cancelled", "analysis_id": analysis_id}
    return {"status": "not_found", "analysis_id": analysis_id}

@app.get("/analyze")
async def analyze(ticker: str, provider: str = "openai"):
    import uuid
    analysis_id = str(uuid.uuid4())
    active_analyses[analysis_id] = False
    
    async def event_generator() -> AsyncGenerator[str, None]:
        if provider == "openai":
            model_name = "gpt-4o"
            family = "gpt"
        elif provider == "groq":
            model_name = "llama-3.3-70b-versatile"
            family = "groq" 
        elif provider == "google":
            model_name = "gemini-pro-latest"
            family = "gemini"
        else:
            model_name = "gpt-4o"
            family = "gpt"
        
        try:
            model_client = AutoGenModelFactory.get_model(
                provider=provider,
                model_name=model_name,
                temperature=0,
                model_info={
                    "family": family, 
                    "vision": False, 
                    "function_calling": True, 
                    "json_output": True, 
                    "structured_output": True if provider == "openai" else False
                }
            )
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Model initialization failed: {str(e)}'})}\n\n"
            return

        # PHASE 1: Analysts
        yield f"data: {json.dumps({'source': 'System', 'content': 'PHASE 1: Starting Data Collection for ' + ticker.upper(), 'analysis_id': analysis_id})}\n\n"
        analyst_team = get_analyst_team(model_client)
        phase1_task = f"Perform complete analyst data collection for {ticker.upper()}."
        analyst_context = []

        try:
            async for message in analyst_team.run_stream(task=phase1_task):
                if active_analyses.get(analysis_id, False): break
                raw_source = getattr(message, 'source', 'System')
                content = getattr(message, 'content', '')
                if not content or raw_source == 'User': continue
                analyst_context.append(f"[{raw_source}]: {content}")
                yield f"data: {json.dumps({'source': raw_source, 'content': str(content)})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'source': 'Error', 'content': f'Phase 1 bug: {str(e)}'})}\n\n"

        # PHASE 2: Decision
        yield f"data: {json.dumps({'source': 'System', 'content': 'PHASE 2: Designing Strategy...'})}\n\n"
        market_context_str = "\n\n".join(analyst_context)
        decision_team = get_decision_team(model_client)
        phase2_task = f"ANALYST CONTEXT:\n{market_context_str}\n\nGOAL: Design, critique, and finalize trade for {ticker}. Only the LeadOrchestrator can end the cycle."

        try:
            async for message in decision_team.run_stream(task=phase2_task):
                if active_analyses.get(analysis_id, False): break
                raw_source = getattr(message, 'source', 'System')
                content = getattr(message, 'content', '')
                if not content or (raw_source == 'User' and "ANALYST CONTEXT" in content): continue
                payload = {"source": raw_source, "content": str(content)}
                if raw_source in ['RiskManager', 'LeadOrchestrator']:
                    structured = extract_json(str(content))
                    if structured: payload["structured_result"] = structured
                yield f"data: {json.dumps(payload)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'source': 'Error', 'content': f'Phase 2 bug: {str(e)}'})}\n\n"

        if analysis_id in active_analyses: del active_analyses[analysis_id]
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Static mounting logic...
frontend_dist = os.path.abspath(os.path.join(current_dir, "../frontend/dist"))
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    from fastapi.responses import FileResponse
    @app.get("/{rest_of_path:path}")
    async def serve_frontend(rest_of_path: str):
        file_path = os.path.join(frontend_dist, rest_of_path)
        if os.path.isfile(file_path): return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    async def root(): return {"message": "API running. Frontend missing."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
