import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load .env from project root
# current file: notebooks/architecture/layers/cognition.py
# root: ../../../
root_path = Path(__file__).parent.parent.parent.parent
load_dotenv(root_path / ".env")

class CognitiveOutput:
    def __init__(self, thought: str, action: Optional[str] = None, action_input: Optional[Dict] = None, final_answer: Optional[str] = None):
        self.thought = thought
        self.action = action
        self.action_input = action_input
        self.final_answer = final_answer

class CognitionLayer:
    """
    The 'Brain' of the agent.
    Responsibility: Reason about the state and decide the next move.
    Now uses an LLM (OpenAI GPT-4o) to make decisions.
    """
    
    def __init__(self):
        # Setup OpenAI client
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not found. Agent will fail.")
            
        self.client = OpenAI(api_key=api_key)
        self.model_name = "gpt-4o"
        
        self.system_prompt = """
You are an intelligent agent designed to help users with calculations and file notes.
You have access to the following tools:
1. calculate(expression: str): Evaluates a mathematical expression (e.g., "120 + 25").
2. save_note(filename: str, content: str): Saves text to a file.
3. read_note(filename: str): Reads the content of a file.

Instructions:
- Analyze the user request and the conversation history.
- Decide if you need to use a tool or if you can answer directly.
- You must output valid JSON only, matching this structure:
{
  "thought": "Your reasoning process here.",
  "action": "name_of_tool_or_null",
  "action_input": { "arg_name": "value" } or null,
  "final_answer": "Your final response to the user" or null
}
- If you use a tool, 'action' must be the tool name, and 'final_answer' must be null.
- If you are finished or just chatting, 'action' must be null, and 'final_answer' must contain your message.
- "action_input" should be a dictionary of arguments matching the tool signature.
        """

    def add_tool(self, tool_name: str, tool_description: str):
        # Insert the new tool properly
        marker = "3. read_note(filename: str): Reads the content of a file."
        if marker in self.system_prompt:
             new_entry = f"\n4. {tool_name}: {tool_description}"
             self.system_prompt = self.system_prompt.replace(marker, marker + new_entry)
        else:
             print("Warning: Could not inject tool description automatically.")

    def decide(self, history: List[Dict[str, str]]) -> CognitiveOutput:
        """
        Calls the LLM to decide the next step.
        """
        # 1. Construct Messages
        messages = [{"role": "system", "content": self.system_prompt}]
        
        for entry in history:
            role = entry['role']
            content = entry['content']
            
            # Map internal roles to OpenAI roles
            if role == 'user':
                messages.append({"role": "user", "content": content})
            elif role == 'assistant':
                messages.append({"role": "assistant", "content": content})
            elif role == 'system':
                # 'system' in our history usually means tool output, 
                # but OpenAI prevents multiple system messages or changing order arbitrarily.
                # We'll represent tool outputs as user messages to Keep It Simple for this demo
                # or strictly we should use 'tool' role if we had tool_call_ids.
                # Here we just treat it as context.
                messages.append({"role": "user", "content": f"Opbservation/Tool Output: {content}"})

        # 2. Call LLM
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content
            # Clean up potential markdown code blocks if the model adds them (e.g. ```json ... ```)
            if response_text.startswith("```"):
                response_text = response_text.strip("`").replace("json", "").strip()

            data = json.loads(response_text)
            
            return CognitiveOutput(
                thought=data.get("thought", "No thought provided."),
                action=data.get("action"),
                action_input=data.get("action_input"),
                final_answer=data.get("final_answer")
            )
            
        except Exception as e:
            return CognitiveOutput(
                thought=f"Error during LLM call: {str(e)}",
                final_answer="I apologize, my brain encountered an error."
            )
