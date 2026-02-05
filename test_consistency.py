import asyncio
import json
import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "src", "market-analyst", "backend")
sys.path.append(backend_dir)
sys.path.append(os.path.dirname(backend_dir)) # for 'common' if needed

from common.utility.autogen_model_factory import AutoGenModelFactory
from teams.team import get_trading_team, extract_json

async def run_analysis(ticker: str, provider: str = "openai") -> Dict[str, Any]:
    print(f"\n[INFO] Starting Analysis for {ticker.upper()} using {provider}...")
    
    # Model Setup
    if provider == "openai":
        model_name = "gpt-4o"
        family = "gpt"
        info = {"family": family, "vision": False, "function_calling": True, "json_output": True, "structured_output": True}
    elif provider == "google":
        model_name = "gemini-pro-latest"
        family = "gemini"
        info = None
    else: # groq
        model_name = "llama-3.3-70b-versatile"
        family = "groq"
        info = None

    client = AutoGenModelFactory.get_model(
        provider=provider,
        model_name=model_name,
        temperature=0,
        model_info=info
    )
    
    team = get_trading_team(client)
    
    # Run team analysis
    results = []
    async for message in team.run_stream(task=f"Analyze {ticker} and provide a trading strategy."):
        if hasattr(message, 'source') and message.source == "RiskManager":
             print(f"\n[DEBUG] Raw RiskManager output from {provider}:")
             print(message.content)
             results.append(message.content)
    
    # Extract final result
    if results:
        final_content = results[-1]
        structured = extract_json(final_content)
        return structured
    return {}

async def run_suite(ticker: str):
    print(f"\n{'='*60}")
    print(f"COMPREHENSIVE CONSISTENCY TEST FOR {ticker.upper()}")
    print(f"{'='*60}")
    
    gpt_results = []
    for i in range(3):
        print(f"\n[Run {i+1}] Testing GPT-4o...")
        r = await run_analysis(ticker, "openai")
        gpt_results.append(r)
    
    print(f"\n[Run 4] Testing Gemini Pro...")
    gemini_result = await run_analysis(ticker, "google")
    
    print(f"\n{'='*30}")
    print(f"SUMMARY REPORT ({ticker.upper()})")
    print(f"{'='*30}")
    
    for idx, r in enumerate(gpt_results):
        print(f"GPT Run {idx+1}: {r.get('final_decision')} (Score: {r.get('confidence')})")
    
    print(f"Gemini Run: {gemini_result.get('final_decision')} (Score: {gemini_result.get('confidence')})")
    
    # Consistency Checks
    gpt_decisions = [r.get('final_decision') for r in gpt_results]
    gpt_consistent = len(set(gpt_decisions)) == 1
    cross_match = gemini_result.get('final_decision') == gpt_decisions[0]
    
    print(f"\nGPT Internal Consistency: {'PASS' if gpt_consistent else 'FAIL'}")
    print(f"GPT-Gemini Alignment: {'PASS' if cross_match else 'FAIL'}")

if __name__ == "__main__":
    asyncio.run(run_suite("MSFT"))
