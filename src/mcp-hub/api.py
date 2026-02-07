
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

KNOWN_SERVERS = [
    {"id": "mcp-trader", "name": "MCP Trader", "description": "Quantitative trading strategies and market data analysis."},
    {"id": "mcp-web", "name": "MCP Web", "description": "Web search, content extraction, and research tools."},
    {"id": "mcp-azure-sre", "name": "MCP Azure SRE", "description": "Infrastructure management and monitoring for Azure."},
    {"id": "mcp-rag-secure", "name": "MCP Secure RAG", "description": "Multi-tenant knowledge base with strict isolation."},
    {"id": "mcp-trading-research", "name": "MCP Trading Research", "description": "Qualitative financial research and sentiment analysis."},
    {"id": "mcp-github", "name": "MCP GitHub", "description": "GitHub repository management and automation."},
    {"id": "mcp-seo", "name": "MCP SEO", "description": "Website auditing for SEO and accessibility."}
]

@app.get("/api/servers")
async def list_servers():
    """Dynamically discovers and returns MCP servers with real metrics."""
    mcp_dirs = []
    if (PROJECT_ROOT / "src").exists():
        mcp_dirs = [d for d in (PROJECT_ROOT / "src").iterdir() if d.is_dir() and d.name.startswith("mcp-") and d.name != "mcp-hub"]
    
    metrics = get_metrics()
    servers = []
    
    # Use known servers as the base if discovery yields nothing (common in Docker)
    if not mcp_dirs:
        for s in KNOWN_SERVERS:
            server_metrics = metrics.get(s["id"], {"hourly": 0, "weekly": 0, "monthly": 0})
            def fmt(n):
                if n >= 1000: return f"{n/1000:.1f}k"
                return str(n)
            
            servers.append({**s, "metrics": {
                "hourly": fmt(server_metrics["hourly"]),
                "weekly": fmt(server_metrics["weekly"]),
                "monthly": fmt(server_metrics["monthly"])
            }})
        return servers

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
