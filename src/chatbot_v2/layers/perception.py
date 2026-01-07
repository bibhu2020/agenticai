import json
import os
import datetime
from dataclasses import dataclass
from openai import OpenAI

@dataclass
class EnvironmentState:
    user_input: str
    timestamp: str
    source: str

class PerceptionLayer:
    """
    The 'Sensors' of the agent. 
    Responsibility: Accept raw data, clean it, validate it (Guardrails), and package it.
    """
    
    def __init__(self):
         api_key = os.environ.get("OPENAI_API_KEY")
         self.client = OpenAI(api_key=api_key) if api_key else None
         self.model_name = "gpt-4o"
    
    def perceive(self, raw_text: str, source: str = "user_input") -> EnvironmentState:
        # 1. Basic Cleaning
        clean_text = raw_text.strip()
        
        # 2. Guardrail Check (Input Validation)
        # We run this BEFORE accepting the input into the system state.
        if self.client and clean_text:
            validation = self._run_guardrail(clean_text)
            if not validation["is_valid"]:
                raise ValueError(f"Guardrail tripped: {validation['reasoning']}")

        return EnvironmentState(
            user_input=clean_text,
            timestamp=datetime.datetime.now().isoformat(),
            source=source
        )

    def _run_guardrail(self, text: str) -> dict:
        """
        Validates if logic contains unparliamentary language.
        """
        system_prompt = """
        You are a highly efficient Guardrail Agent. 
        
        **Goal**: Validate that the user input is safe and polite.
        
        **PASS / VALID Criteria**:
        - The input is technical, professional, or casual.
        - The input contains complex instructions, code features, or formatting instructions.
        - The input is a valid request for information or action.
        
        **FAIL / INVALID Criteria**:
        - The input contains HATE SPEECH, EXPLICIT PROFANITY, or THREATS.
        - The input is aggressive, insulting, or unparliamentary.
        
        **Output Format**:
        Return JSON only: { "is_valid": boolean, "reasoning": string }
        
        If unsure, lean towards VALID.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            # On failure, fail open or closed? Let's log and allow for now to prevent blocking on API errors.
            print(f"Guardrail check failed: {e}")
            return {"is_valid": True, "reasoning": "Guardrail check failed, allowing input."}
