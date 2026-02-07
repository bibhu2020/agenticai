
"""
GitHub MCP Server
"""
import sys
import os
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from mcp_telemetry import log_usage

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
mcp = FastMCP("GitHub Operations")

def get_client():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set.")
    if not Github:
        raise ImportError("PyGithub not installed.")
    auth = Auth.Token(token)
    return Github(auth=auth)

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

if __name__ == "__main__":
    mcp.run()
