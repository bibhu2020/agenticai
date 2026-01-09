# Agentic AI: V1 - Explicit Implementation (No Frameworks)

> **Core Concept: "From Scratch"**
> This version demonstrates the core layers of an Agentic System built **explicitly** using pure Python and the OpenAI API. 
> It **does NOT** use any high-level agent frameworks (like LangChain, AutoGen, or OpenAI Agents SDK). 
> The goal is to reveal the internal mechanics—how Perception, Cognition, Action, and Memory communicate—without "magic".
>
> 👉 For the implementation using the **OpenAI Agents SDK**, see **[Architecture V2](../architecture_v2)**.

## Project Overview

This project demonstrates the core distinction between **Agentic Architecture Layers** (the structural components) and **Design Patterns** (the behavioral logic).

It is designed as a "Glass Box" implementation so you can see exactly how the components interact.

## 📂 Project Structure

```
architecture/
├── layers/               # THE ANATOMY (Physical Components)
│   ├── perception.py     # "The Eyes" - Inputs & Sensing
│   ├── cognition.py      # "The Brain" - Decision Making (Mock LLM)
│   ├── action.py         # "The Hands" - Tool Execution
│   └── memory.py         # "The Memory" - State Handling
│
├── patterns/             # THE BEHAVIOR (Workflows)
│   └── react_agent.py    # ReAct Pattern (Loop: Perceive -> Reason -> Act)
│
└── main.py               # Entry point
```

---

## 🏗️ Architecture Layers
Layers represent the *separation of concerns* in the codebase.

### 1. Perception Layer (`layers/perception.py`)
- **Role**: The interface between the agent and the outside world.
- **Function**: Accepts raw input (user text, logs, etc.), cleans it, and timestamps it. It does not reason; it only standardizes content for the brain.

### 2. Cognition Layer (`layers/cognition.py`)
- **Role**: The decision engine (Brain).
- **Function**: Takes the current `Memory` and `Perception` state to decide **what to do next**.
- *Note*: In a production app, this would call OpenAI/Anthropic. Here, it uses a "Mock Intelligence" to simulate reasoning without API keys.

### 3. Action Layer (`layers/action.py`)
- **Role**: The execution unit (Hands).
- **Function**: Contains the actual tools (Calculator, File I/O). It blindly executes commands sent by the Cognition Layer. It is purely functional and has no "agency."

### 4. Memory Layer (`layers/memory.py`)
- **Role**: The storage unit.
- **Function**: Stores conversation history (Short-term) and could be extended for RAG/Vectors (Long-term).

---

## 🧠 Design Patterns
Patterns describe *how* independent layers are orchestrated to solve problems.

### The ReAct Pattern (`patterns/react_agent.py`)
**ReAct** stands for **Reason + Act**. 
Instead of just answering immediately, the agent enters a loop:
1.  **Perceive**: Read user input.
2.  **Think**: "Do I need a tool for this?"
3.  **Act**: If yes, execute the tool.
4.  **Observe**: Look at the tool output.
5.  **Repeat**: Feed the output back into the brain and decide again.

If we wanted to change the behavior (e.g., to "Plan-Execute"), we would only modify this `patterns` folder, leaving the `layers` untouched.

---

## 🚀 How to Run

1. Navigate to the folder:
   ```bash
   cd notebooks/architecture
   ```

2. Run the demonstration:
   ```bash
   # Linux/Mac/WSL
   python3 main.py
   
   # Windows
   python main.py
   ```

### What to Expect
The agent will automatically perform 3 scenarios:
1.  **Math**: "Calculate 120 + 25" (Demonstrates Tool Use)
2.  **Write**: "Save a note" (Demonstrates Side Effects)
3.  **Read**: "Read the note" (Demonstrates Feedback Loop)
