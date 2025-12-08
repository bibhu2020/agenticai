"""Healthcare Assistant - Entry point for Hugging Face deployment.

This script sets up the Python path and launches the Streamlit application.
"""
import sys
from pathlib import Path

# Add common directory to Python path for shared modules
project_root = Path(__file__).parent
common_path = project_root / "common"
sys.path.insert(0, str(common_path))

# Add src directory to path
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the Streamlit app
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys
    
    # Set up the Streamlit app path
    app_path = str(project_root / "src" / "healthcare-assistant" / "app.py")
    
    # Run Streamlit with the app
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.port=7860",
        "--server.address=0.0.0.0",
        "--server.headless=true"
    ]
    
    sys.exit(stcli.main())
