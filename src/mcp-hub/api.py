# FORCE REDEPLOY: Telemetry Sync v2
import os
import sys
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime, timedelta

# Add parent dir to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Core Telemetry Imports for Metrics/History
from core.mcp_telemetry import get_metrics, get_usage_history, get_system_metrics, get_recent_logs, get_recent_traces, log_usage


# Telemetry Import
try:
    from core.mcp_telemetry import _write_db
except ImportError:
    # If standard import fails, try absolute path fallback
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.core.mcp_telemetry import _write_db

from pydantic import BaseModel

# Optional: HF Hub for status checks
try:
    from huggingface_hub import HfApi
    hf_api = HfApi()
except ImportError:
    hf_api = None

class LogEvent(BaseModel):
    server: str
    tool: str
    timestamp: Optional[str] = None

class TraceEvent(BaseModel):
    server: str
    trace_id: str
    span_id: str
    name: str
    duration_ms: float
    status: Optional[str] = "ok"
    parent_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class MetricEvent(BaseModel):
    server: str
    name: str
    value: float
    tags: Optional[str] = "{}"
    timestamp: Optional[str] = None

app = FastAPI()

@app.post("/api/telemetry")
@app.post("/api/telemetry/log")
async def ingest_log(event: LogEvent):
    """Ingests usage logs."""
    try:
        ts = event.timestamp or datetime.now().isoformat()
        _write_db("logs", {
            "timestamp": ts,
            "server": event.server,
            "tool": event.tool
        })
        return {"status": "ok"}
    except Exception as e:
        print(f"Log Ingest Failed: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/telemetry/trace")
async def ingest_trace(event: TraceEvent):
    """Ingests distributed traces."""
    try:
        _write_db("traces", event.dict())
        return {"status": "ok"}
    except Exception as e:
        print(f"Trace Ingest Failed: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/telemetry/metric")
async def ingest_metric(event: MetricEvent):
    """Ingests quantitative metrics."""
    try:
        ts = event.timestamp or datetime.now().isoformat()
        data = event.dict()
        data["timestamp"] = ts
        _write_db("metrics", data)
        return {"status": "ok"}
    except Exception as e:
        print(f"Metric Ingest Failed: {e}")
        return {"status": "error", "message": str(e)}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).parent.parent.parent
HF_USERNAME = os.environ.get("HF_USERNAME", "mishrabp")

KNOWN_SERVERS = [
    {"id": "mcp-trader", "name": "MCP Trader", "description": "Quantitative trading strategies and market data analysis."},
    {"id": "mcp-web", "name": "MCP Web", "description": "Web search, content extraction, and research tools."},
    {"id": "mcp-azure-sre", "name": "MCP Azure SRE", "description": "Infrastructure management and monitoring for Azure."},
    {"id": "mcp-rag-secure", "name": "MCP Secure RAG", "description": "Multi-tenant knowledge base with strict isolation."},
    {"id": "mcp-trading-research", "name": "MCP Trading Research", "description": "Qualitative financial research and sentiment analysis."},
    {"id": "mcp-github", "name": "MCP GitHub", "description": "GitHub repository management and automation."},
    {"id": "mcp-seo", "name": "MCP SEO", "description": "Website auditing for SEO and accessibility."},
    {"id": "mcp-weather", "name": "MCP Weather", "description": "Real-time weather forecast and location intelligence."}
]

async def get_hf_status(space_id: str) -> str:
    """Get status from Hugging Face Space with timeout."""
    if not hf_api:
        return "Unknown"
    try:
        # space_id is like "username/space-name"
        repo_id = f"{HF_USERNAME}/{space_id}" if "/" not in space_id else space_id
        # Use a thread pool or run_in_executor since get_space_runtime is blocking
        loop = asyncio.get_event_loop()
        runtime = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: hf_api.get_space_runtime(repo_id)),
            timeout=5.0
        )
        return runtime.stage.capitalize()
    except asyncio.TimeoutError:
        print(f"Timeout checking status for {space_id}")
        return "Timeout"
    except Exception as e:
        print(f"Error checking status for {space_id}: {e}")
        return "Offline"

