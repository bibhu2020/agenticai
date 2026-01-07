import json
import os
from openai import AsyncOpenAI

class CognitionLayer:
    """
    Analyzes audit data and generates readable reports.
    """
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = "gpt-4o"

    async def analyze(self, audit_data: dict) -> str:
        """
        Takes raw audit JSON and produces a markdown summary with recommendations.
        """
        if not audit_data.get("success"):
             return f"❌ Audit Failed: {audit_data.get('error')}"
             
        summary_json = json.dumps(audit_data.get("data", {}).get("summary", {}), indent=2)
        
        system_prompt = """
        You are an **Accessibility Expert** (WCAG 2.1 AA Specialist).
        You will receive a JSON summary of accessibility violations found on a webpage.
        
        Your Goal:
        1. Summarize the key issues.
        2. Explain WHY they are barriers to users (e.g. screen readers, low vision).
        3. Provide actionable code snippets or recommendations to fix them.
        
        Ouput Format:
        Markdown. Use tables for lists of violations.
        """
        
        try:
             completion = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Audit Data:\n{summary_json}"}
                ]
            )
             return completion.choices[0].message.content
        except Exception as e:
            return f"Error analyzing results: {e}"
