import os
import subprocess
import sys

# Use module execution to guarantee Streamlit runs inside the current interpreter
subprocess.run([
    sys.executable, "-m", "streamlit",
    "run",
    os.path.join("ui", "app.py"),
    "--server.runOnSave", "true"
])
