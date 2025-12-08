---
title: Healthcare RAG Chatbot
emoji: 🤖
colorFrom: green
colorTo: indigo
sdk: docker
sdk_version: "0.0.1"
app_file: app.py
pinned: false
---

# Healthcare RAG Chatbot

A Streamlit-based healthcare chatbot that uses RAG (Retrieval-Augmented Generation) combined with web search to provide comprehensive medical information.

## Features

- 🏥 **Healthcare Information Retrieval**: Get accurate healthcare information from knowledge base and web
- 📚 **RAG Search**: Primary search through medical knowledge base
- 🌐 **Web Search Fallback**: DuckDuckGo search when knowledge base doesn't have information
- 💬 **Conversation Memory**: Maintains context across the conversation
- 📝 **Source Citations**: Clear indication of information source (Knowledge Base vs Web Search)
- 📥 **Export Conversations**: Export chat history in text, markdown, or JSON format
- 🎨 **Modern UI**: Clean, professional chat interface with message bubbles

## Architecture

```
src/healthcare-rag-chatbot/
├── app.py          # Streamlit UI
├── chat.py         # Chat management & memory
└── README.md       # This file
```

The chatbot integrates with:
- `common/aagents/healthcare_agent.py` - Healthcare RAG agent
- `common/mcp/tools/rag_tool.py` - RAG search tool
- `common/mcp/tools/search_tools.py` - DuckDuckGo search tool

## How It Works

1. **User asks a question** → Sent to healthcare agent
2. **Agent calls `rag_search`** → Searches medical knowledge base
3. **If RAG has info** → Returns with "Knowledge Base" citation
4. **If RAG fails** → Agent automatically calls `duckduckgo_search`
5. **If web search succeeds** → Returns with "Web Search" citation
6. **If both fail** → Returns "no information available" message

## Running the Application

### Prerequisites

- Python 3.12
- Virtual environment activated
- Required dependencies installed (see `pyproject.toml`)

### Start the App

```bash
# From project root
cd src/healthcare-rag-chatbot
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Ask Questions

Simply type your healthcare question in the input box and click "Send". Examples:
- "What is diabetes?"
- "What are the symptoms of hypertension?"
- "What is HL7?"

### View Tool Usage

The chatbot shows which tools were used for each response via badges:
- 🔧 `rag_search` - Searched knowledge base
- 🔧 `duckduckgo_search` - Searched the web

### Export Conversations

1. Click "Export Chat" in the sidebar
2. Select format (text, markdown, or JSON)
3. Click "Download" to save the conversation

### Clear History

Click "🗑️ Clear Conversation" in the sidebar to start fresh.

## Configuration

The chatbot uses:
- **Model**: Gemini 2.0 Flash (via OpenAI-compatible API)
- **Knowledge Base**: Medical documents in RAG system
- **Web Search**: DuckDuckGo (no API key required)

Environment variables are loaded from `.env` in the project root.

## Medical Disclaimer

⚠️ **Important**: This chatbot provides information for educational purposes only. Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment.

## Technical Details

### Chat Manager (`chat.py`)

- Manages conversation history with timestamps
- Handles async agent interactions
- Tracks tool usage and metadata
- Provides export functionality

### Streamlit UI (`app.py`)

- Modern chat interface with message bubbles
- Session state management
- Tool call visualization
- Responsive design with custom CSS

### Healthcare Agent

The agent follows strict rules:
- NEVER uses pre-trained knowledge
- ALWAYS calls `rag_search` first
- MUST call `duckduckgo_search` if RAG fails
- Only provides information from tools
- Includes source citations and disclaimers