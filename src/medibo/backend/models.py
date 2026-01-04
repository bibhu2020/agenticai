
from pydantic import BaseModel

class ChatRequest(BaseModel):
    patient_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    action_taken: str
