# Interview Assistant Implementation Plan

## 1. Overview
The Interview Assistant is a RAG-powered multi-agent system designed to streamline the recruitment process. It allows interviewers to upload candidate resumes, analyze them against specific job descriptions, and generate tailored interview questions.

We will use **`autogen-agentchat`** to orchestrate the multi-agent workflow for resume analysis, fitness evaluation, and interview design.

## 2. Architecture

### High-Level Components
1.  **Streamlit App**: Serves as both the UI and the control layer.
2.  **RAG Engine (ChromaDB)**: Stores vector embeddings of candidate resumes.
3.  **Session DB (SQLite)**: Stores structured application state.
4.  **Agentic Core**: `autogen-agentchat` agents:
    *   **Evaluation Team**: `JD_Summarizer`, `Resume_Summarizer`, `Evaluator`, `Coordinator`.
    *   **Interview Team**: `Interview_Strategist`, `Question_Generator`, `Question_Reviewer`.
    *   **Tools**: `search_candidate_knowledge_base`.

### Persistence & Reset
*   The app checks **SQLite** on startup. If a session exists, it loads the Dashboard view immediately.
*   **"New Interview" Button**: Clears both ChromaDB collections and the SQLite tables to start fresh.

### Agent Workflow
*   **UserProxy**: Configured to allow human input if needed, but primarily acts as the bridge for the Streamlit app.
*   **ResumeAnalyst**: Queries the RAG system to evaluate candidates against the Job Description.
*   **Interviewer**: Generates specific questions based on the Analyst's report.

## 3. Technology Stack
*   **UI & Server**: Streamlit (Python).
*   **AI/ML**:
    *   **Framework**: `autogen-agentchat` (Microsoft AutoGen).
    *   **Vector DB**: ChromaDB (Local persistent).
    *   **Orchestration**: Agents will access ChromaDB via registered tools (`register_function`).
    *   **Embeddings**: OpenAI or compatible (SentenceTransformers).
    *   **LLM**: Ollama (Gemma 3 4B) hosted on Ollama Cloud.

## 4. Directory Structure
```text
src/interview-assistant/
├── app.py                 # Streamlit Entry point (Main UI)
├── agents/                # Agent Definitions
│   ├── __init__.py
│   └── definitions.py     # JD_Summarizer, Resume_Summarizer, Evaluator, Coordinator
├── teams/                 # Team Orchestration
│   ├── __init__.py
│   └── evaluation_team.py # Evaluation Workflow (RoundRobin)
├── data/                  # Persistent Storage (SQlite + ChromaDB)
├── rag/                   # Retrieval Augmented Generation
│   ├── __init__.py
│   ├── db.py              # ChromaDB Interface
│   └── ingest.py          # PDF/Text Parsing & Chunking
└── implementation.md      # This file
```

## 5. User Flows & Implementation Strategy

### Flow 1: Ingestion & Dashboard (✅ Completed)
**Objective**: Upload data and prepare the workspace.
*   **Input**:
    *   File Uploader (Multiple PDFs).
    *   Job Description (Text Area).
    *   "Submit" Button.
*   **System Action**:
    *   Parse PDFs and ingest into **ChromaDB** with metadata (`name`, `filename`).
    *   Store JD in session state.
    *   Initialize the **Candidate Grid**.
*   **Output**: A data grid displaying discovered candidates. Columns: `[Select]`, `Name`, `Status` (Pending/Evaluated), `Score`, `Actions`.

### Flow 2: On-Demand Evaluation (✅ Completed)
**Objective**: Multi-Agent analysis of specific candidates.
*   **Input**: User clicks "Evaluate" on a specific candidate row.
*   **System Action**:
    *   **Evaluation Team** (`RoundRobinGroupChat`) is triggered in `src/interview-assistant/teams/evaluation_team.py`.
    *   **JD_Summarizer**: Extracts key criteria.
    *   **Resume_Summarizer**: Fetches resume evidence from RAG.
    *   **Evaluator**: Scores and analyzes.
    *   **Coordinator**: Validates JSON output.
    *   **Output**: Updates the grid data with `Fitness Score`, `Strengths`, `Weaknesses` in SQLite.
*   **Output**: The grid refreshes to show the new data with progress bars.

### Flow 3: Interview Design Studio (✅ Completed)
**Objective**: Interactive question generation and revision.
*   **Trigger**: User selects a candidate (who is evaluated) and enters the "Interview Studio".
*   **Interface**: 
    *   "Generate Interview Guide" Button (One-click generation).
    *   Chat Interface for **Revision** (e.g., "Make technical questions harder").
*   **System Action**:
    *   **Interview Generation Team** (`teams/interview_team.py`):
        *   **Interview_Strategist**: Sets weights (Tech/Leadership/Behavioral) based on candidate profile.
        *   **Question_Generator**: Creates 20 questions.
        *   **Question_Reviewer**: Validates output.
    *   **Revision Flow**: Updates existing questions based on user feedback.
*   **Output**:
    *   Interactive Expandable List of Questions.
    *   JSON Download.
    *   Persistence in SQLite for session reloading.

## 6. Implementation Steps

### Phase 1: Core & RAG (✅ Done)
1.  **Frontend**: Build the layout in `app.py`.
2.  **RAG**: Implement `ingest_resumes(files)` to populate ChromaDB.
3.  **Persistence**: SQLite database for session state.

### Phase 2: Evaluation Agent (✅ Done)
1.  Define agents in `agents/definitions.py`.
2.  Implement `run_evaluation_team` in `teams/evaluation_team.py`.
3.  Connect "Evaluate" button in UI to the team runner.

### Phase 3: Interview Chat & PDF (✅ Done)
1.  **Interview Agents**: Created `Interview_Strategist`, `Question_Generator`, `Question_Reviewer` in `agents/definitions.py`.
2.  **Team Helper**: Created `teams/interview_team.py` with `run_interview_generation_team` and `run_interview_revision`.
3.  **App Integration**: Integrated Generation and Revision flows in `render_studio` in `app.py`.
4.  **Persistence**: Added `questions` column to SQLite schema for saving state.
5.  **PDF Generation**: (Pending: PDF Export logic is currently JSON-only, PDF button is a placeholder).