@app.get("/api/servers/{server_id}")
async def get_server_detail(server_id: str):
    """Returns detailed documentation and tools for a specific server."""
    try:
        print(f"DEBUG: get_server_detail called for {server_id}")
        # Log usage for trends
        try:
            asyncio.create_task(asyncio.to_thread(log_usage, "MCP Hub", f"view_{server_id}"))
        except Exception as e:
            print(f"DEBUG: Failed to log usage: {e}")

        server_path = PROJECT_ROOT / "src" / server_id
        readme_path = server_path / "README.md"
        print(f"DEBUG: Looking for README at {readme_path}")
        
        description = "No documentation found."
        tools = []
        
        if readme_path.exists():
            content = readme_path.read_text()
            # Parse description (text between # and ## Tools)
            desc_match = content.split("## Tools")[0].split("#")
            if len(desc_match) > 1:
                description = desc_match[-1].split("---")[-1].strip()
                
            # Parse tools
            if "## Tools" in content:
                tools_section = content.split("## Tools")[1].split("##")[0]
                for line in tools_section.strip().split("\n"):
                    if line.strip().startswith("-"):
                        tools.append(line.strip("- ").strip())
        else:
            print(f"DEBUG: README not found at {readme_path}")

        # Apply strict capitalization
        name = server_id.replace("-", " ").title()
        for word in ["Mcp", "Sre", "Rag", "Seo", "mcp", "sre", "rag", "seo"]:
            name = name.replace(word, word.upper())
            description = description.replace(word, word.upper())
            tools = [t.replace(word, word.upper()) for t in tools]

        # Generate sample code
        sample_code = f"""from openai_agents import Agent, Runner
from mcp_bridge import MCPBridge

# 1. Initialize Bridge
bridge = MCPBridge("https://{HF_USERNAME}-{server_id}.hf.space/sse")

# 2. Setup Agent with {name} Tools
agent = Agent(
    name="{name} Expert",
    instructions="You are an expert in {name}.",
    functions=bridge.get_tools()
)

# 3. Execute
result = Runner.run(agent, "How can I use your tools?")
print(result.final_text)
"""

        return {
            "id": server_id,
            "name": name,
            "description": description,
            "tools": tools,
            "sample_code": sample_code,
            "logs_url": f"https://huggingface.co/spaces/{HF_USERNAME}/{server_id}/logs"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR: get_server_detail failed: {e}")
        return {"error": str(e), "id": server_id, "name": "Error Loading Server", "description": str(e), "tools": [], "sample_code": ""}

@app.on_event("startup")
async def startup_event():
    # 1. Environment Check
    token = os.environ.get("HF_TOKEN")
    is_hub = os.environ.get("MCP_IS_HUB", "false")
    pg_db = os.environ.get("MCP_TRACES_DB")
    
    print("--- MCP HUB BOOT SEQUENCE ---")
    print(f"ENV MCP_IS_HUB: {is_hub}")
    
    if token:
        print(f"ENV HF_TOKEN: Configured ({len(token)} chars)")
    else:
        print("WARNING: HF_TOKEN not set! Live status checks will fail.")
        
    # 2. Database Check
    if pg_db:
        print(f"ENV MCP_TRACES_DB: Configured (Scheme: {pg_db.split(':')[0]})")
        try:
            import psycopg2
            print("DEPENDENCY: psycopg2-binary installed.")
            # We don't connect here to avoid blocking start, but telemetry module will try.
        except ImportError:
            print("CRITICAL ERROR: psycopg2-binary NOT installed. Postgres will fail!")
    else:
        print("ENV MCP_TRACES_DB: Not set. Using SQLite fallback.")
        
    print("--- SEQUENCE COMPLETE ---")

@app.get("/api/servers/{server_id}/logs")
async def get_server_logs(server_id: str):
    """Fetches real-time runtime status and formats it as system logs."""
    if not hf_api:
        return {"logs": "[ERROR] HF API not initialized. Install huggingface_hub."}
    
    try:
        repo_id = f"{HF_USERNAME}/{server_id}" if "/" not in server_id else server_id
        
        # Debug print
        print(f"Fetching logs for {repo_id}...")
        
        loop = asyncio.get_event_loop()
        runtime = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: hf_api.get_space_runtime(repo_id)),
            timeout=10.0
        )
        
        # Format runtime info as logs
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Safely get hardware info
        hardware_info = "UNKNOWN"
        if hasattr(runtime, 'hardware') and runtime.hardware and hasattr(runtime.hardware, 'current'):
            hardware_info = runtime.hardware.current

        log_lines = [
            f"[{ts}] SYSTEM_BOOT: Connected to MCP Stream",
            f"[{ts}] TARGET_REPO: {repo_id}",
            f"[{ts}] RUNTIME_STAGE: {runtime.stage.upper()}",
            f"[{ts}] HARDWARE_SKU: {hardware_info}",
        ]
        
        if hasattr(runtime, 'domains') and runtime.domains:
            for d in runtime.domains:
                log_lines.append(f"[{ts}] DOMAIN_BINDING: {d.domain} [{d.stage}]")
                
        # Safely get replica info
        replica_count = 1
        if hasattr(runtime, 'replicas') and runtime.replicas and hasattr(runtime.replicas, 'current'):
            replica_count = runtime.replicas.current
             
        log_lines.append(f"[{ts}] REPLICA_COUNT: {replica_count}")

        if runtime.stage == "RUNNING":
            log_lines.append(f"[{ts}] STATUS_CHECK: HEALTHY")
            log_lines.append(f"[{ts}] STREAM_GATEWAY: ACTIVE")
        else:
            log_lines.append(f"[{ts}] STATUS_CHECK: {runtime.stage}")

        # --- REAL LOG INJECTION ---
        # Get actual telemetry events from DB
        try:
            # server_id usually matches the DB server column (e.g. mcp-weather)
            # but sometimes we might need mapping if ids differ. Assuming 1:1 for now.
            start_marker = server_id.replace("mcp-", "").upper()
            
            # Fetch Logs
            real_logs = get_recent_logs(server_id, limit=10)
            
            # Fetch Traces
            real_traces = get_recent_traces(server_id, limit=10)
            
        # Prepare Events
        events = []
        if real_logs:
            for l in real_logs:
                events.append({
                    "ts": l["timestamp"], 
                    "line": f"{start_marker}_TOOL: Executed '{l['tool']}'",
                    "type": "log"
                })
        
        if real_traces:
            for t in real_traces:
                status_icon = "✅" if t['status'] == 'ok' else "❌"
                events.append({
                    "ts": t["start_time"],
                    "line": f"TRACE_SPAN: {t['name']} ({t['duration_ms']}ms) {status_icon} [{t['status'].upper()}]",
                    "type": "trace"
                })
        
        # Sort events by timestamp descending (Newest First)
        def parse_ts(x):
            t = x["ts"]
            if isinstance(t, str):
                try:
                    return datetime.fromisoformat(t)
                except:
                    return datetime.now()
            return t
            
        events.sort(key=parse_ts, reverse=True)
        
        # Build Final Log Stream in Descending Order
        final_stream = []
        
        # 1. Newest telemetry events first
        if events:
            for e in events[:20]: # Show top 20
                e_ts = parse_ts(e).strftime("%Y-%m-%d %H:%M:%S")
                final_stream.append(f"[{e_ts}] {e['line']}")
            final_stream.append("-" * 40)
            
        # 2. System status (newest status first)
        final_stream.append(f"[{ts}] STATUS_CHECK: {runtime.stage.upper()}")
        final_stream.append(f"[{ts}] STREAM_GATEWAY: ACTIVE")
        final_stream.append(f"[{ts}] REPLICA_COUNT: {replica_count}")
        final_stream.append(f"[{ts}] HARDWARE_SKU: {hardware_info}")
        final_stream.append(f"[{ts}] RUNTIME_STAGE: {runtime.stage.upper()}")
        final_stream.append(f"[{ts}] TARGET_REPO: {repo_id}")
        final_stream.append(f"[{ts}] SYSTEM_BOOT: Connected to MCP Stream")
        
        return {"logs": "\n".join(final_stream)}
        
    except Exception as e:
        print(f"Log Streaming Error: {e}")
        return {"logs": f"Neural link disrupted: {str(e)}"}

