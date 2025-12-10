---
title: Literature Review Assistant
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "0.0.1"
app_file: app.py
pinned: false
license: mit
short_description: A multi-agent AI researcher (autogen)
---

# 📚 Literature Review Assistant

A multi-agent AI application that conducts automatic literature reviews on any topic using Arxiv.

## Features

- **🔍 Automated Paper Search**: Searches Arxiv for relevant research papers based on your topic.
- **🤖 Multi-Agent Collaboration**: 
    - **Search Agent**: Smartly queries Arxiv to find the most relevant papers.
    - **Summarizer Agent**: synthesizes findings into a concise, readable review.
- **📄 Extractive Summarization**: Generates summaries with titles, authors, key contributions, and takeaways.
- **⚛️ AutoGen Powered**: Built using the `autogen-agentchat` and `autogen-ext` libraries.
- **🖥️ Real-time UI**: Streamlit interface to watch the agents collaborate in real-time.

## Architecture

The project consists of a frontend and a backend logic module:

```
src/literature-review/
├── app.py          # Streamlit frontend
├── backend.py      # AutoGen agents and workflow logic
└── Dockerfile      # Container configuration
```

### Core Components (`backend.py`)
- **`arxiv_search` Tool**: Uses the `arxiv` Python library to fetch paper metadata.
- **`search_agent`**: An `AssistantAgent` that formulates queries and selects papers.
- **`summarizer`**: An `AssistantAgent` that turns raw paper data into a structured Markdown report.
- **`RoundRobinGroupChat`**: Orchestrates the conversation between the two agents.

## Running the Application

### Prerequisites
- Python 3.10+
- OpenAI API Key (configured in environment or `.env`)

### Local Setup

1. **Navigate to the project directory**:
   ```bash
   cd src/literature-review
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # OR if using uv/poetry
   uv sync
   ```
   *(Note: Ensure you have `streamlit`, `autogen-agentchat`, `autogen-ext`, `arxiv`, and `python-dotenv` installed)*

3. **Set up Environment Variables**:
   Create a `.env` file in the root or `src/literature-review` directory:
   ```env
   OPENAI_API_KEY=sk-...
   ```

4. **Run the Streamlit App**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Enter a **Research Topic** (e.g., "Large Language Models for Healthcare").
2. Select the **Number of Papers** to review.
3. Click **Search**.
4. Watch as the agents find papers and generate your literature review in real-time!