from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.models.schemas import ChatMessage, UserProfile
from backend.agents.tutor_agent import TutorAgent
from backend.memory.vector_store import MemoryManager
import uuid
from datetime import datetime

app = FastAPI(title="AI Tutor Bot API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
memory_manager = MemoryManager()
tutor_agent = TutorAgent(memory_manager)

# In-memory user storage (replace with proper database)
users_db = {}

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        user_level = users_db.get(message.user_id, {}).get("current_level", 1)
        response = tutor_agent.generate_response(
            user_id=message.user_id,
            question=message.message,
            user_level=user_level
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users")
async def create_user(name: str):
    user_id = str(uuid.uuid4())
    user = UserProfile(
        user_id=user_id,
        name=name,
        created_at=datetime.now(),
        last_active=datetime.now()
    )
    users_db[user_id] = user.dict()
    return {"user_id": user_id}

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

@app.post("/api/quiz/{topic}")
async def generate_quiz(topic: str, difficulty: int = 5):
    try:
        quiz = tutor_agent.generate_quiz(topic, difficulty)
        return {"quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)