@app.get("/api/servers")
async def list_servers():
    """Returns MCP servers with real metrics and HF status."""
    try:
        print("DEBUG: list_servers called")
        metrics = get_metrics()
        print(f"DEBUG: metrics retrieved (keys: {list(metrics.keys())})")
        
        # 1. Discover local servers in src/
        discovered = {}
        if (PROJECT_ROOT / "src").exists():
            for d in (PROJECT_ROOT / "src").iterdir():
                if d.is_dir() and d.name.startswith("mcp-") and d.name != "mcp-hub":
                    readme_path = d / "README.md"
                    description = "MCP HUB Node"
                    if readme_path.exists():
                        lines = readme_path.read_text().split("\n")
                        # Try to find the first non-header line
                        for line in lines:
                            clean = line.strip()
                            if clean and not clean.startswith("#") and not clean.startswith("-"):
                                description = clean
                                break
                    
                    name = d.name.replace("-", " ").title()
                    # Apply strict capitalization
                    for word in ["Mcp", "Sre", "Rag", "Seo", "mcp", "sre", "rag", "seo"]:
                        name = name.replace(word, word.upper())
                    
                    description = description.replace("mcp", "MCP").replace("Mcp", "MCP").replace("sre", "SRE").replace("Sre", "SRE").replace("rag", "RAG").replace("Rag", "RAG").replace("seo", "SEO").replace("Seo", "SEO")
                    
                    discovered[d.name] = {
                        "id": d.name,
                        "name": name,
                        "description": description
                    }
        print(f"DEBUG: Discovered {len(discovered)} local servers")
        
        # 2. Merge with Known Servers (ensures we don't miss anything in Docker)
        all_servers_map = {s["id"]: s for s in KNOWN_SERVERS}
        all_servers_map.update(discovered) # Discovered overrides known if collision
        
        servers_to_check = list(all_servers_map.values())
        print(f"DEBUG: Checking status for {len(servers_to_check)} servers")
        
        # 3. Check status in parallel
        # Wrap status check to ensure it doesn't fail
        try:
            status_tasks = [get_hf_status(s["id"]) for s in servers_to_check]
            statuses = await asyncio.gather(*status_tasks)
        except Exception as e:
            print(f"DEBUG: Status check failed: {e}")
            statuses = ["Unknown"] * len(servers_to_check)

        results = []
        for idx, s in enumerate(servers_to_check):
            server_metrics = metrics.get(s["id"], {"hourly": 0, "weekly": 0, "monthly": 0})
            
            def fmt(n):
                if n is None: return "0"
                if n >= 1000: return f"{n/1000:.1f}k"
                return str(n)
            
            name = s["name"]
            for word in ["Mcp", "Sre", "Rag", "Seo", "mcp", "sre", "rag", "seo"]:
                        name = name.replace(word, word.upper())

            results.append({
                **s,
                "name": name,
                "status": statuses[idx],
                "metrics": {
                    "hourly": fmt(server_metrics.get("hourly", 0)),
                    "weekly": fmt(server_metrics.get("weekly", 0)),
                    "monthly": fmt(server_metrics.get("monthly", 0)),
                    "raw_hourly": server_metrics.get("hourly", 0),
                    "raw_weekly": server_metrics.get("weekly", 0),
                    "raw_monthly": server_metrics.get("monthly", 0)
                }
            })
        
        print(f"DEBUG: Returning {len(results)} servers")
        return {
            "servers": sorted(results, key=lambda x: x["name"]),
            "system": get_system_metrics()
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "servers": []}

