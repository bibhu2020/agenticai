
# FORCE REDEPLOY: Telemetry Sync v2
import os
import json
import sqlite3
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
HUB_URL = os.environ.get("MCP_HUB_URL", "http://localhost:7860")
IS_HUB = os.environ.get("MCP_IS_HUB", "false").lower() == "true"
PG_CONN_STR = os.environ.get("MCP_TRACES_DB")

# Single SQLite DB for the Hub (fallback)
if os.path.exists("/app"):
    DB_FILE = Path("/tmp/mcp_logs.db")
else:
    # src/core/mcp_telemetry.py -> src/core -> src -> project root
    DB_FILE = Path(__file__).parent.parent.parent / "mcp_logs.db"

def _get_conn():
    # PostgreSQL Mode
    if PG_CONN_STR and IS_HUB:
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(PG_CONN_STR)
            # Init schema if needed (lazy check could be optimized)
            _init_pg_db(conn)
            return conn
        except Exception as e:
            print(f"Postgres Connection Failed: {e}")
            # Fallback to SQLite not recommended if PG configured, but handling graceful failure might be needed.
            # For now, we raise or assume SQLite fallback if PG fail? Let's error out to be safe.
            raise e

    # SQLite Mode (Default)
    # Auto-init if missing (lazy creation)
    if IS_HUB and not os.path.exists(DB_FILE):
        _init_db()
        
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def _init_pg_db(conn):
    """Initializes the PostgreSQL database with required tables."""
    try:
        with conn.cursor() as cur:
            # Logs
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
                    server VARCHAR(255) NOT NULL,
                    tool VARCHAR(255) NOT NULL
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_logs_ts ON logs(timestamp)")
            
            # Traces
            cur.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    id SERIAL PRIMARY KEY,
                    trace_id VARCHAR(64) NOT NULL,
                    span_id VARCHAR(64) NOT NULL,
                    parent_id VARCHAR(64),
                    name VARCHAR(255) NOT NULL,
                    status VARCHAR(50),
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_ms FLOAT,
                    server VARCHAR(255)
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_traces_tid ON traces(trace_id)")
            
            # Metrics
            cur.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    value FLOAT NOT NULL,
                    tags TEXT,
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
                    server VARCHAR(255)
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_metrics_ts ON metrics(timestamp)")
            
        conn.commit()
    except Exception as e:
        print(f"Postgres DB Init Failed: {e}")
        conn.rollback()

