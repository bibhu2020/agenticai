
import asyncio
import sys
from pathlib import Path

# Setup paths
project_root = Path('/home/azure/agenticai')
sys.path.append(str(project_root / 'src'))
sys.path.append(str(project_root / 'src' / 'github-portal'))

from mcp_bridge import bridge

async def test():
    print("Connecting to remote MCP...")
    try:
        tools = await bridge.connect()
        print(f"Success! Tools found: {list(tools.keys())}")
        await bridge.disconnect()
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test())
