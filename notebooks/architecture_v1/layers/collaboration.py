from typing import Dict, Any, Optional

class CollaborationLayer:
    """
    The 'Mouth/Ears' of the agent.
    Responsibility: Handle communication with other agents.
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.peers: Dict[str, Any] = {} # Map names to agent instances

    def discover_peers(self, peers: Dict[str, Any]):
        """Register other agents in the network."""
        # Filter out self to avoid talking to mirror
        self.peers = {k: v for k, v in peers.items() if k != self.agent_name}

    def ask_agent(self, target_name: str, question: str) -> str:
        """
        Send a message to another agent and wait for a synchronous response.
        """
        if target_name not in self.peers:
            return f"Error: Agent '{target_name}' is not known. Known peers: {list(self.peers.keys())}"
        
        target_agent = self.peers[target_name]
        
        # We assume the target agent has a 'run' or 'receive_message' method
        # Since we are using ReActAgent, it has .run(user_input)
        print(f"\n[Collaboration] {self.agent_name} calling {target_name}...")
        
        # Recursive call to the other agent's main loop
        # We prefix with "Request from {self.agent_name}:" to give context
        result = target_agent.run(f"Request from {self.agent_name}: {question}")
        
        print(f"[Collaboration] {target_name} replied to {self.agent_name}.\n")
        return result
