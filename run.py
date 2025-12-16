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
from pathlib import Path
from typing import Dict, Optional
from agents import Runner, SQLiteSession
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
    "deep-research": {
        "path": "src/deep-research",
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
        "description": "Trip Planner - Detailed trip itinerary planning"
    },
    "chatbot": {
        "path": "src/chatbot",
        "entry": "app.py",
        "description": "General Chatbot - Multi-purpose conversational AI"
    },
    "accessibility": {
        "path": "src/accessibility",
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
        "entry": "app.py",
        "description": "Market Analyst - Multi-agent market analysis tool"
    },
    "image": {
        "path": "src/image-generator",
        "entry": "app.py",
        "description": "Image Generator - Multi-agent image generation tool"
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
    
    # Build streamlit command
    cmd = ["streamlit", "run", app_file]
    
    # Add port if specified
    if port:
        cmd.extend(["--server.port", str(port)])
        print(f"🔌 Port: {port}")
    else:
        print(f"🔌 Port: 8501 (default)")
    
    print("\n" + "=" * 70)
    print("\n🎯 Starting application...\n")
    
    # Prepare environment with project root in PYTHONPATH to fix imports
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root) + os.pathsep + env.get("PYTHONPATH", "")
    print(f"\n\nPYTHONPATH: {env['PYTHONPATH']}")

    try:
        # Change to app directory and run
        os.chdir(app_dir)
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except FileNotFoundError:
        print("\n❌ Error: Streamlit not found. Please install it:")
        print("   pip install streamlit")
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
