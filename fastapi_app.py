from fastapi import FastAPI
from src.chatbot.legal_assistant import get_assistant_response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import uvicorn

app = FastAPI()

# Allow Streamlit to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ChatRequest(BaseModel):
    user_query: str
    conversation_history: List[Dict[str, str]]

# Response model
class ChatResponse(BaseModel):
    assistant_reply: str

@app.get("/")
def root():
    return {"message": "FastAPI backend is running"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Receives user query and conversation history,
    returns assistant's reply.
    """
    reply = get_assistant_response(
        user_query=request.user_query,
        conversation_history=request.conversation_history
    )
    return {"assistant_reply": reply}

if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000)
