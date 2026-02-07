import asyncio
import sys
import random
from mcp import ClientSession
from mcp.client.sse import sse_client
from typing import Dict, Any

# Configuration
BASE_URL = "https://mishrabp-{}.hf.space/sse"
CONCURRENCY = 5  # Number of concurrent batches
ITERATIONS = 20  # Total batches (Total reqs = CONCURRENCY * ITERATIONS * 5 agents)

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

async def call_agent(name: str, tool: str, args: Dict[str, Any], batch_id: int):
    url = BASE_URL.format(name)
    try:
        # Short timeout to fail fast if agent is down
        async with sse_client(url, timeout=5) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                await session.call_tool(tool, args)
                print(f"[{batch_id}] ✅ {name}:{tool} success")
    except Exception as e:
        print(f"[{batch_id}] ❌ {name} failed: {str(e)[:50]}...")

async def run_batch(batch_id):
    targets = get_targets()
    tasks = [call_agent(t["name"], t["tool"], t["args"], batch_id) for t in targets]
    await asyncio.gather(*tasks)

async def main():
    print(f"� Starting Heavy Load Generator...")
    print(f"Plan: {ITERATIONS} iterations of {len(get_targets())} requests each.")
    
    for i in range(ITERATIONS):
        print(f"\n--- Batch {i+1}/{ITERATIONS} ---")
        await run_batch(i+1)
        # Random sleep to distribution load
        await asyncio.sleep(random.uniform(0.5, 2.0))
    
    print("\n🎉 Heavy load generation complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
