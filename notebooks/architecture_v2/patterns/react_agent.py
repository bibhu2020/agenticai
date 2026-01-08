from typing import List, Optional, Callable
from layers.perception import PerceptionLayer
from layers.cognition import CognitionLayer
from layers.action import ActionLayer
from layers.memory import MemoryLayer
from layers.security import get_input_guardrail, get_output_guardrail
from agents import Runner, function_tool, trace

class ReActAgent:
    """
    DESIGN PATTERN: ReAct (Reason + Act)
    
    This agent combines reasoning (LLM) with action execution (Tools).
    Now delegates the loop to OpenAI Agents SDK 'Runner'.
    """
    
    def __init__(self, name: str = "Assistant", 
                 tools: list = None, 
                 handoffs: list = None, 
                 model: str = "gpt-4o", 
                 instructions: str = "You are a helpful assistant."):
        self.name = name
        
        # Initialize the 'Organs' (Layers)
        self.perception = PerceptionLayer()
        self.memory = MemoryLayer()
        
        # Initialize Native SDK Guardrails
        self.input_guardrails = [get_input_guardrail()]
        self.output_guardrails = [get_output_guardrail()]
        
        # Prepare tools
        if tools is None:
            tools = []
            
        # Brain gets the full toolset AND guardrails (Input & Output)
        self.brain = CognitionLayer(
            name=name, 
            tools=tools, 
            handoffs=handoffs, 
            input_guardrails=self.input_guardrails, 
            output_guardrails=self.output_guardrails,
            model=model,
            instructions=instructions
        )
    
    @property
    def agent(self):
        """Expose the inner OpenAI SDK Agent for handoffs."""
        return self.brain.agent
        
    async def run(self, user_input: str):
        # 1. Perception Layer (Input)
        env_state = self.perception.perceive(user_input)
        
        # 2. Security Check (Native Guardrail handled by Agent execution)
        # We no longer validate manually. The SDK Runner will invoke the guardrail agent first.
            
        self.memory.add_entry("user", env_state.user_input)
        
        print(f"\n--- [{self.name}] Agent SDK Runner ---")
        
        # 3. Cognition + Action (Handled by SDK)
        # Runner handles the ReAct loop (Thought -> Action -> Observation -> Repeat)
        # We use 'trace' to output debug logs showing tool calls and handoffs
        with trace(f"Agent {self.name}"):
            result = await Runner.run(self.brain.agent, input=env_state.user_input)
        
        # 3. Output
        # Determine who actually answered (if Handoff occurred)
        responder_name = self.name
        if hasattr(result, "agent") and hasattr(result.agent, "name"):
            responder_name = result.agent.name
            
        print(f"[{responder_name} Final Answer]: {result.final_output}")
        self.memory.add_entry("assistant", result.final_output)
        
        return result.final_output
