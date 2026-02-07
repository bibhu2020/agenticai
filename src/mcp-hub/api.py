
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys

# Add parent dir to path for imports
sys.path.append(str(Path(__file__).parent.parent))
try:
    from mcp_telemetry import get_metrics
except ImportError:
    # Handle direct run
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.mcp_telemetry import get_metrics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).parent.parent.parent

@app.get("/api/servers")
async def list_servers():
    """Dynamically discovers and returns MCP servers with real metrics."""
    mcp_dirs = [d for d in (PROJECT_ROOT / "src").iterdir() if d.is_dir() and d.name.startswith("mcp-") and d.name != "mcp-hub"]
    
    metrics = get_metrics()
    servers = []
    
    for d in mcp_dirs:
        readme_path = d / "README.md"
        description = "MCP Server"
        title = d.name.replace("-", " ").title()
        
        if readme_path.exists():
            content = readme_path.read_text()
            # Simple heuristic for description
            if "#" in content:
                desc_line = [line for line in content.split("\n") if line.strip() and not line.startswith(("#", "---"))]
                if desc_line:
                    description = desc_line[0]
        
        # Format metrics
        server_metrics = metrics.get(d.name, {"hourly": 0, "weekly": 0, "monthly": 0})
        
        def fmt(n):
            if n >= 1000: return f"{n/1000:.1f}k"
            return str(n)

        servers.append({
            "name": title,
            "id": d.name,
            "description": description,
            "metrics": {
                "hourly": fmt(server_metrics["hourly"]),
                "weekly": fmt(server_metrics["weekly"]),
                "monthly": fmt(server_metrics["monthly"])
            }
        })
    
    return sorted(servers, key=lambda x: x["name"])

@app.get("/api/usage")
async def get_usage_trends():
    """Returns usage data for charts (mocked for now, but from real structure)."""
    # In a real app, this would query a DB for time-series data
    # For now, we return the structure needed by the frontend
    return {
        "labels": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        "datasets": [
            {"name": "Total Activity", "data": [120, 150, 180, 160, 210, 140, 130]}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
