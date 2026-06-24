"""Chat management module for Remedy healthcare chatbot."""
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage


class ChatManager:
    """Manages conversation history and LangGraph agent interactions."""

    def __init__(self, graph):
        self.graph = graph
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            message["metadata"] = metadata
        self.conversation_history.append(message)

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        return self.conversation_history

    def clear_history(self):
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    async def get_response_async(self, user_message: str) -> Dict[str, Any]:
        self.add_message("user", user_message)
        try:
            result = await self.graph.ainvoke(
                {"messages": [HumanMessage(content=user_message)]}
            )
            content = result["messages"][-1].content
            self.add_message("assistant", content)
            return {"content": content, "success": True, "tool_calls": []}
        except Exception as e:
            error_message = f"Error getting response: {e}"
            self.add_message("assistant", error_message, {"error": True})
            return {"content": error_message, "success": False, "error": str(e)}

    def get_response(self, user_message: str) -> Dict[str, Any]:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.get_response_async(user_message))
                loop.close()
            else:
                result = loop.run_until_complete(self.get_response_async(user_message))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.get_response_async(user_message))
            loop.close()
        return result

    def export_conversation(self, format: str = "text") -> str:
        if format == "json":
            return json.dumps(self.conversation_history, indent=2)

        elif format == "markdown":
            output = f"# Healthcare Chat Session - {self.session_id}\n\n"
            for msg in self.conversation_history:
                role = msg["role"].capitalize()
                output += f"## {role} ({msg.get('timestamp', '')})\n\n{msg['content']}\n\n---\n\n"
            return output

        else:  # text
            output = f"Healthcare Chat Session - {self.session_id}\n" + "=" * 60 + "\n\n"
            for msg in self.conversation_history:
                output += f"[{msg.get('timestamp', '')}] {msg['role'].upper()}:\n{msg['content']}\n\n"
            return output