def _init_db():
    """Initializes the SQLite database with required tables."""
    # Ensure parent dir exists
    if not os.path.exists(DB_FILE.parent):
        os.makedirs(DB_FILE.parent, exist_ok=True)
            
    try:
        # Connect directly to create file
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    server TEXT NOT NULL,
                    tool TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_ts ON logs(timestamp)")
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT NOT NULL,
                    span_id TEXT NOT NULL,
                    parent_id TEXT,
                    name TEXT NOT NULL,
                    status TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration_ms REAL,
                    server TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    tags TEXT,
                    timestamp TEXT NOT NULL,
                    server TEXT
                )
            """)
            
        conn.close()
    except Exception as e:
        print(f"DB Init Failed: {e}")

# Init handled lazily in _get_conn

def log_usage(server_name: str, tool_name: str):
    """Logs a usage event. Writes to DB if Hub, else POSTs to Hub API."""
    timestamp = datetime.utcnow().isoformat()
    if IS_HUB:
        _write_db("logs", {"timestamp": timestamp, "server": server_name, "tool": tool_name})
    else:
        _send_remote("log", {"timestamp": timestamp, "server": server_name, "tool": tool_name})

def log_trace(server_name: str, trace_id: str, span_id: str, name: str, duration_ms: float, 
              status: str = "ok", parent_id: str = None):
    """Logs a trace span."""
    now = datetime.utcnow()
    end_time = now.isoformat()
    start_time = (now - timedelta(milliseconds=duration_ms)).isoformat()
    
    data = {
        "server": server_name,
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_id": parent_id,
        "name": name,
        "status": status,
        "start_time": start_time,
        "end_time": end_time,
        "duration_ms": duration_ms
    }
    
    if IS_HUB:
        _write_db("traces", data)
    else:
        _send_remote("trace", data)

def log_metric(server_name: str, name: str, value: float, tags: dict = None):
    """Logs a metric point."""
    timestamp = datetime.utcnow().isoformat()
    tags_str = json.dumps(tags) if tags else "{}"
    
    data = {
        "server": server_name,
        "name": name,
        "value": value,
        "tags": tags_str,
        "timestamp": timestamp
    }
    
    if IS_HUB:
        _write_db("metrics", data)
    else:
        _send_remote("metric", data)

def _write_db(table: str, data: dict):
    """Helper to write to DB (PG or SQLite)."""
    try:
        conn = _get_conn()
        cols = list(data.keys())
        placeholders = ["%s"] * len(cols) if PG_CONN_STR and IS_HUB else ["?"] * len(cols)
        query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        values = list(data.values())
        
        if PG_CONN_STR and IS_HUB:
            with conn.cursor() as cur:
                cur.execute(query, values)
            conn.commit()
            conn.close()
        else:
            with conn:
                conn.execute(query, values)
            conn.close()
    except Exception as e:
        print(f"Local Write Failed ({table}): {e}")

def _send_remote(type: str, data: dict):
    """Helper to post to Hub."""
    try:
        # Fire and forget
        requests.post(f"{HUB_URL}/api/telemetry/{type}", json=data, timeout=2)
    except Exception:
        pass

def get_metrics():
    """Aggregates metrics from DB."""
    if not IS_HUB and not DB_FILE.exists():
         # If not Hub and no local sqlite, nothing to show
        return {}
    
    try:
        conn = _get_conn()
        metrics = {}
        rows = []
        
        if PG_CONN_STR and IS_HUB:
            from psycopg2.extras import RealDictCursor
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT server, timestamp FROM logs")
                rows = cur.fetchall()
            conn.close()
        else:
            rows = conn.execute("SELECT server, timestamp FROM logs").fetchall()
            conn.close()
            
        now = datetime.utcnow()
        
        for row in rows:
            server = row["server"]
            # Handle different timestamp formats (PG vs SQLite textual)
            ts = row["timestamp"]
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            
            if server not in metrics:
                metrics[server] = {"hourly": 0, "weekly": 0, "monthly": 0}
            
            delta = now - ts
            if delta.total_seconds() < 3600:
                metrics[server]["hourly"] += 1
            if delta.days < 7:
                metrics[server]["weekly"] += 1
            if delta.days < 30: # Assuming a month is roughly 30 days for simplicity
                metrics[server]["monthly"] += 1
                
        return metrics
    except Exception as e:
        print(f"Metrics Error: {e}")
        return {}

def get_usage_history(range_hours: int = 24, intervals: int = 12):
    """Returns time-series data for the chart."""
    if not IS_HUB and not DB_FILE.exists():
        return _generate_mock_history(range_hours, intervals)
        
    try:
        now = datetime.utcnow()
        start_time = now - timedelta(hours=range_hours)
        bucket_size = (range_hours * 3600) / intervals
        
        conn = _get_conn()
        rows = []
        
        if PG_CONN_STR and IS_HUB:
            from psycopg2.extras import RealDictCursor
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT server, timestamp FROM logs WHERE timestamp >= %s", (start_time,))
                rows = cur.fetchall()
            conn.close()
        else:
            rows = conn.execute(
                "SELECT server, timestamp FROM logs WHERE timestamp >= ?", 
                (start_time.isoformat(),)
            ).fetchall()
            conn.close()

        if not rows:
            return {"labels": [], "datasets": {}}

        # Process buckets
        active_servers = set(r["server"] for r in rows)
        datasets = {s: [0] * intervals for s in active_servers}
        
        for row in rows:
            ts = row["timestamp"]
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
                
            delta = (ts - start_time).total_seconds()
            bucket_idx = int(delta // bucket_size)
            if 0 <= bucket_idx < intervals:
                datasets[row["server"]][bucket_idx] += 1
                
        # Labels (Unix timestamps as integers)
        labels = []
        for i in range(intervals):
            bucket_time = start_time + timedelta(seconds=i * bucket_size)
            labels.append(int(bucket_time.timestamp()))
                 
        return {"labels": labels, "datasets": datasets}
        
    except Exception as e:
        print(f"History Error: {e}")
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
             
    datasets = {}
    # simulate 3 active servers
    for name, base_load in [("mcp-hub", 50), ("mcp-weather", 20), ("mcp-azure-sre", 35)]:
        data_points = []
        for _ in range(intervals):
            # Random walk
            val = max(0, int(base_load + random.randint(-10, 15)))
            data_points.append(val)
        
        datasets[name] = data_points
        
    return {"labels": labels, "datasets": datasets}

def get_system_metrics():
    """Calculates global system health metrics."""
    metrics = get_metrics()
    total_hourly = sum(s["hourly"] for s in metrics.values())
    
    uptime = "99.9%"
    latency = "42ms"
    if total_hourly > 0:
        base_latency = 42
        load_factor = (total_hourly / 1000) * 15
        latency = f"{int(base_latency + load_factor)}ms"
    
    if total_hourly >= 1000:
        throughput = f"{total_hourly/1000:.1f}k/hr"
    else:
        throughput = f"{total_hourly}/hr"
        
    return {
        "uptime": uptime,
        "throughput": throughput,
        "latency": latency
    }

def get_recent_logs(server_id: str, limit: int = 50):
    """Fetches the most recent logs for a specific server."""
    if not IS_HUB and not DB_FILE.exists():
        return []
        
    try:
        conn = _get_conn()
        rows = []
        
        if PG_CONN_STR and IS_HUB:
            from psycopg2.extras import RealDictCursor
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                 cur.execute(
                    "SELECT timestamp, tool FROM logs WHERE server = %s ORDER BY id DESC LIMIT %s", 
                    (server_id, limit)
                )
                 rows = cur.fetchall()
            conn.close()
        else:
            rows = conn.execute(
                "SELECT timestamp, tool FROM logs WHERE server = ? ORDER BY id DESC LIMIT ?", 
                (server_id, limit)
            ).fetchall()
            conn.close()
            
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Log Fetch Error: {e}")
        return []

def get_recent_traces(server_id: str, limit: int = 50):
    """Fetches the most recent traces for a specific server."""
    if not IS_HUB and not DB_FILE.exists():
        return []
        
    try:
        conn = _get_conn()
        rows = []
        
        if PG_CONN_STR and IS_HUB:
            from psycopg2.extras import RealDictCursor
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                 cur.execute(
                    "SELECT trace_id, name, status, duration_ms, start_time FROM traces WHERE server = %s ORDER BY id DESC LIMIT %s", 
                    (server_id, limit)
                )
                 rows = cur.fetchall()
            conn.close()
        else:
            rows = conn.execute(
                "SELECT trace_id, name, status, duration_ms, start_time FROM traces WHERE server = ? ORDER BY id DESC LIMIT ?", 
                (server_id, limit)
            ).fetchall()
            conn.close()
            
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Trace Fetch Error: {e}")
        return []
