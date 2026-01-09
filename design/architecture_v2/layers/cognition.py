import os
from pathlib import Path
from typing import List, Callable, Optional, Union, Any
from agents import Agent
from dotenv import load_dotenv

# Load .env from project root
# current file: notebooks/architecture/layers/cognition.py
# root: ../../../
root_path = Path(__file__).parent.parent.parent.parent
load_dotenv(root_path / ".env")

class CognitionLayer:
    """
    The 'Brain' of the agent.
    Responsibility: Reason about the state and decide the next move.
    Now uses the OpenAI Agents SDK.
    """
    
    def __init__(self, name: str = "Assistant", 
                    tools: Optional[List[Callable]] = None, 
                    handoffs: Optional[List[Agent]] = None, 
                    input_guardrails: Optional[List] = None, 
                    output_guardrails: Optional[List] = None, 
                    model: Union[str, Any] = "gpt-4o", 
                    instructions: str = "You are a helpful AI assistant."):
        if tools is None:
            tools = []
        if handoffs is None:
            handoffs = []
        if input_guardrails is None:
            input_guardrails = []
        if output_guardrails is None:
            output_guardrails = []
            
        self.model_name = model
        
        self.agent = Agent(
            name=name,
            instructions=instructions.strip(),
            tools=tools,
            handoffs=handoffs,
            model=self.model_name
        )
        
        # Assign Guardrails
        if input_guardrails:
             self.agent.input_guardrails = input_guardrails
             
        if output_guardrails:
             self.agent.output_guardrails = output_guardrails

    def add_tool(self, tool: Callable):
        """
        Dynamically add a tool to the agent's brain.
        """
        if isinstance(self.agent.tools, list):
            self.agent.tools.append(tool)
