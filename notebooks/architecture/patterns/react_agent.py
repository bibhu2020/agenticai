from layers.perception import PerceptionLayer
from layers.cognition import CognitionLayer, CognitiveOutput
from layers.action import ActionLayer
from layers.memory import MemoryLayer

class ReActAgent:
    """
    DESIGN PATTERN: ReAct (Reason + Act)
    
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
        
    def run(self, user_input: str):
        # 1. Perception Layer (Input)
        env_state = self.perception.perceive(user_input)
        self.memory.add_entry("user", env_state.user_input)
        
        # Max steps to prevent infinite loops (Pattern Safeguard)
        for step in range(5):
            print(f"\n--- Step {step+1} (ReAct Loop) ---")
            
            # 2. Cognition Layer (Reasoning)
            # The 'Pattern' here is feeding the entire history to the brain at each step
            history = self.memory.get_history()
            decision: CognitiveOutput = self.brain.decide(history)
            
            print(f"[Think]: {decision.thought}")
            
            # 3. Handling Decision (Pattern Logic)
            if decision.final_answer:
                print(f"[Final Answer]: {decision.final_answer}")
                self.memory.add_entry("assistant", decision.final_answer)
                return decision.final_answer
                
            if decision.action:
                # 4. Action Layer (Execution)
                print(f"[Action Needed]: Call {decision.action} with {decision.action_input}")
                tool_result = self.hands.execute(decision.action, decision.action_input)
                
                # 5. Feedback Loop (Pattern Logic)
                # We feed the result back into memory so the brain sees it next time
                print(f"[Observation]: {tool_result}")
                self.memory.add_entry("system", f"Tool {decision.action} returned: {tool_result}")
                
        return "Agent stuck in a loop."
