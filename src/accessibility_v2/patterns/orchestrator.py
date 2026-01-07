from src.accessibility_v2.layers.perception import PerceptionLayer
from src.accessibility_v2.layers.action import ActionLayer
from src.accessibility_v2.layers.cognition import CognitionLayer

class AccessibilityOrchestrator:
    def __init__(self):
        self.perception = PerceptionLayer()
        self.action = ActionLayer()
        self.cognition = CognitionLayer()

    async def audit_site(self, url: str):
        # 1. Perception
        state = self.perception.perceive(url)
        if not state.is_valid_url:
            yield f"❌ Invalid URL: {state.url}"
            return

        # 2. Action (Run Audit)
        yield f"🔍 Auditing {state.url}..."
        audit_result = await self.action.execute("audit_url", {"url": state.url})
        
        if not audit_result.get("success"):
            yield f"❌ Audit failed: {audit_result.get('error')}"
            return

        # 3. Cognition (Analyze)
        yield "🧠 Analyzing results with AI..."
        analysis = await self.cognition.analyze(audit_result)
        
        yield analysis
