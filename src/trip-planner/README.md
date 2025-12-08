---
title: AI Trip Planner API
emoji: 🌍
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# AI Trip Planner API
This is an AI Agentic Trip Planner for planning a trip to any country worldwide with real-time data. It's going to have the 
following features:
- Real-time weather info
- Attraction and Activity List
- Hotel Costs
- Currency Conversion
- Itenary Planning
- Total Expenses
- Summerizer

## Create Project
```
uv init ai-trip-planner
```

## Create a virtual environment - option1
uv is like npm in nodejs. uv is created using RUST language.
```
uv python list

uv python install cpython-3.11.12-linux-x86_64-gnu 

uv venv .venv --python=cpython-3.11.12-linux-x86_64-gnu

source .venv/bin/activate

deactivate
```

## Create a virtual environment - option2
uv is like npm in nodejs. uv is created using RUST language.
```
uv python list

conda create --prefix /home/azureuser/ws/agenticai/projects/ai-trip-planner/.venv python=3.11 -y

conda activate /home/azureuser/ws/agenticai/projects/ai-trip-planner/.venv

conda deactivate 
```

## Install the packages
```
uv pip install -r requirements.txt

uv pip list
```

## Run the app
```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

streamlit run streamlit_app.py
```