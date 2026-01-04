
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse
from orchestrator import MediBoOrchestrator
from database import init_db

app = FastAPI(title="MediBo API", description="AI Triage Agent")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = MediBoOrchestrator()

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    response, action = await orchestrator.handle_request(request.patient_id, request.message)
    return ChatResponse(response=response, action_taken=action)

@app.get("/")
def read_root():
    return {"message": "MediBo API is running"}
