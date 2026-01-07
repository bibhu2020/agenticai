from dataclasses import dataclass
import datetime
from urllib.parse import urlparse

@dataclass
class EnvironmentState:
    url: str
    timestamp: str
    is_valid_url: bool
    error_message: str = None

class PerceptionLayer:
    """
    Validates and accepts the target URL.
    """
    
    def perceive(self, raw_input: str) -> EnvironmentState:
        url = raw_input.strip()
        is_valid = self._validate_url(url)
        
        return EnvironmentState(
            url=url,
            timestamp=datetime.datetime.now().isoformat(),
            is_valid_url=is_valid,
            error_message=None if is_valid else "Invalid URL format."
        )

    def _validate_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
