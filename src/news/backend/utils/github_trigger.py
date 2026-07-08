"""Admin-triggered GitHub Actions control: force-run the daily news agent, check its status."""
from __future__ import annotations
import os

from github import Github

REPO = "bibhu2020/agenticai"
WORKFLOW_FILE = "news-agent-daily.yml"
BRANCH = "main"


def _get_workflow():
    token = os.environ.get("NEWS_TRIGGER_GH_TOKEN", "")
    if not token:
        raise RuntimeError("NEWS_TRIGGER_GH_TOKEN is not set")
    repo = Github(token).get_repo(REPO)
    return repo.get_workflow(WORKFLOW_FILE)


def trigger_agent_run() -> bool:
    """Fire a workflow_dispatch event on the daily news agent workflow."""
    workflow = _get_workflow()
    return workflow.create_dispatch(ref=BRANCH)


def get_last_run_status() -> dict:
    """Return status of the most recent run of the daily news agent workflow."""
    workflow = _get_workflow()
    runs = workflow.get_runs()
    if runs.totalCount == 0:
        return {"status": "unknown", "conclusion": None, "created_at": None, "html_url": None}
    run = runs[0]
    return {
        "status": run.status,
        "conclusion": run.conclusion,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "html_url": run.html_url,
    }
