
"""
GitHub MCP Server
"""
import sys
import os
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from core.mcp_telemetry import log_usage, log_trace, log_metric
import uuid
import time
import datetime

# Add src to pythonpath
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
if src_dir not in sys.path:
    sys.path.append(src_dir)

try:
    from github import Github, Auth
    from github.GithubException import GithubException
except ImportError:
    Github = None
    Auth = None
    GithubException = Exception

# Initialize FastMCP Server
mcp = FastMCP("GitHub Operations", host="0.0.0.0")

def get_client():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set.")
    if not Github:
        raise ImportError("PyGithub not installed.")
    auth = Auth.Token(token)
    return Github(auth=auth)

@mcp.tool()
def list_repositories() -> List[Dict[str, Any]]:
    """
    List all repositories for the authenticated user/owner.
    """
    start_time = time.time()
    trace_id = str(uuid.uuid4())
    span_id = str(uuid.uuid4())
    log_usage("mcp-github", "list_repositories")
    
    try:
        g = get_client()
        # Get repos for the owner/authenticated user
        repos = g.get_user().get_repos(sort="updated", direction="desc")
        
        results = []
        for repo in repos[:20]: # Limit to 20 most recent
            results.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "updated_at": str(repo.updated_at),
                "language": repo.language
            })
        
        duration = (time.time() - start_time) * 1000
        log_trace("mcp-github", trace_id, span_id, "list_repositories", duration, "ok")
        log_metric("mcp-github", "repos_fetched", len(results), {"status": "ok"})
        return results
        
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_trace("mcp-github", trace_id, span_id, "list_repositories", duration, "error")
        return [{"error": str(e)}]

@mcp.tool()
def list_issues(owner: str, repo_name: str, state: str = "open") -> List[Dict[str, Any]]:
    """
    List issues for a repository.
    """
    log_usage("mcp-github", "list_issues")
    try:
        g = get_client()
        repo = g.get_repo(f"{owner}/{repo_name}")
        issues = repo.get_issues(state=state)
        
        results = []
        for issue in issues[:10]: # Limit to 10 recent
            results.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "created_at": str(issue.created_at),
                "user": issue.user.login
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def create_issue(owner: str, repo_name: str, title: str, body: str) -> Dict[str, Any]:
    """
    Create a new issue.
    """
    log_usage("mcp-github", "create_issue")
    try:
        g = get_client()
        repo = g.get_repo(f"{owner}/{repo_name}")
        issue = repo.create_issue(title=title, body=body)
        return {
            "number": issue.number,
            "title": issue.title,
            "url": issue.html_url
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_issue(owner: str, repo_name: str, issue_number: int) -> Dict[str, Any]:
    """
    Get detailed issue info including comments.
    """
    log_usage("mcp-github", "get_issue")
    try:
        g = get_client()
        repo = g.get_repo(f"{owner}/{repo_name}")
        issue = repo.get_issue(issue_number)
        
        comments = []
        for c in issue.get_comments():
            comments.append({
                "user": c.user.login,
                "body": c.body,
                "created_at": str(c.created_at)
            })
            
        return {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "state": issue.state,
            "comments": comments
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def list_security_alerts(owner: str, repo_name: str) -> List[Dict[str, Any]]:
    """
    List dependabot alerts (if enabled and accessible).
    """
    try:
        g = get_client()
        repo = g.get_repo(f"{owner}/{repo_name}")
        
        # PyGithub support for alerts varies, using common method if available
        # or manual requests otherwise. Assuming PyGithub >= 2.0 has some support.
        # Often requires specific permissions.
        try:
            alerts = repo.get_dependabot_alerts()
            results = []
            for alert in alerts:
                results.append({
                    "number": alert.number,
                    "package": alert.dependency.package.name,
                    "severity": alert.security_advisory.severity,
                    "state": alert.state,
                    "created_at": str(alert.created_at)
                })
            return results
        except AttributeError:
             return [{"error": "get_dependabot_alerts not supported by this PyGithub version"}]
             
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def create_pull_request(owner: str, repo_name: str, title: str, body: str, head: str, base: str = "main") -> Dict[str, Any]:
    """
    Create a new Pull Request.
    """
    try:
        g = get_client()
        repo = g.get_repo(f"{owner}/{repo_name}")
        pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return {
            "number": pr.number,
            "title": pr.title,
            "url": pr.html_url,
            "state": pr.state
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_pull_request(owner: str, repo_name: str, pr_number: int) -> Dict[str, Any]:
    """
    Get Pull Request details.
    """
    try:
        g = get_client()
        repo = g.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(pr_number)
        return {
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "state": pr.state,
            "merged": pr.merged,
             "url": pr.html_url
        }
    except Exception as e:
         return {"error": str(e)}

@mcp.tool()
def list_workflow_runs(owner: str, repo_name: str) -> List[Dict[str, Any]]:
    """
    List recent workflow runs for a repository.
    """
    log_usage("mcp-github", "list_workflow_runs")
    try:
        g = get_client()
        repo = g.get_repo(f"{owner}/{repo_name}")
        runs = repo.get_workflow_runs()
        
        results = []
        for run in runs[:10]:
            results.append({
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "event": run.event,
                "created_at": str(run.created_at),
                "url": run.html_url
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_workflow_run_details(owner: str, repo_name: str, run_id: int) -> Dict[str, Any]:
    """
    Get details of a specific workflow run.
    """
    log_usage("mcp-github", "get_workflow_run_details")
    try:
        g = get_client()
        repo = g.get_repo(f"{owner}/{repo_name}")
        run = repo.get_workflow_run(run_id)
        
        return {
            "id": run.id,
            "name": run.name,
            "status": run.status,
            "conclusion": run.conclusion,
            "event": run.event,
            "created_at": str(run.created_at),
            "updated_at": str(run.updated_at),
            "url": run.html_url,
            "run_number": run.run_number
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import os
    if os.environ.get("MCP_TRANSPORT") == "sse":
        import uvicorn
        port = int(os.environ.get("PORT", 7860))
        uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=port)
    else:
        mcp.run()
