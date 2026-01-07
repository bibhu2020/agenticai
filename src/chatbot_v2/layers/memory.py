from typing import List, Dict

class MemoryLayer:
    """
    The 'Memory' of the agent.
    Responsibility: Store and retrieve conversation history.
    """
    
    def __init__(self):
        self.history: List[Dict[str, str]] = []

    def add_entry(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        return self.history
    
    def set_history(self, messages: List[Dict[str, str]]):
        """Allows initializing/overwriting memory from external source (e.g. Streamlit session)"""
        self.history = messages
