#!/usr/bin/env python3
"""
Universal App Launcher for AgenticAI Projects

Usage:
    python run.py <app_name> [--port PORT] [--help]

Examples:
    python run.py remedy
    python run.py athena --port 8502
    python run.py midas
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
    "nexus": {
        "path": "src/nexus",
        "entry": "app.py",
        "description": "Nexus - AI Research Assistant - Multi-specialist orchestrator for finance, news, and web research"
    },
    "athena": {
        "path": "src/athena",
        "entry": "app.py",
        "description": "Athena - Deep Research Reporter - Plans, searches, and synthesises comprehensive research reports"
    },
    "remedy": {
        "path": "src/remedy",
        "entry": "app.py",
        "description": "Remedy - Healthcare RAG Advisor - Medical information retrieval using RAG and web search"
    },
    "midas": {
        "path": "src/midas",
        "entry": "app.py",
        "description": "Midas - Stock Investment Analyst - Multi-agent investment team for technical and sentiment analysis"
    },
    "odyssey": {
        "path": "src/odyssey",
        "entry": "app.py",
        "description": "Odyssey - Travel Planner - AI-powered trip planning with flight, hotel, and itinerary recommendations"
    },
    "waypoint": {
        "path": "src/waypoint",
        "entry": "main.py",
        "type": "fastapi",
        "description": "Waypoint - Trip Planner API - Phidata-powered trip itinerary planning REST API"
    },
    "agora": {
        "path": "src/agora",
        "entry": "backend/main.py",
        "type": "fastapi",
        "description": "Agora - AI Market Analyst - Real-time multi-agent market analysis with streaming (Vue.js + FastAPI)"
    },
    "fifa": {
        "path": "src/fifa",
        "entry": "backend/main.py",
        "type": "fastapi",
        "description": "FIFA - World Cup 2026 Dashboard - Live scores, schedule & news powered by LangGraph + Gemini (Vue.js PWA + FastAPI)"
    },
    "news": {
        "path": "src/news",
        "entry": "backend/main.py",
        "type": "fastapi",
        "description": "News - Daily News Digest - Top 5 stories across 10 categories powered by LangGraph + Claude (OpenRouter) (Vue.js PWA + FastAPI)"
    },
    "test": {
        "path": ".",
        "entry": "tests",
        "type": "test",
        "description": "Run Project Tests - Executes pytest suite"
    },
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
    print("Example: python run.py remedy --port 8501\n")


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
    if app_name in ("agora", "fifa", "news"):
        frontend_dir = project_root / f"src/{app_name}/frontend"
        dist_dir = frontend_dir / "dist"
        if not dist_dir.exists():
            print(f"\n🛠️  Frontend build missing for {app_name}. Building now...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, shell=is_windows)
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
  python run.py remedy                  # Launch Remedy healthcare chatbot
  python run.py athena --port 8502      # Launch on custom port
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
