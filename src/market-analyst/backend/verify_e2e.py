import os
import sys
import asyncio
import json

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

async def main():
    ticker = "MSFT"
    provider = "openai"
    import time
    start_time = time.time()
    
    print(f"--- OPTIMIZED PERFORMANCE RUN FOR {ticker} ---", flush=True)
    
    try:
        model_client = AutoGenModelFactory.get_model(
            provider=provider,
            model_name="gpt-4o",
            temperature=0,
            model_info={"family": "gpt", "vision": False, "function_calling": True, "json_output": True, "structured_output": True}
        )
    except Exception as e:
        print(f"Model error: {e}")
        return

    # PHASE 1
    print("\n[PHASE 1: DATA COLLECTION]", flush=True)
    analyst_team = get_analyst_team(model_client)
    phase1_task = f"Perform complete analyst data collection for {ticker}."
    analyst_context = []

    try:
        async for message in analyst_team.run_stream(task=phase1_task):
            source = getattr(message, 'source', 'System')
            content = getattr(message, 'content', '')
            if not content or source == 'User': continue
            
            # Print first 200 chars of each significant report
            if len(str(content)) > 200:
                print(f"[{source}] generated a report ({len(str(content))} chars).", flush=True)
                analyst_context.append(f"[{source}]: {content}")
            else:
                # Likely a tool call result or short comment
                pass
    except Exception as e:
        print(f"Phase 1 Error: {e}")

    # PHASE 2
    print("\n[PHASE 2: STRATEGY & RISK]", flush=True)
    market_context_str = "\n\n".join(analyst_context)
    decision_team = get_decision_team(model_client)
    phase2_task = f"ANALYST CONTEXT:\n{market_context_str}\n\nGOAL: Design, critique, and finalize trade for {ticker}. Only the LeadOrchestrator can end the cycle."

    try:
        msg_count = 0
        async for message in decision_team.run_stream(task=phase2_task):
            source = getattr(message, 'source', 'System')
            content = getattr(message, 'content', '')
            if not content or (source == 'User' and "ANALYST CONTEXT" in content): continue
            
            msg_count += 1
            print(f"[{msg_count}] {source}: {str(content)[:150]}...", flush=True)
            
            if "[[ANALYSIS_JUDGMENT_COMPLETE]]" in str(content):
                print("\n--- STABLE TERMINATION DETECTED ---", flush=True)
                break
    except Exception as e:
        print(f"Phase 2 Error: {e}")

    print(f"\n--- PERFORMANCE SUMMARY ---", flush=True)
    print(f"Total Time: {time.time() - start_time:.2f}s", flush=True)
    print("--- VERIFICATION COMPLETE ---", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
