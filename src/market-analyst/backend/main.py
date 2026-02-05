from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import os
import sys
from typing import AsyncGenerator

# Add path for common and local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if repo_root not in sys.path:
    sys.path.append(repo_root)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from common.utility.autogen_model_factory import AutoGenModelFactory
from teams.team import get_trading_team, extract_json
from tools.news_data import get_sentiment_pipeline

app = FastAPI(title="Market Analyst API")

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
    # Warm up the model in a background thread if possible, 
    # but for now let's just trigger the lazy load.
    print("Warming up FinBERT...")
    get_sentiment_pipeline()

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/cancel/{analysis_id}")
async def cancel_analysis(analysis_id: str):
    """Cancel a running analysis."""
    if analysis_id in active_analyses:
        active_analyses[analysis_id] = True  # Mark as cancelled
        return {"status": "cancelled", "analysis_id": analysis_id}
    return {"status": "not_found", "analysis_id": analysis_id}

@app.get("/analyze")
async def analyze(ticker: str, provider: str = "openai"):
    import uuid
    analysis_id = str(uuid.uuid4())
    active_analyses[analysis_id] = False  # False = not cancelled
    
    async def event_generator() -> AsyncGenerator[str, None]:
        # Guardrail: Check Trading Hours (9:30 AM - 4:00 PM ET, Mon-Fri)
        guardrail_enabled = os.getenv("MARKET_GUARDRAIL_ON", "true").lower() == "true"
        
        if guardrail_enabled:
            try:
                from datetime import datetime, time
                import pytz
                
                et_tz = pytz.timezone('US/Eastern')
                now_et = datetime.now(et_tz)
                
                # Check if weekend (Saturday=5, Sunday=6)
                is_weekend = now_et.weekday() >= 5
                
                # Check market hours (09:30 - 16:00)
                market_open = time(9, 30)
                market_close = time(16, 0)
                is_market_hours = market_open <= now_et.time() <= market_close
                
                if is_weekend or not is_market_hours:
                    msg = f"MARKET CLOSED ({now_et.strftime('%I:%M %p')} ET). Analysis requires live data. Please return Mon-Fri, 9:30 AM - 4:00 PM ET.\nSet MARKET_GUARDRAIL_ON=false to bypass."
                    yield f"data: {json.dumps({'source': 'System', 'content': msg, 'error': msg})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
            except ImportError:
                print("Warning: pytz not found, skipping market hours check.")
                pass
            except Exception as e:
                print(f"Time check error: {e}")
            
        # Setup Model
        if provider == "openai":
            model_name = "gpt-4o"
            family = "gpt"
        elif provider == "groq":
            model_name = "llama-3.3-70b-versatile"
            family = "groq" 
        elif provider == "google":
            # Using Gemini Pro for more robust reasoning and 
            # higher quality decision making across multiple agents.
            model_name = "gemini-pro-latest"
            family = "gemini"
        else:
            model_name = "gpt-4o"
            family = "gpt"
        
        try:
            temp = 0
            # For Non-OpenAI providers, let the factory handle default model_info metadata
            if provider in ["google", "groq"]:
                info = None
            else:
                info = {"family": family, "vision": False, "function_calling": True, "json_output": True, "structured_output": True}
            
            model_client = AutoGenModelFactory.get_model(
                provider=provider,
                model_name=model_name,
                temperature=temp,
                model_info=info
            )
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Model initialization failed: {str(e)}'})}\n\n"
            return

        team = get_trading_team(model_client)
        task = f"""
        Perform a professional multi-agent trade analysis for {ticker.upper()}.
        1. TechnicalAnalyst: Deep chart study, SMA trends, and RSI momentum.
        2. VolatilityAnalyst: Study IV vs HV, VIX context, and option chain liquidity.
        3. SentimentAnalyst: News sentiment (Top 5 stories) and market mood.
        4. FundamentalAnalyst: Check P/E, PEG, and balance sheet health.
        5. StrategyAdvisor: MUST call get_option_chain_snapshot to get real strikes. Use findings from all analysts to recommend an optimal option spread with SPECIFIC STRIKES AND PRICES.
        6. RiskManager: Final validation. Output JSON with "final_decision" (TRADE/WAIT), "confidence", and "actionable_recommendation".
        """
        
        # Yield initial status
        yield f"data: {json.dumps({'source': 'System', 'content': 'Starting sequential analysis for ' + ticker.upper() + '...', 'analysis_id': analysis_id})}\n\n"

        try:
            async for message in team.run_stream(task=task):
                # Check if cancelled
                if active_analyses.get(analysis_id, False):
                    yield f"data: {json.dumps({'source': 'System', 'content': 'Analysis cancelled by user.'})}\n\n"
                    yield "data: [DONE]\n\n"
                    break
                
                raw_source = getattr(message, 'source', 'System')
                content = getattr(message, 'content', '')
                
                # Handle non-string content (e.g., ToolCalls/FunctionCalls)
                if not isinstance(content, str):
                    try:
                        content = str(content)
                    except:
                        content = "[Complex Content]"
                
                if not content and not hasattr(message, 'models_usage'): 
                    continue

                # Skip echoing the huge prompt task
                if raw_source.lower() == 'user' and "Perform a professional multi-agent" in content:
                    continue

                payload = {
                    "source": raw_source,
                    "content": content
                }
                print(f"[STREAM] Sent: {raw_source} (len: {len(content)})")
                yield f"data: {json.dumps(payload)}\n\n"
        except Exception as e:
            print(f"[STREAM ERROR] {str(e)}")
            error_msg = f"Analysis execution failed: {str(e)}"
            yield f"data: {json.dumps({'source': 'Error', 'content': error_msg})}\n\n"
            
        print("[STREAM] Done.")
        # Cleanup
        if analysis_id in active_analyses:
            del active_analyses[analysis_id]
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Serve Frontend Static Files
frontend_dist = os.path.abspath(os.path.join(current_dir, "../frontend/dist"))
print(f"Checking for frontend at: {frontend_dist}")

if os.path.exists(frontend_dist):
    # Mount assets folder explicitly
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    # Serve index.html for the root and any other non-API routes
    from fastapi.responses import FileResponse
    @app.get("/{rest_of_path:path}")
    async def serve_frontend(rest_of_path: str):
        # If it's a file that exists in dist, serve it
        file_path = os.path.join(frontend_dist, rest_of_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # Otherwise serve index.html (SPA routing)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    print("WARNING: Frontend dist folder not found!")
    @app.get("/")
    async def root():
        return {"message": "Market Analyst API is running. Frontend not built.", "path": frontend_dist}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
