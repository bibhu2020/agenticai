
import subprocess
import time
import requests
import sys
import os

def test_stream():
    # Start API
    env = os.environ.copy()
    env["PYTHONPATH"] = env.get("PYTHONPATH", "") + ":" + os.getcwd() + "/src"
    env["MCP_IS_HUB"] = "true"
    
    # Ensure local DB is used
    if os.path.exists("mcp_logs.db"):
        os.remove("mcp_logs.db")
        
    proc = subprocess.Popen(["python3", "src/mcp-hub/api.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("API Started with PID", proc.pid)
    
    try:
        time.sleep(5)
        
        # Send Trace
        trace_payload = {
            "server": "mcp-weather",
            "trace_id": "test-trace-1",
            "span_id": "span-1",
            "name": "ImportantWeatherCheck",
            "duration_ms": 500.0,
            "status": "ok",
            "start_time": "2023-10-27T10:00:00"
        }
        
        print("Sending trace...")
        r = requests.post("http://localhost:7860/api/telemetry/trace", json=trace_payload, timeout=2)
        print("Trace Response:", r.status_code, r.text)
        
        # Give DB time to write
        time.sleep(2)
        
        # Fetch Logs
        print("Fetching logs...")
        r = requests.get("http://localhost:7860/api/servers/mcp-weather/logs", timeout=2)
        print("Logs Response:", r.status_code)
        logs = r.json().get("logs", "")
        print("--- LOG CONTENT ---")
        print(logs)
        print("-------------------")
        
        if "ImportantWeatherCheck" in logs and "TRACE_SPAN" in logs:
            print("SUCCESS: Trace found in log stream.")
        else:
            print("FAILURE: Trace NOT found in log stream.")
            
            # Print API Output for debugging
            print("\n--- API PROCESS OUTPUT ---")
            proc.terminate()
            try:
                outs, errs = proc.communicate(timeout=5)
                print("STDOUT:", outs.decode('utf-8', errors='replace'))
                print("STDERR:", errs.decode('utf-8', errors='replace'))
            except Exception as e:
                print(f"Could not read output: {e}")
            sys.exit(1)
            
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()

if __name__ == "__main__":
    test_stream()
