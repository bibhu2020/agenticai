# Agentic AI Projects
This is a collection of agentic AI projects. Every project has its own project folder with its project specific configurations and environment variable settings. However, they all share the same common python virtual environment.

## Folder Structure
```
agenticaiproject/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env
├── .gitignore
│
├── _notebooks/ --> contains ipynb files mostly on prompt engineering.
├── github/
│   ├── workflows/ --> it has the ci/cd pipelines that deploy the application into Hugging Face.
├── accessibility/
├── chatbot/
├── deep-research/
├── mcp-servers/  --> it has a list of mcp servers that are shared by the projects
├── stock-advisor/
├── trip-planner/

```
## Hugging Face URLs

- accessibility: In Progress
- chatbot: https://mishrabp-chatbot-app.hf.space
- deep-research: https://mishrabp-deep-research.hf.space
- stock-advisor: TBD
- trip-planner: https://mishrabp-trip-advisor-app.hf.space/


## How to setup locally

- You must have python and uv packag managed installed on your PC.

- Run `uv sync` command to create the virtual environment and install the required packages listed in pyproject.toml.

- Activate the virtual environment `source .venv/bin/activate`.

- Now, you can navigate to each project folder and create an .env file.

- Setup all the environment variables listed in .env.name file in .env file.

- Run `python run.py` 
