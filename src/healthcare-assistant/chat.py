"""Chat management module for healthcare chatbot with conversation memory."""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from agents import Runner
from mcp.tools.rag_tool import UserContext
from langsmith import traceable


class ChatManager:
    """Manages conversation history and agent interactions."""
    
    def __init__(self, agent):
        """
        Initialize ChatManager with an agent.
        
        Args:
            agent: The healthcare agent instance to use for responses
        """
        self.agent = agent
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a message to conversation history.
        
        Args:
            role: Either 'user' or 'assistant'
            content: The message content
            metadata: Optional metadata (e.g., tool calls, sources)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            message["metadata"] = metadata
        
        self.conversation_history.append(message)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the full conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @traceable(name="Healthcare Chat Response")
    async def get_response_async(self, user_message: str) -> Dict[str, Any]:
        """
        Get a response from the agent asynchronously.
        
        Args:
            user_message: The user's message
            
        Returns:
            Dict containing response content and metadata
        """
        # Add user message to history
        self.add_message("user", user_message)
        
        try:
            print(f"\n{'='*60}")
            print(f"[CHAT] User Query: {user_message}")
            print(f"{'='*60}")
            
            # Run the agent with the user message using Runner.run()
            userContext = UserContext(
                uid=self.session_id,
                db_path="../../db/",
                file_path="../../data/",
                similarity_threshold=0.7  # FAISS L2 distance threshold (lower = better match)
            )
            response = await Runner.run(starting_agent=self.agent, 
                                        context=userContext,
                                        input=user_message)
            
            print(f"\n[CHAT] Agent execution completed")
            print(f"[CHAT] Response length: {len(response.final_output) if hasattr(response, 'final_output') else 0} characters")
            print(f"{'='*60}\n")
            
            # Extract response content from final_output
            response_content = response.final_output if hasattr(response, 'final_output') else str(response)
            
            # Add assistant response to history (tool calls are tracked via DEBUG output)
            self.add_message("assistant", response_content)
            
            return {
                "content": response_content,
                "tool_calls": [],  # Tool tracking via DEBUG logs
                "success": True
            }
            
        except Exception as e:
            error_message = f"Error getting response: {str(e)}"
            print(f"\n[CHAT] ❌ Error: {error_message}")
            print(f"{'='*60}\n")
            
            self.add_message("assistant", error_message, {"error": True})
            
            return {
                "content": error_message,
                "tool_calls": [],
                "success": False,
                "error": str(e)
            }
    
    def get_response(self, user_message: str) -> Dict[str, Any]:
        """
        Get a response from the agent (synchronous wrapper).
        
        Args:
            user_message: The user's message
            
        Returns:
            Dict containing response content and metadata
        """
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a new loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.get_response_async(user_message))
                loop.close()
            else:
                result = loop.run_until_complete(self.get_response_async(user_message))
        except RuntimeError:
            # No event loop exists, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.get_response_async(user_message))
            loop.close()
        
        return result
    
    def export_conversation(self, format: str = "text") -> str:
        """
        Export conversation history in specified format.
        
        Args:
            format: Export format ('text', 'json', 'markdown')
            
        Returns:
            Formatted conversation string
        """
        if format == "json":
            import json
            return json.dumps(self.conversation_history, indent=2)
        
        elif format == "markdown":
            output = f"# Healthcare Chat Session - {self.session_id}\n\n"
            for msg in self.conversation_history:
                role = msg["role"].capitalize()
                content = msg["content"]
                timestamp = msg.get("timestamp", "")
                output += f"## {role} ({timestamp})\n\n{content}\n\n---\n\n"
            return output
        
        else:  # text format
            output = f"Healthcare Chat Session - {self.session_id}\n"
            output += "=" * 60 + "\n\n"
            for msg in self.conversation_history:
                role = msg["role"].upper()
                content = msg["content"]
                timestamp = msg.get("timestamp", "")
                output += f"[{timestamp}] {role}:\n{content}\n\n"
            return output
