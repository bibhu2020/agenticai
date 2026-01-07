from src.accessibility_v2.tools.web_auditor import WebAuditor
from typing import Dict, Any

class ActionLayer:
    """
    Executes the accessibility audit.
    """
    def __init__(self):
        self.auditor = WebAuditor()

    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action == "audit_url":
            url = params.get("url")
            if not url:
                return {"error": "No URL provided"}
            
            print(f"[Action] Auditing {url}...")
            return await self.auditor.full_audit(url)
        
        return {"error": f"Unknown action: {action}"}
