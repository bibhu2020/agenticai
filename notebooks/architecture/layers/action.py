from typing import Any, Dict

class ActionLayer:
    """
    The 'Hands' of the agent.
    Responsibility: Execute specific, well-defined tools or side-effects.
    Does NOT reason about 'why'.
    """
    
    def __init__(self):
        # Register available tools
        self.tools = {
            "calculate": self._tool_calculator,
            "save_note": self._tool_save_note,
            "read_note": self._tool_read_note
        }
    
    def execute(self, tool_name: str, args: Dict[str, Any]) -> str:
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."
        
        print(f"[Action] Executing tool: {tool_name} with args: {args}")
        try:
            return self.tools[tool_name](**args)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def _tool_calculator(self, expression: str) -> str:
        # unsafe eval for demo purposes
        try:
            allowed_chars = "0123456789+-*/(). "
            if not all(c in allowed_chars for c in expression):
                 return "Error: Invalid characters in expression"
            return str(eval(expression))
        except Exception:
            return "Error in calculation"

    def _tool_save_note(self, filename: str, content: str) -> str:
        with open(filename, 'w') as f:
            f.write(content)
        return f"File {filename} saved successfully."

    def _tool_read_note(self, filename: str) -> str:
        try:
            with open(filename, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "Error: File not found."
