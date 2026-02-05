import os
import sys
import asyncio
import json
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add path for common and local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if repo_root not in sys.path:
    sys.path.append(repo_root)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from common.utility.autogen_model_factory import AutoGenModelFactory
from teams.team import get_analyst_team, get_decision_team

async def run_analysis(ticker, provider, model_name, run_id):
    print(f"\n--- STARTING RUN {run_id} [{provider.upper()} - {model_name}] ---", flush=True)
    start_time = time.time()
    
    try:
        model_client = AutoGenModelFactory.get_model(
            provider=provider,
            model_name=model_name,
            temperature=0
        )
    except Exception as e:
        return {"error": f"Model error: {e}"}

    # PHASE 1
    print(f"[{run_id}] Phase 1: Data Collection...", end="", flush=True)
    analyst_team = get_analyst_team(model_client)
    phase1_task = f"Perform complete analyst data collection for {ticker}."
    analyst_context = []
    
    try:
        async for message in analyst_team.run_stream(task=phase1_task):
            source = getattr(message, 'source', 'System')
            content = getattr(message, 'content', '')
            if not content or source == 'User': continue
            if len(str(content)) > 200:
                analyst_context.append(f"[{source}]: {content}")
    except Exception as e:
        return {"error": f"Phase 1 Error: {e}"}
    print("Done.", flush=True)

    # PHASE 2
    print(f"[{run_id}] Phase 2: Strategy & Risk...", end="", flush=True)
    market_context_str = "\n\n".join(analyst_context)
    decision_team = get_decision_team(model_client)
    phase2_task = f"ANALYST CONTEXT:\n{market_context_str}\n\nGOAL: Design, critique, and finalize trade for {ticker}. Only the LeadOrchestrator can end the cycle."

    final_json = None
    last_message = ""
    try:
        async for message in decision_team.run_stream(task=phase2_task):
            content = getattr(message, 'content', '')
            source = getattr(message, 'source', 'System')
            if content:
                last_message = f"[{source}]: {content[:500]}"
                if "FINAL_STRATEGY:" in str(content) or "ORCHESTRATOR_DECISION: FINAL_APPROVAL" in str(content):
                    try:
                        # Search for JSON anywhere in the text
                        json_pattern = r'\{.*\}'
                        match = re.search(json_pattern, str(content), re.DOTALL)
                        if match:
                             final_json = json.loads(match.group(0))
                    except:
                        pass
    except Exception as e:
        return {"error": f"Phase 2 Error: {e}"}
    
    if not final_json:
        print(f"DEBUG: No strategy JSON found. Last message preview: {last_message}", flush=True)

    print("Done.", flush=True)
    
    elapsed = time.time() - start_time
    return {
        "provider": provider,
        "model": model_name,
        "time": round(elapsed, 2),
        "strategy": final_json.get("strategy_type", "N/A") if final_json else "N/A",
        "direction": final_json.get("direction", "N/A") if final_json else "N/A",
        "confidence": final_json.get("confidence", 0) if final_json else 0
    }

async def main():
    ticker = "META"
    print(f"=== MULTI-MODEL CONSISTENCY BENCHMARK FOR {ticker} ===")
    
    tests = [
        {"provider": "openai", "model": "gpt-4o", "label": "GPT-4o Run 1"},
        {"provider": "openai", "model": "gpt-4o", "label": "GPT-4o Run 2"},
        {"provider": "google", "model": "gemini-2.0-flash", "label": "Gemini 2.0 Flash"}
    ]
    
    results = []
    for i, test in enumerate(tests):
        res = await run_analysis(ticker, test["provider"], test["model"], i+1)
        results.append(res)
        if "error" in res:
            print(f"Error in {test['label']}: {res['error']}")
            
    print("\n" + "="*60)
    print(f"{'Run':<5} {'Model':<20} {'Time':<10} {'Strategy':<20} {'Dir':<10}")
    print("-" * 60)
    for i, res in enumerate(results):
        if "error" in res: continue
        print(f"{i+1:<5} {res['model']:<20} {res['time']:<10} {res['strategy']:<20} {res['direction']:<10}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
