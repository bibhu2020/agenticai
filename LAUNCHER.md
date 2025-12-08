# Universal App Launcher

A convenient launcher script to run any Streamlit application in the `src/` directory.

## Usage

### List Available Apps

```bash
python run.py --list
```

### Launch an App

```bash
python run.py <app_name>
```

### Launch on Custom Port

```bash
python run.py <app_name> --port 8502
```

## Available Applications

| App Name | Description | Location |
|----------|-------------|----------|
| `healthcare` | Healthcare RAG Chatbot - Medical information with RAG and web search | `src/healthcare-rag-chatbot` |
| `deep-research` | Deep Research AI - Comprehensive research assistant | `src/deep-research/ui` |
| `stock-advisor` | Stock Advisor - Financial analysis and stock recommendations | `src/stock-advisor/ui` |
| `travel-agent` | Travel Agent - Trip planning and travel recommendations | `src/travel-agent/ui` |
| `trip-planner` | Trip Planner - Detailed trip itinerary planning | `src/trip-planner/app` |
| `chatbot` | General Chatbot - Multi-purpose conversational AI | `src/chatbot/ui` |
| `accessibility` | Accessibility Tools - Assistive technology applications | `src/accessibility` |

## Examples

```bash
# Launch healthcare chatbot
python run.py healthcare

# Launch deep research on port 8502
python run.py deep-research --port 8502

# Launch stock advisor
python run.py stock-advisor

# Show help
python run.py --help
```

## Features

- ✅ Single entry point for all apps
- ✅ Auto-discovery of app locations
- ✅ Custom port configuration
- ✅ Descriptive app registry
- ✅ Error handling and validation
- ✅ Clean, user-friendly interface

## Adding New Apps

To add a new app to the launcher, edit `run.py` and add an entry to the `APP_REGISTRY`:

```python
APP_REGISTRY = {
    # ... existing apps ...
    "my-new-app": {
        "path": "src/my-new-app",
        "entry": "app.py",
        "description": "My New App - Description here"
    }
}
```

## Requirements

- Python 3.12+
- Streamlit installed in your virtual environment
