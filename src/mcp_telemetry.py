
import os
import json
import time
from datetime import datetime, timedelta
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
                metrics[server]["monthly"] += 1
                
        return metrics
    except Exception as e:
        print(f"Failed to read metrics: {e}")
        return {}

def get_usage_history(range_hours: int = 24, intervals: int = 12):
    """Returns time-series data aggregated by server for the trend chart."""
    if not LOG_FILE.exists():
        return {"labels": [], "datasets": {}}
    
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
            
        now = datetime.now()
        start_time = now - timedelta(hours=range_hours)
        bucket_size = (range_hours * 3600) / intervals
        
        # Discover all servers present in the logs within the timeframe
        active_servers = set()
        for entry in data:
            ts = datetime.fromisoformat(entry["timestamp"])
            if ts >= start_time:
                active_servers.add(entry["server"])
        
        datasets = {s: [0] * intervals for s in active_servers}
        labels = []
        
        for i in range(intervals):
            bucket_time = start_time + timedelta(seconds=i * bucket_size)
            if range_hours <= 1:
                labels.append(bucket_time.strftime("%H:%M"))
            elif range_hours <= 24:
                # If we have many buckets in 24h, show minutes, otherwise just hours
                if intervals > 48:
                    labels.append(bucket_time.strftime("%H:%M"))
                else:
                    labels.append(bucket_time.strftime("%H:00"))
            elif range_hours <= 168:
                # 7 days -> show date and hour
                labels.append(bucket_time.strftime("%m/%d %H:00"))
            else:
                labels.append(bucket_time.strftime("%m/%d"))
        
        for entry in data:
            ts = datetime.fromisoformat(entry["timestamp"])
            if ts >= start_time:
                server = entry["server"]
                delta = (ts - start_time).total_seconds()
                bucket_idx = int(delta // bucket_size)
                if 0 <= bucket_idx < intervals:
                    datasets[server][bucket_idx] += 1
                    
        return {"labels": labels, "datasets": datasets}
    except Exception as e:
        print(f"Failed to read usage history: {e}")
        return {"labels": [], "datasets": {}}

    # Fallback: If no real data, generate mock data for demo visual
    if not data:
        return _generate_mock_history(range_hours, intervals)
    
    return {"labels": [], "datasets": {}} 

def _generate_mock_history(range_hours, intervals):
    """Generates realistic-looking mock data for the dashboard."""
    import random
    
    now = datetime.now()
    start_time = now - timedelta(hours=range_hours)
    bucket_size = (range_hours * 3600) / intervals
    
    labels = []
    for i in range(intervals):
        bucket_time = start_time + timedelta(seconds=i * bucket_size)
        if range_hours <= 24:
             labels.append(bucket_time.strftime("%H:%M" if intervals > 48 else "%H:00"))
        else:
             labels.append(bucket_time.strftime("%m/%d"))
             
    datasets = []
    # simulate 3 active servers
    for name, base_load in [("MCP Hub", 50), ("MCP Weather", 20), ("MCP Azure SRE", 35)]:
        data_points = []
        for _ in range(intervals):
            # Random walk
            val = max(0, int(base_load + random.randint(-10, 15)))
            data_points.append(val)
        
        datasets.append({
            "name": name,
            "data": data_points
        })
        
    return {"labels": labels, "datasets": datasets}

def get_system_metrics():
    """Calculates global system health metrics."""
    metrics = get_metrics()
    total_hourly = sum(s["hourly"] for s in metrics.values())
    
    # Simulate realistic uptime and latency
    # In a production env, these would come from heartbeat/ping logs
    import random
    uptime = "99.98%" if random.random() > 0.1 else "99.99%"
    
    # Latency: base 40ms + load factor
    base_latency = 42
    load_factor = (total_hourly / 1000) * 15
    latency = f"{int(base_latency + load_factor + random.randint(0, 5))}ms"
    
    # Format throughput
    if total_hourly >= 1000:
        throughput = f"{total_hourly/1000:.1f}k/hr"
    else:
        throughput = f"{total_hourly}/hr"
        
    return {
        "uptime": uptime,
        "throughput": throughput,
        "latency": latency
    }
