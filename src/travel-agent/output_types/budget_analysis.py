from typing import List, Optional
from pydantic import BaseModel, Field

# --- Models for structured outputs ---
class BudgetAnalysis(BaseModel):
    is_realistic: bool
    reasoning: str
    suggested_budget: Optional[float] = None