from dataclasses import dataclass
import datetime

@dataclass
class EnvironmentState:
    user_input: str
    timestamp: str
    source: str

class PerceptionLayer:
    """
    The 'Sensors' of the agent. 
    Responsibility: Accept raw data, clean it, and package it into a standard format.
    Does NOT make decisions.
    """
    
    def perceive(self, raw_text: str, source: str = "user_terminal") -> EnvironmentState:
        # Simulate cleaning or pre-processing
        clean_text = raw_text.strip()
        
        print(f"\n[Perception] Detected input from {source}: '{clean_text}'")
        
        return EnvironmentState(
            user_input=clean_text,
            timestamp=datetime.datetime.now().isoformat(),
            source=source
        )
