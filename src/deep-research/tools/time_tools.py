from datetime import datetime
from agents import function_tool
from core.logger import log_call

class TimeTools:
    """Provides tools related to current date and time."""

    @staticmethod
    @function_tool
    @log_call
    def current_datetime(format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Returns the current date and time as a formatted string.
        
        Args:
            format (str): Optional datetime format (default: "YYYY-MM-DD HH:MM:SS")
        
        Returns:
            str: Current date and time in the specified format
        """
        now = datetime.now()
        return now.strftime(format)
