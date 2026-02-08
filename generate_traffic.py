import asyncio
import sys
import random
import requests
import uuid
from datetime import datetime
from mcp import ClientSession
from mcp.client.sse import sse_client
from typing import Dict, Any

# Configuration
BASE_URL = "https://mishrabp-{}.hf.space/sse"
ITERATIONS = random.randint(1, 5) # Total cycles of calling all agents sequentially

STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
CITIES = ["San Francisco", "New York", "London", "Tokyo", "Paris", "Berlin", "Mumbai"]
QUERIES = ["latest AI news", "python async tutorial", "stock market trends", "weather patterns", "LLM architectures"]

def get_targets():
    """Generates a fresh set of randomized targets."""
    return [
        {
            "name": "mcp-github",
            "tool": "list_repositories",
            "args": {}
        },
        {
            "name": "mcp-weather",
            "tool": "get_current_weather",
            "args": {"location": random.choice(CITIES)}
        },
        {
            "name": "mcp-trader",
            "tool": "get_stock_price",
            "args": {"symbol": random.choice(STOCKS)}
        },
        {
            "name": "mcp-seo",
            "tool": "analyze_seo",
            "args": {"url": "https://example.com"}
        },
        {
            "name": "mcp-web",
            "tool": "search",
            "args": {"query": random.choice(QUERIES)}
        }
    ]


async def call_agent_and_emit_telemetry(name: str, tool: str, args: Dict[str, Any], batch_id: int):
    # 1. Real Tool Call (generates a Log event via Agent -> Hub)
    url = BASE_URL.format(name)
    try:
        # Check if agent is alive first (optimization)
        async with sse_client(url, timeout=5) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                start = asyncio.get_event_loop().time()
                await session.call_tool(tool, args)
                duration = (asyncio.get_event_loop().time() - start) * 1000
                print(f"[{batch_id}] ✅ {name}:{tool} success ({int(duration)}ms)")
                
                # 2. Simulate Trace/Metric emission (since Agents might be stale)
                # We send this directly to the Hub to test ingestion
                await emit_fake_telemetry(name, tool, duration)
                
    except Exception as e:
        print(f"[{batch_id}] ❌ {name} failed: {str(e)[:50]}...")

async def emit_fake_telemetry(server: str, tool: str, duration: float):
    # This simulates what the updated Agent WOULD send.
    hub_api = "https://mishrabp-mcp-hub.hf.space/api/telemetry"
    import uuid
    trace_id = str(uuid.uuid4())
    span_id = str(uuid.uuid4())
    
    # Send Trace
    try:
        trace_payload = {
            "server": server,
            "trace_id": trace_id,
            "span_id": span_id,
            "name": f"tool_call:{tool}",
            "duration_ms": duration,
            "status": "ok",
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat()
        }
        requests.post(f"{hub_api}/trace", json=trace_payload, timeout=1)
    except: pass
    
    # Send Metric
    try:
        metric_payload = {
            "server": server,
            "name": "tool_latency",
            "value": duration,
            "tags": '{"env": "prod"}',
            "timestamp": datetime.now().isoformat()
        }
        requests.post(f"{hub_api}/metric", json=metric_payload, timeout=1)
    except: pass
    
    # Send Log (Manually, in case Agent is silent)
    try:
        log_payload = {
            "server": server,
            "tool": tool,
            "timestamp": datetime.now().isoformat()
        }
        requests.post(f"{hub_api}/log", json=log_payload, timeout=1)
    except: pass

async def run_batch(batch_id):
    all_targets = get_targets()
    # Randomly pick 1 or 2 servers
    count = min(len(all_targets), random.randint(1, 2))
    targets = random.sample(all_targets, count)
    
    for i, t in enumerate(targets):
        print(f"[{batch_id}] Processing target {i+1}/{len(targets)}: {t['name']}")
        await call_agent_and_emit_telemetry(t["name"], t["tool"], t["args"], batch_id)
        # Subtle delay between individual calls to prevent flooding
        await asyncio.sleep(0.5)

async def main():
    print(f" Starting Randomized Traffic Simulator...")
    # Set to 1 iteration per call as requested
    plan_iterations = ITERATIONS
    print(f"Plan: {plan_iterations} iteration(s) (picking 1-2 random servers).")
    
    for i in range(plan_iterations):
        await run_batch(i+1)
    
    print("\n🎉 Traffic simulation complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
