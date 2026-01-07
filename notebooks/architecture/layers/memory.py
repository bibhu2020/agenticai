from dataclasses import dataclass
from typing import List, Dict

@dataclass
class MemoryEntry:
    role: str
    content: str
    timestamp: str

class MemoryLayer:
    """
    The 'Hippocampus' of the agent.
    Responsibility: Store and retrieve conversation history and state.
    """
    
    def __init__(self):
        self.short_term_memory: List[MemoryEntry] = []
    
    def add_entry(self, role: str, content: str):
        import datetime
        entry = MemoryEntry(
            role=role,
            content=content,
            timestamp=datetime.datetime.now().isoformat()
        )
        self.short_term_memory.append(entry)
        
    def get_history(self) -> List[Dict[str, str]]:
        # Format for LLM consumption
        return [{"role": m.role, "content": m.content} for m in self.short_term_memory]
