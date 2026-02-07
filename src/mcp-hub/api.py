
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

from fastapi.staticfiles import StaticFiles
import uvicorn

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

# Mount static files for production
static_path = Path(__file__).parent / "dist"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
