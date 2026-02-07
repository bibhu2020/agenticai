
"""
Azure SRE MCP Server
"""
import sys
import os
import logging
from typing import List, Dict, Any, Optional

# Add src to pythonpath
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from mcp.server.fastmcp import FastMCP
from mcp_telemetry import log_usage

# Azure Imports
try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.monitor import MonitorManagementClient
    from azure.mgmt.compute import ComputeManagementClient
    from azure.monitor.query import LogsQueryClient
except ImportError:
    # Allow running without Azure SDKs installed (for testing/mocking)
    DefaultAzureCredential = None
    ResourceManagementClient = None
    MonitorManagementClient = None
    ComputeManagementClient = None
    LogsQueryClient = None

# Initialize Server
mcp = FastMCP("Azure SRE")

# Helper to get credential
def get_credential():
    if not DefaultAzureCredential:
         raise ImportError("Azure SDKs not installed.")
    return DefaultAzureCredential()

@mcp.tool()
def list_resources(subscription_id: str, resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List Azure resources in a subscription or resource group.
    """
    log_usage("mcp-azure-sre", "list_resources")
    try:
        cred = get_credential()
        client = ResourceManagementClient(cred, subscription_id)
        
        if resource_group:
            resources = client.resources.list_by_resource_group(resource_group)
        else:
            resources = client.resources.list()
            
        return [{"name": r.name, "type": r.type, "location": r.location, "id": r.id} for r in resources]
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def restart_vm(subscription_id: str, resource_group: str, vm_name: str) -> str:
    """
    Restart a Virtual Machine.
    """
    log_usage("mcp-azure-sre", "restart_vm")
    try:
        cred = get_credential()
        client = ComputeManagementClient(cred, subscription_id)
        
        poller = client.virtual_machines.begin_restart(resource_group, vm_name)
        poller.result() # Wait for completion
        return f"Successfully restarted VM: {vm_name}"
    except Exception as e:
        return f"Error restarting VM: {str(e)}"

@mcp.tool()
def get_metrics(subscription_id: str, resource_id: str, metric_names: List[str]) -> List[Dict[str, Any]]:
    """
    Get metrics for a resource.
    """
    log_usage("mcp-azure-sre", "get_metrics")
    try:
        cred = get_credential()
        client = MonitorManagementClient(cred, subscription_id)
        
        # Default to last 1 hour
        metrics_data = client.metrics.list(
            resource_id,
            metricnames=",".join(metric_names),
            timespan="PT1H",
            interval="PT1M",
            aggregation="Average"
        )
        
        results = []
        for item in metrics_data.value:
            for timeseries in item.timeseries:
                for data in timeseries.data:
                    results.append({
                        "metric": item.name.value,
                        "timestamp": str(data.time_stamp),
                        "average": data.average
                    })
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def analyze_logs(workspace_id: str, query: str) -> List[Dict[str, Any]]:
    """
    Execute KQL query on Log Analytics Workspace.
    """
    try:
        cred = get_credential()
        client = LogsQueryClient(cred)
        
        response = client.query_workspace(workspace_id, query, timespan="P1D")
        
        if response.status == "Success":
            # Convert table to list of dicts
            results = []
            for table in response.tables:
                columns = table.columns
                for row in table.rows:
                    results.append(dict(zip(columns, row)))
            return results
        else:
             return [{"error": "Query failed"}]
             
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def check_health(subscription_id: str, resource_group: str) -> Dict[str, str]:
    """
    Perform a health check on key resources in a resource group.
    Checks status of VMs.
    """
    try:
        cred = get_credential()
        compute_client = ComputeManagementClient(cred, subscription_id)
        
        vms = compute_client.virtual_machines.list(resource_group)
        health_status = {}
        
        for vm in vms:
            # Get instance view for power state
            instance_view = compute_client.virtual_machines.instance_view(resource_group, vm.name)
            statuses = [s.display_status for s in instance_view.statuses if s.code.startswith('PowerState')]
            health_status[vm.name] = statuses[0] if statuses else "Unknown"
            
        return health_status
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
