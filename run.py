#!/usr/bin/env python3
"""
Universal App Launcher for AgenticAI Projects

Usage:
    python run.py <app_name> [--port PORT] [--help]

Examples:
    python run.py healthcare
    python run.py deep-research --port 8502
    python run.py stock-analyst
    python run.py --list
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path
from typing import Dict, Optional
# from agents import Runner, SQLiteSession
# from agents import set_trace_processors
# from langsmith.wrappers import OpenAIAgentsTracingProcessor

# Load environment variables explicitly
from dotenv import load_dotenv
load_dotenv(override=True)

# App registry - maps app names to their paths and entry points
APP_REGISTRY: Dict[str, Dict[str, str]] = {
    "healthcare": {
        "path": "src/healthcare-assistant",
        "entry": "app.py",
        "description": "Healthcare Assistant - Medical information with RAG and web search"
    },
    "deep-research_v1": {
        "path": "src/deep-research_v1",
        "entry": "app.py",
        "description": "Deep Research AI - Comprehensive research assistant"
    },
    "deep-research_v2": {
        "path": "src/deep-research_v2",
        "entry": "app.py",
        "description": "Deep Research AI - Comprehensive research assistant"
    },
    "stock-analyst": {
        "path": "src/stock-analyst",
        "entry": "app.py",
        "description": "Stock Analyst - Financial analysis and stock recommendations"
    },
    "travel-agent": {
        "path": "src/travel-agent",
        "entry": "app.py",
        "description": "Travel Agent - Trip planning and travel recommendations"
    },
    "trip-planner": {
        "path": "src/trip-planner",
        "entry": "main.py",
        "type": "fastapi",
        "description": "Trip Planner - Detailed trip itinerary planning"
    },
    "chatbot_v1": {
        "path": "src/chatbot_v1",
        "entry": "app.py",
        "description": "General Chatbot - Multi-purpose conversational AI"
    },
    "chatbot_v2": {
        "path": "src/chatbot_v2",
        "entry": "app.py",
        "description": "Layered Chatbot (ReAct) - Advanced Architecture"
    },
    "accessibility_v2": {
        "path": "src/accessibility_v2",
        "entry": "app.py",
        "description": "Accessibility Auditor V2 - Layered Architecture"
    },
    "accessibility_v1": {
        "path": "src/accessibility_v1",
        "entry": "app.py",
        "description": "Accessibility Tools - Assistive technology applications"
    },
    "literature-review": {
        "path": "src/literature-review",
        "entry": "app.py",
        "description": "Literature Review Assistant - Multi-agent literature review tool"
    },
    "market-analyst": {
        "path": "src/market-analyst",
        "entry": "backend/main.py",
        "type": "fastapi",
        "description": "Market Analyst - Decoupled Multi-agent market analysis (Vue.js + FastAPI)"
    },
    "image": {
        "path": "src/image-generator",
        "entry": "app.py",
        "description": "Image Generator - Multi-agent image generation tool"
    },
    "interview-assistant": {
        "path": "src/interview-assistant",
        "entry": "app.py",
        "description": "Interview Assistant - Multi-agent interview tool"
    },
    "finadvisor-lg": {
        "path": "src/finadvisor",
        "entry": "app-lg.py",
        "description": "Financial Advisor - Multi-agent financial advisor tool using LangGraph"
    },
    "finadvisor-oai": {
        "path": "src/finadvisor",
        "entry": "app-oai.py",
        "description": "Financial Advisor - Multi-agent financial advisor tool using OpenAI"
    },
    "finadvisor-phi": {
        "path": "src/finadvisor",
        "entry": "app-phi.py",
        "description": "Financial Advisor - Multi-agent financial advisor tool using Phidata"
    }
    ,
    "finadvisor-ag": {
        "path": "src/finadvisor",
        "entry": "app-ag.py",
        "description": "Financial Advisor - Multi-agent financial advisor tool using Autogen"
    },
    "mcp-trader": {
        "path": "src/mcp-trader",
        "entry": "server.py",
        "type": "script",
        "description": "Strategies MCP Server - FastMCP server for trading strategies"
    },
    "mcp-web": {
        "path": "src/mcp-web",
        "entry": "server.py",
        "type": "script",
        "description": "Web MCP Server - Search, Extract, Wikipedia, Arxiv"
    },
    "mcp-azure-sre": {
        "path": "src/mcp-azure-sre",
        "entry": "server.py",
        "type": "script",
        "description": "Azure SRE MCP Server - Manage Azure Resources & Monitoring"
    },
    "mcp-rag-secure": {
        "path": "src/mcp-rag-secure",
        "entry": "server.py",
        "type": "script",
        "description": "Secure RAG MCP Server - Multi-tenant knowledge base"
    },
    "mcp-trading-research": {
        "path": "src/mcp-trading-research",
        "entry": "server.py",
        "type": "script",
        "description": "Trading Research MCP Server - News, Insider, Analysts"
    },
    "mcp-github": {
        "path": "src/mcp-github",
        "entry": "server.py",
        "type": "script",
        "description": "GitHub MCP Server - Issues, PRs, Alerts"
    },
    "mcp-seo": {
        "path": "src/mcp-seo",
        "entry": "server.py",
        "type": "script",
        "description": "SEO & ADA MCP Server - Website Audits"
    },
    "github-portal": {
        "path": "src/github-portal",
        "entry": "app.py",
        "type": "streamlit",
        "description": "GitHub Portal - Repository health dashboard for issues, security, and pipelines"
    },
    "mcp-hub": {
        "path": "src/mcp-hub",
        "entry": "package.json",
        "type": "npm",
        "description": "MCP HUB - Discovery and monitoring portal (Vue.js)"
    },
    "test": {
        "path": ".",
        "entry": "tests",
        "type": "test",
        "description": "Run Project Tests - Executes pytest suite"
    },
    "salesdata": {
        "path": "src/salesdata",
        "entry": "app.py",
        "type": "salesdata",
        "description": "Sales Data Agent - Agentic RAG over sales CSV (FastAPI + Streamlit)"
    }
}


def print_banner():
    """Print a nice banner."""
    print("=" * 70)
    print("🚀 AgenticAI Projects Launcher".center(70))
    print("=" * 70)
    print()


def list_apps():
    """List all available apps."""
    print_banner()
    print("Available Applications:\n")
    
    max_name_len = max(len(name) for name in APP_REGISTRY.keys())
    
    for name, config in sorted(APP_REGISTRY.items()):
        print(f"  {name.ljust(max_name_len + 2)} - {config['description']}")
    
    print("\n" + "=" * 70)
    print("\nUsage: python run.py <app_name> [--port PORT]")
    print("Example: python run.py healthcare --port 8501\n")


def validate_app(app_name: str) -> Optional[Dict[str, str]]:
    """
    Validate that the app exists and its files are present.
    
    Args:
        app_name: Name of the app to validate
        
    Returns:
        App configuration dict if valid, None otherwise
    """
    if app_name not in APP_REGISTRY:
        print(f"❌ Error: Unknown app '{app_name}'")
        print(f"\nAvailable apps: {', '.join(sorted(APP_REGISTRY.keys()))}")
        print("\nRun 'python run.py --list' to see all available apps.")
        return None
    
    config = APP_REGISTRY[app_name]
    project_root = Path(__file__).parent
    app_path = project_root / config["path"] / config["entry"]
    
    if not app_path.exists():
        print(f"❌ Error: App file not found at {app_path}")
        return None
    
    return config


def launch_app(app_name: str, port: Optional[int] = None):
    """
    Launch a Streamlit app.
    
    Args:
        app_name: Name of the app to launch
        port: Optional port number (default: 8501)
    """
    config = validate_app(app_name)
    if not config:
        sys.exit(1)
    
    project_root = Path(__file__).parent
    app_dir = project_root / config["path"]
    app_file = config["entry"]
    
    print_banner()
    print(f"📱 Launching: {config['description']}")
    print(f"📂 Location: {config['path']}")
    print(f"🌐 Entry Point: {app_file}")
    
    app_type = config.get("type", "streamlit")
    
    python_exe = sys.executable
    is_windows = sys.platform == "win32"
    
    # Prepare environment with project root in PYTHONPATH to fix imports
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root) + os.pathsep + env.get("PYTHONPATH", "")
    
    # Decoupled App Logic: Build frontend if needed
    if app_name == "market-analyst":
        frontend_dir = project_root / "src/market-analyst/frontend"
        dist_dir = frontend_dir / "dist"
        if not dist_dir.exists():
            print("\n🛠️ Frontend build missing. Building now...")
            subprocess.run(["npm", "run", "build"], cwd=frontend_dir, shell=is_windows)
            print("✅ Frontend built.\n")
    
    # App Type specific logic
    if app_type == "fastapi":
        # Extract module name from entry point (e.g. backend/main.py -> backend.main)
        module_path = app_file.replace(".py", "").replace("/", ".").replace("\\", ".")
        cmd = [python_exe, "-m", "uvicorn", f"{module_path}:app", "--host", "0.0.0.0"]
        default_port = 8000
    elif app_type == "script":
        cmd = [python_exe, app_file]
        default_port = None
    elif app_type == "test":
        cmd = [python_exe, "-m", "pytest", app_file, "-v"]
        default_port = None
    elif app_type == "npm":
        cmd = ["npm", "run", "dev"]
        default_port = 5173
    else:
        cmd = [python_exe, "-m", "streamlit", "run", app_file]
        default_port = 8501
    
    # Add port if specified
    actual_port = port if port else default_port
    
    if app_type in ["streamlit", "fastapi", "npm"]:
        if port:
            if app_type == "fastapi":
                cmd.extend(["--port", str(port)])
            elif app_type == "npm":
                cmd.extend(["--", "--port", str(port)])
            else:
                cmd.extend(["--server.port", str(port)])
            print(f"🔌 Port: {port}")
        else:
            print(f"🔌 Port: {default_port} (default)")
            
        # Kill any process using the target port (Port is only relevant for web apps)
        try:
            import platform
            if platform.system() != "Windows":
                # Use fuser on Linux/Mac to kill processes on the port
                kill_cmd = ["fuser", "-k", f"{actual_port}/tcp"]
                subprocess.run(kill_cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                print(f"🧹 Cleaned up port {actual_port}")
        except Exception:
            pass  # Silently continue if cleanup fails
    
    print("\n" + "=" * 70)
    print("\n🎯 Starting application...\n")
    
    print(f"\n\nPYTHONPATH: {env['PYTHONPATH']}")

    try:
        # Change to app directory and run
        os.chdir(app_dir)
        
        # Special case for mcp-hub: launch backend API first
        if app_name == "mcp-hub":
            print("🚀 Starting MCP Hub Backend API on port 8001...")
            api_cmd = [python_exe, "api.py"]
            subprocess.Popen(api_cmd, env=env, shell=is_windows)

        # Special case for salesdata: launch FastAPI backend + Streamlit frontend
        if app_name == "salesdata":
            api_port = 8080
            ui_port = port if port else 8501

            # Aggressively kill any stale processes on both ports
            import platform
            if platform.system() != "Windows":
                for p in [api_port, ui_port]:
                    # lsof is more reliable than fuser for finding PIDs by port
                    result = subprocess.run(
                        ["lsof", "-ti", f":{p}"],
                        capture_output=True, text=True
                    )
                    pids = result.stdout.strip().split()
                    for pid in pids:
                        subprocess.run(["kill", "-9", pid],
                                       stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                time.sleep(1)  # let OS release ports
                print(f"🧹 Cleaned up ports {api_port} and {ui_port}")

            print(f"🚀 Starting Sales Agent API on port {api_port}...")
            api_cmd = [
                python_exe, "-m", "uvicorn", "api:app",
                "--host", "0.0.0.0", "--port", str(api_port)
            ]
            subprocess.Popen(api_cmd, env=env, shell=is_windows, cwd=app_dir)

            # Poll /health until agent is ready (instead of a fixed sleep)
            import urllib.request, urllib.error, json as _json
            health_url = f"http://localhost:{api_port}/health"
            print(f"⏳ Waiting for API + agent to be ready", end="", flush=True)
            timeout = 90  # seconds
            ready = False
            for _ in range(timeout):
                time.sleep(1)
                print(".", end="", flush=True)
                try:
                    with urllib.request.urlopen(health_url, timeout=2) as r:
                        data = _json.loads(r.read())
                        if data.get("agent_ready"):
                            ready = True
                            break
                except Exception:
                    pass
            print()
            if not ready:
                print("⚠️  API did not become ready within 90s — launching UI anyway")

            print(f"🌐 Starting Streamlit UI on port {ui_port}...")
            ui_cmd = [
                python_exe, "-m", "streamlit", "run", "app.py",
                "--server.port", str(ui_port)
            ]
            subprocess.run(ui_cmd, env=env, shell=is_windows)
            return




        subprocess.run(cmd, env=env, shell=is_windows)
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except FileNotFoundError:
        binary = "command"
        if app_type == "fastapi": binary = "uvicorn"
        elif app_type == "streamlit": binary = "streamlit"
        elif app_type == "test": binary = "pytest"
        
        print(f"\n❌ Error: {binary} not found in the current environment.")
        print(f"   Please install it: pip install {binary}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error launching app: {e}")
        sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Universal launcher for AgenticAI project applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py healthcare              # Launch healthcare chatbot
  python run.py deep-research --port 8502   # Launch on custom port
  python run.py --list                  # List all available apps

Available Apps:
  """ + "\n  ".join(f"{name}: {config['description']}" 
                     for name, config in sorted(APP_REGISTRY.items()))
    )
    
    parser.add_argument(
        "app_name",
        nargs="?",
        help="Name of the app to launch"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        help="Port number for Streamlit server (default: 8501)"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available apps"
    )
    
    args = parser.parse_args()
    
    # Handle --list flag
    if args.list:
        list_apps()
        return
    
    # Require app name if not listing
    if not args.app_name:
        parser.print_help()
        print("\n")
        list_apps()
        return
    
    # Launch the app
    launch_app(args.app_name, args.port)


if __name__ == "__main__":
    # set_trace_processors([OpenAIAgentsTracingProcessor()])
    main()
