from src.chatbot_v2.layers.perception import PerceptionLayer
from src.chatbot_v2.layers.cognition import CognitionLayer, CognitiveOutput
from src.chatbot_v2.layers.action import ActionLayer
from src.chatbot_v2.layers.memory import MemoryLayer
from typing import List, Dict

class ChatbotOrchestrator:
    """
    DESIGN PATTERN: ReAct (Reason + Act) - Orchestrator
    
    Structure:
    1. Loop:
       - Update Perception
       - Consult Cognition (Reasoning)
       - If Action needed -> Call Action Layer -> Loop
       - If Final Answer -> Return
    """
    
    def __init__(self):
        # Initialize the 'Organs' (Layers)
        self.perception = PerceptionLayer()
        self.brain = CognitionLayer()
        self.hands = ActionLayer()
        self.memory = MemoryLayer()
        
    async def run(self, user_input: str, external_history: List[Dict[str, str]] = None):
        """
        Runs the agent loop.
        Args:
            user_input: The new message from the user.
            external_history: Existing chat history (e.g. from Streamlit).
        """
        # 1. Sync Memory
        if external_history:
            self.memory.set_history(list(external_history)) # Copy
        
        # 2. Perception Layer (Input)
        env_state = self.perception.perceive(user_input)
        self.memory.add_entry("user", env_state.user_input)
        
        # Max steps to prevent infinite loops
        for step in range(5):
            print(f"\n--- Step {step+1} (ReAct Loop) ---")
            
            # 3. Cognition Layer (Reasoning)
            history = self.memory.get_history()
            decision: CognitiveOutput = await self.brain.decide(history)
            
            print(f"[Think]: {decision.thought}")
            
            # 4. Handling Decision
            if decision.final_answer:
                print(f"[Final Answer]: {decision.final_answer}")
                self.memory.add_entry("assistant", decision.final_answer)
                return decision.final_answer
                
            if decision.action:
                # 5. Action Layer (Execution)
                print(f"[Action Needed]: Call {decision.action} with {decision.action_input}")
                tool_result = await self.hands.execute(decision.action, decision.action_input or {})
                
                # 6. Feedback Loop
                print(f"[Observation]: {tool_result}")
                self.memory.add_entry("system", f"Tool {decision.action} returned: {tool_result}")
                
        return "I apologize, but I got stuck in a loop trying to answer your request."
