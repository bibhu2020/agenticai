### Setting up .venv
```bash
conda create --prefix /home/azureuser/ws/agenticai/projects/ai-stock-advisor/.venv python=3.11 -y

conda activate /home/azureuser/ws/agenticai/projects/ai-stock-advisor/.venv

conda deactivate 

uv pip install -r requirements.txt
```

### Run Unit Tests
```bash
pytest -v tests/test_data_agent.py

python -m pytest -v

```