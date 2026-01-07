import sys
import os

# Add the current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from patterns.react_agent import ReActAgent

def main():
    agent = ReActAgent()
    
    print("=== Agentic Architecture Demo ===")
    print("This app demonstrates the separation of Layers (Human Organs) and Patterns (Human Behavior).")
    print("Files involved:")
    print(" - layers/perception.py (See)")
    print(" - layers/cognition.py (Think)")
    print(" - layers/action.py (Do)")
    print(" - patterns/react_agent.py (The Logic Loop)\n")
    
    # Scene 1: Simple Math
    print("\n>>> User: calculate 120 + 25")
    agent.run("calculate 120 + 25")
    
    # Scene 2: File Operations 
    print("\n>>> User: save a note to hello.txt saying 'Agentic AI is cool'")
    agent.run("save a note to hello.txt saying 'Agentic AI is cool'")

    # Scene 3: Verification
    print("\n>>> User: read the note hello.txt")
    agent.run("read the note hello.txt")

if __name__ == "__main__":
    main()
