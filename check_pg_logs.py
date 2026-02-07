
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to sys.path
sys.path.append(str(Path(__file__).parent / "src"))

# Set Environment Variables manually for the script to use the right DB
# These will be overridden by the shell export but it's good for robustness
from core.mcp_telemetry import _get_conn

def check():
    try:
        conn = _get_conn()
        cur = conn.cursor()
        
        # Check last hour (UTC)
        start = datetime.utcnow() - timedelta(hours=1)
        cur.execute("SELECT COUNT(*) FROM logs WHERE timestamp >= %s", (start,))
        count = cur.fetchone()[0]
        print(f"Logs in last hour (UTC): {count}")
        
        # Check last hour (Local)
        start_local = datetime.now() - timedelta(hours=1)
        cur.execute("SELECT COUNT(*) FROM logs WHERE timestamp >= %s", (start_local,))
        count_local = cur.fetchone()[0]
        print(f"Logs in last hour (Local): {count_local}")
        
        # Check last 7 days
        start_7d = datetime.now() - timedelta(days=7)
        cur.execute("SELECT COUNT(*) FROM logs WHERE timestamp >= %s", (start_7d,))
        count_7d = cur.fetchone()[0]
        print(f"Logs in last 7 days (Postgres): {count_7d}")
        
        # Check total
        cur.execute("SELECT COUNT(*) FROM logs")
        total = cur.fetchone()[0]
        print(f"Total logs (Postgres): {total}")
        
        # Check distinct servers
        cur.execute("SELECT DISTINCT server FROM logs")
        servers = [r[0] for r in cur.fetchall()]
        print(f"Servers in DB: {servers}")
        
        # List some recent non-Hub ones if any
        if count_7d > 0:
            print("\nRecent non-Hub logs (last 10):")
            cur.execute("SELECT server, timestamp, tool FROM logs WHERE server != 'MCP Hub' ORDER BY timestamp DESC LIMIT 10")
            for r in cur.fetchall():
                print(f"  {r[0]}: {r[2]} at {r[1]}")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