@app.get("/api/usage")
async def get_usage_trends(range: str = "24h"):
    """Returns real usage trends based on the requested time range."""
    range_map = {
        "1h": (1, 60),     # 1 hour -> minutely (60 buckets)
        "24h": (24, 24),   # 24 hours -> hourly (24 buckets)
        "7d": (168, 28),   # 7 days -> 6-hourly (28 buckets)
        "30d": (720, 30)   # 30 days -> daily (30 buckets)
    }
    
    hours, intervals = range_map.get(range, (24, 24))
    history = get_usage_history(range_hours=hours, intervals=intervals)
    
    datasets = []
    for server_id, counts in history["datasets"].items():
        datasets.append({
            "name": server_id.replace("mcp-", "").title(),
            "data": counts
        })
    
    # If no data, return empty
    if not datasets:
        return {"labels": history.get("labels", []), "datasets": []}
        
    return {
        "labels": history["labels"],
        "datasets": datasets
    }

from fastapi.responses import FileResponse

# Mount static files
static_path = Path(__file__).parent / "dist"

if static_path.exists():
    # Mount assets folder specifically
    app.mount("/assets", StaticFiles(directory=str(static_path / "assets")), name="assets")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Check if the requested path exists as a file in dist (e.g., vite.svg)
    file_path = static_path / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    
    # Otherwise, serve index.html for SPA routing
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    return {"error": "Frontend not built. Run 'npm run build' in src/mcp-hub"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
