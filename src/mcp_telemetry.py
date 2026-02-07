
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Use a central log file for usages
# In Docker/HF, /tmp is writable. Locally, use the project root.
import sys
if os.path.exists("/app"):
    LOG_FILE = Path("/tmp/mcp_usage_log.json")
else:
    LOG_FILE = Path(__file__).parent.parent / "mcp_usage_log.json"

def log_usage(server_name: str, tool_name: str):
    """Logs a tool call with timestamp."""
    try:
        data = []
        if LOG_FILE.exists():
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "server": server_name,
            "tool": tool_name
        }
        data.append(entry)
        
        # Keep only last 10,000 logs for performance
        if len(data) > 10000:
            data = data[-10000:]
            
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to log usage: {e}")

def get_metrics():
    """Aggregates metrics from the log file."""
    if not LOG_FILE.exists():
        return {}
    
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
            
        now = datetime.now()
        metrics = {}
        
        for entry in data:
            server = entry["server"]
            ts = datetime.fromisoformat(entry["timestamp"])
            
            if server not in metrics:
                metrics[server] = {"hourly": 0, "weekly": 0, "monthly": 0}
            
            # Simple duration checks
            delta = now - ts
            if delta.total_seconds() < 3600:
                metrics[server]["hourly"] += 1
            if delta.days < 7:
                metrics[server]["weekly"] += 1
            if delta.days < 30:
                metrics[server]["monthly"] += 1
                
        return metrics
    except Exception as e:
        print(f"Failed to read metrics: {e}")
        return {}
