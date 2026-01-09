# Deep Research v2 (LangGraph Edition)

This is a port of the Deep Research app to use **LangGraph** for orchestration.

## Architecture

The application uses a graph-based agentic workflow:

1.  **Planner Node**: Decomposes the query into a list of web search queries.
2.  **Search Node**: Executes the planned searches using the Google Serper API.
3.  **Writer Node**: Synthesizes the search results into a comprehensive report.

## Setup

1.  Ensure you have the required dependencies (LangGraph, LangChain, Streamlit, etc.).
2.  Set up your environment variables (create a `.env` file or export them):
    -   `OPENAI_API_KEY`
    -   `SERPER_API_KEY`

## Running

Run the Streamlit app:

```bash
streamlit run src/deep-research_v2/app.py
```
