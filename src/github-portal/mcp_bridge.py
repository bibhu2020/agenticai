
import asyncio
import os
from mcp import ClientSession
from mcp.client.sse import sse_client
from agents import function_tool
from typing import List, Dict, Any, Optional

class MCPGitHubBridge:
    def __init__(self, sse_url: str = "https://mishrabp-mcp-github.hf.space/sse"):
        self.sse_url = sse_url
        self.session: Optional[ClientSession] = None
        self._exit_stack = None
        self._tools_cache = {}

    async def connect(self):
        """Connect to the remote MCP server via SSE."""
        from contextlib import AsyncExitStack
        import traceback
        
        try:
            self._exit_stack = AsyncExitStack()
            
            # Connect to server
            print(f"DEBUG: Attempting to connect to {self.sse_url}")
            streams = await self._exit_stack.enter_async_context(sse_client(self.sse_url))
            self.session = await self._exit_stack.enter_async_context(ClientSession(streams[0], streams[1]))
            
            # Initialize
            print("DEBUG: Initializing session...")
            await self.session.initialize()
            
            # Discover tools
            print("DEBUG: Listing tools...")
            response = await self.session.list_tools()
            self._tools_cache = {t.name: t for t in response.tools}
            print(f"DEBUG: Connected successfully. Found {len(self._tools_cache)} tools.")
            return self._tools_cache
        except Exception as e:
            print(f"DEBUG: Connection failed error: {str(e)}")
            traceback.print_exc()
            if self._exit_stack:
                await self._exit_stack.aclose()
            raise e

    async def call_tool(self, name: str, arguments: Dict[str, Any]):
        """Call a tool on the remote MCP server."""
        if not self.session:
            raise RuntimeError("MCP Bridge not connected. Call connect() first.")
        
        result = await self.session.call_tool(name, arguments)
        return result.content

    async def disconnect(self):
        """Disconnect from the server."""
        if self._exit_stack:
            await self._exit_stack.aclose()

# Global bridge instance
bridge = MCPGitHubBridge()

# Specific tools exposed for the Agent
# We wrap them to make them easy for the Agent to call

@function_tool
async def list_issues(owner: str, repo_name: str, state: str = "open") -> str:
    """List issues for a repository."""
    try:
        if not bridge.session: await bridge.connect()
        content = await bridge.call_tool("list_issues", {"owner": owner, "repo_name": repo_name, "state": state})
        return str(content)
    except Exception as e:
        return f"Error: {str(e)}"

@function_tool
async def get_issue(owner: str, repo_name: str, issue_number: int) -> str:
    """Get detailed issue info including comments."""
    try:
        if not bridge.session: await bridge.connect()
        content = await bridge.call_tool("get_issue", {"owner": owner, "repo_name": repo_name, "issue_number": issue_number})
        return str(content)
    except Exception as e:
        return f"Error: {str(e)}"

@function_tool
async def list_security_alerts(owner: str, repo_name: str) -> str:
    """List security alerts (Dependabot)."""
    try:
        if not bridge.session: await bridge.connect()
        content = await bridge.call_tool("list_security_alerts", {"owner": owner, "repo_name": repo_name})
        return str(content)
    except Exception as e:
        return f"Error: {str(e)}"

@function_tool
async def list_workflow_runs(owner: str, repo_name: str) -> str:
    """List recent CI/CD workflow runs."""
    try:
        if not bridge.session: await bridge.connect()
        content = await bridge.call_tool("list_workflow_runs", {"owner": owner, "repo_name": repo_name})
        return str(content)
    except Exception as e:
        return f"Error: {str(e)}"

@function_tool
async def get_workflow_run_details(owner: str, repo_name: str, run_id: int) -> str:
    """Get status and details of a specific workflow run."""
    try:
        if not bridge.session: await bridge.connect()
        content = await bridge.call_tool("get_workflow_run_details", {"owner": owner, "repo_name": repo_name, "run_id": run_id})
        return str(content)
    except Exception as e:
        return f"Error: {str(e)}"

def get_github_tools():
    return [list_issues, get_issue, list_security_alerts, list_workflow_runs, get_workflow_run_details]
