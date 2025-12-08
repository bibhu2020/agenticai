from datetime import datetime
from agents import function_tool
# from ..common.utility.logger import log_call

@function_tool
# @log_call
def current_datetime(format: str = "natural") -> str:
    """
    Returns the current date and time as a formatted string.
    
    Args:
        format (str): Format style for the datetime. Options:
            - "natural" (default): "Saturday, December 7, 2025 at 3:59 PM"
            - "natural_short": "Dec 7, 2025 at 3:59 PM"
            - "natural_full": "Saturday, December 7, 2025 at 3:59:30 PM CST"
            - Custom strftime format string (e.g., "%Y-%m-%d %H:%M:%S")
    
    Returns:
        str: Current date and time in the specified format
    """
    now = datetime.now()
    
    # Natural format options
    if format == "natural":
        return now.strftime("%A, %B %d, %Y at %I:%M %p")
    elif format == "natural_short":
        return now.strftime("%b %d, %Y at %I:%M %p")
    elif format == "natural_full":
        return now.strftime("%A, %B %d, %Y at %I:%M:%S %p %Z")
    else:
        # Custom format string
        return now.strftime(format)
