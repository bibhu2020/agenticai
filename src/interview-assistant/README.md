---
title: Interviewer Assistant
emoji: 👔
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Agentic AI for Resume Analysis & Interview Prep
---

# 👔 Interviewer Assistant

A **Multi-Agent System** designed to assist HR and technical interviewers by automatically analyzing job descriptions and resumes to generate tailored interview questions and fitness scores.

## 🚀 Features

- **🧠 Multi-Agent Swarm**:
  - **Job Analyst**: Extracts key requirements from JDs.
  - **Candidate Profiler**: Analyzes resumes for strengths and gaps.
  - **Evaluator**: Scores candidates on Technical, Behavioral, and Leadership metrics.
  - **Interview Designer**: Generates bespoke interview questions.
- **📄 Input Flexibility**: Accepts raw text for JD and Resume/LinkedIn profile.
- **📊 Structured Evaluation**: Provides a clear score and justification.

## 🛠️ Architecture

```
src/interview-assistant/
├── app.py                  # Streamlit UI (Orchestrator)
├── teams/                  # Team Definitions
│   └── team.py             # GroupChat Configuration
├── aagents/                # Agent Definitions
│   ├── job_analyst.py      
│   ├── candidate_profiler.py
│   ├── evaluator.py
│   ├── interview_designer.py 
│   └── admin.py            
└── Dockerfile              # Deployment Configuration
```

## 📦 Startup

### Local Run

1. **Install Dependencies**:
   ```bash
   pip install -r src/interviewer-assistant/requirements.txt
   ```

2. **Run Application**:
   ```bash
   streamlit run src/interviewer-assistant/app.py
   ```
   The app will open at `http://localhost:8501`.

## 🐳 Docker / Deployment

The project is packaged for **Hugging Face Spaces** (Docker SDK).

```bash
# Build
docker build -t interviewer-assistant -f src/interviewer-assistant/Dockerfile .

# Run
docker run -p 7860:7860 interviewer-assistant
```