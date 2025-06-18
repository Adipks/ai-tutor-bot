# AI Tutor Bot Development Guide

## 🎯 Project Overview
Build a personalized AI tutor for C programming using Mistral 7B, with progress tracking, adaptive learning, and a clean web interface.

## 📋 Prerequisites
- Python 3.8+
- GPU (recommended) or sufficient RAM for local LLM
- Basic knowledge of Python, FastAPI, and web development
- Git for version control

## 🏗️ Phase 1: Environment Setup & Core Infrastructure

### Step 1.1: Install Ollama and Mistral 7B
```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Or for Windows, download from https://ollama.ai/download

# Pull Mistral 7B Instruct model
ollama pull mistral:7b-instruct
```

### Step 1.2: Create Project Structure
```bash
mkdir ai-tutor-bot
cd ai-tutor-bot

# Create directory structure
mkdir -p {backend,frontend,data,tests,docs}
mkdir -p backend/{api,agents,memory,models}
mkdir -p frontend/{components,pages,utils}
mkdir -p data/{lessons,quizzes,user_data}

# Initialize git repository
git init
```

### Step 1.3: Python Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate
# Or Windows: venv\Scripts\activate

# Create requirements.txt
touch requirements.txt
```

## 🔧 Phase 2: Backend Development

### Step 2.1: Install Dependencies
Add to `requirements.txt`:
```
fastapi==0.104.1
uvicorn==0.24.0
langchain==0.1.0
langchain-community==0.0.10
chromadb==0.4.18
streamlit==1.28.1
pydantic==2.5.0
python-multipart==0.0.6
ollama==0.1.7
sqlalchemy==2.0.23
```

Install:
```bash
pip install -r requirements.txt
```

### Step 2.2: Core Backend Structure

#### `backend/models/schemas.py`
```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserProfile(BaseModel):
    user_id: str
    name: str
    current_level: int = 1
    completed_lessons: List[str] = []
    quiz_scores: Dict[str, float] = {}
    learning_preferences: Dict[str, Any] = {}
    created_at: datetime
    last_active: datetime

class LessonPlan(BaseModel):
    lesson_id: str
    title: str
    level: int
    prerequisites: List[str] = []
    content: str
    code_examples: List[str] = []
    exercises: List[Dict[str, Any]] = []

class ChatMessage(BaseModel):
    message: str
    user_id: str
    context: Optional[str] = None

class QuizQuestion(BaseModel):
    question_id: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    difficulty: int
```

#### `backend/memory/vector_store.py`
```python
import chromadb
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from typing import List, Dict, Any

class MemoryManager:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.embeddings = OllamaEmbeddings(model="mistral:7b-instruct")
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
    
    def add_user_interaction(self, user_id: str, interaction: str, metadata: Dict[str, Any]):
        """Store user interaction with metadata for personalization"""
        self.vectorstore.add_texts(
            texts=[interaction],
            metadatas=[{"user_id": user_id, **metadata}]
        )
    
    def get_user_context(self, user_id: str, query: str, k: int = 5) -> List[str]:
        """Retrieve relevant context for user query"""
        results = self.vectorstore.similarity_search(
            query,
            k=k,
            filter={"user_id": user_id}
        )
        return [doc.page_content for doc in results]
    
    def add_lesson_content(self, lesson_id: str, content: str):
        """Add lesson content to vector store"""
        self.vectorstore.add_texts(
            texts=[content],
            metadatas=[{"type": "lesson", "lesson_id": lesson_id}]
        )
```

#### `backend/agents/tutor_agent.py`
```python
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from typing import Dict, Any, List

class TutorAgent:
    def __init__(self, memory_manager):
        self.llm = Ollama(model="mistral:7b-instruct", temperature=0.7)
        self.memory_manager = memory_manager
        self.conversation_memory = ConversationBufferWindowMemory(k=10)
        
        self.tutor_prompt = PromptTemplate(
            input_variables=["context", "user_level", "question", "history"],
            template="""You are an expert C programming tutor. You're patient, encouraging, and adapt your teaching style to the student's level.

Student Level: {user_level}
Previous Context: {context}
Conversation History: {history}

Student Question: {question}

Guidelines:
- Provide clear, step-by-step explanations
- Use appropriate examples for the student's level
- Encourage questions and experimentation
- Point out common mistakes and how to avoid them
- If the student seems stuck, break down the problem into smaller parts

Response:"""
        )
    
    def generate_response(self, user_id: str, question: str, user_level: int) -> str:
        # Get relevant context from user's learning history
        context = self.memory_manager.get_user_context(user_id, question)
        context_str = "\n".join(context)
        
        # Format prompt
        formatted_prompt = self.tutor_prompt.format(
            context=context_str,
            user_level=user_level,
            question=question,
            history=self.conversation_memory.buffer
        )
        
        # Generate response
        response = self.llm(formatted_prompt)
        
        # Store interaction
        self.memory_manager.add_user_interaction(
            user_id=user_id,
            interaction=f"Q: {question}\nA: {response}",
            metadata={"type": "qa", "level": user_level}
        )
        
        return response
    
    def generate_quiz(self, topic: str, difficulty: int, num_questions: int = 5) -> List[Dict[str, Any]]:
        quiz_prompt = f"""Generate {num_questions} multiple choice questions about {topic} in C programming.
Difficulty level: {difficulty}/10

Format each question as:
Q: [question]
A) [option 1]
B) [option 2] 
C) [option 3]
D) [option 4]
Correct: [A/B/C/D]
Explanation: [brief explanation]

---"""
        
        response = self.llm(quiz_prompt)
        # Parse response into structured format (implement parsing logic)
        return self._parse_quiz_response(response)
    
    def _parse_quiz_response(self, response: str) -> List[Dict[str, Any]]:
        # Implement quiz parsing logic
        questions = []
        # ... parsing implementation
        return questions
```

### Step 2.3: FastAPI Backend

#### Fix Import Structure First

**Option 1: Add __init__.py files (Recommended)**
```bash
# Create __init__.py files to make directories Python packages
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/models/__init__.py
touch backend/agents/__init__.py
touch backend/memory/__init__.py
```

**Option 2: Use relative imports in main.py**

#### `backend/api/main.py` (Fixed Version)
```python
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
```

## 🎨 Phase 3: Frontend Development

### Step 3.1: Streamlit Interface

#### `frontend/app.py`
```python
import streamlit as st
import requests
import json
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="AI C Programming Tutor",
    page_icon="🤖",
    layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def initialize_session_state():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""

def create_user(name: str):
    try:
        response = requests.post(f"{API_BASE_URL}/api/users", params={"name": name})
        if response.status_code == 200:
            return response.json()["user_id"]
    except Exception as e:
        st.error(f"Error creating user: {e}")
    return None

def send_message(message: str, user_id: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={"message": message, "user_id": user_id}
        )
        if response.status_code == 200:
            return response.json()["response"]
    except Exception as e:
        st.error(f"Error sending message: {e}")
    return None

def main():
    initialize_session_state()
    
    st.title("🤖 AI C Programming Tutor")
    st.markdown("Your personal AI tutor for learning C programming!")
    
    # Sidebar for user management
    with st.sidebar:
        st.header("User Profile")
        
        if st.session_state.user_id is None:
            name = st.text_input("Enter your name:")
            if st.button("Start Learning"):
                if name:
                    user_id = create_user(name)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.user_name = name
                        st.success(f"Welcome, {name}!")
                        st.rerun()
        else:
            st.success(f"Welcome back, {st.session_state.user_name}!")
            if st.button("New Session"):
                st.session_state.user_id = None
                st.session_state.messages = []
                st.rerun()
    
    # Main chat interface
    if st.session_state.user_id:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about C programming!"):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = send_message(prompt, st.session_state.user_id)
                    if response:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.info("Please enter your name in the sidebar to start learning!")

if __name__ == "__main__":
    main()
```

## 🚀 Phase 4: Deployment Setup

### Step 4.1: Create Deployment Files

#### `docker-compose.yml`
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - OLLAMA_HOST=http://ollama:11434
  
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
  
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  ollama:
```

#### `Dockerfile`
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📚 Phase 5: Content & Lesson Management

### Step 5.1: Lesson Content Structure

#### `data/lessons/lesson_01_basics.json`
```json
{
  "lesson_id": "c_basics_01",
  "title": "Introduction to C Programming",
  "level": 1,
  "prerequisites": [],
  "content": "C is a powerful general-purpose programming language...",
  "code_examples": [
    "#include <stdio.h>\n\nint main() {\n    printf(\"Hello, World!\\n\");\n    return 0;\n}"
  ],
  "exercises": [
    {
      "instruction": "Write a program that prints your name",
      "expected_output": "Your Name",
      "hints": ["Use printf function", "Don't forget to include stdio.h"]
    }
  ]
}
```

## 🧪 Phase 6: Testing & Launch

### Step 6.1: Testing Script

#### `tests/test_basic_functionality.py`
```python
import pytest
import requests
import time

def test_api_health():
    response = requests.get("http://localhost:8000/docs")
    assert response.status_code == 200

def test_user_creation():
    response = requests.post("http://localhost:8000/api/users", params={"name": "Test User"})
    assert response.status_code == 200
    assert "user_id" in response.json()

def test_chat_functionality():
    # Create user first
    user_response = requests.post("http://localhost:8000/api/users", params={"name": "Test User"})
    user_id = user_response.json()["user_id"]
    
    # Send chat message
    chat_response = requests.post(
        "http://localhost:8000/api/chat",
        json={"message": "What is a variable in C?", "user_id": user_id}
    )
    assert chat_response.status_code == 200
    assert "response" in chat_response.json()
```

## 🎯 Next Steps & Enhancements

### Phase 7: Advanced Features
- **Code Execution**: Integrate online C compiler
- **Progress Tracking**: Visual progress charts
- **Adaptive Learning**: AI-driven difficulty adjustment
- **Code Review**: AI code analysis and suggestions
- **Gamification**: Points, badges, leaderboards

### Phase 8: Production Deployment
- **Database**: Replace in-memory storage with PostgreSQL
- **Authentication**: Add user authentication
- **Scaling**: Container orchestration with Kubernetes
- **Monitoring**: Add logging and monitoring
- **Security**: Input validation, rate limiting

## 🔧 Quick Start Commands (Fixed)

```bash
# Clone and setup
git clone <your-repo>
cd ai-tutor-bot
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Create __init__.py files for proper imports
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/models/__init__.py
touch backend/agents/__init__.py
touch backend/memory/__init__.py

# Start Ollama and pull model
ollama serve
ollama pull mistral:7b-instruct

# Run backend (from project root)
python -m backend.api.main
# OR
cd backend/api && python main.py

# Run frontend (new terminal, from project root)
streamlit run frontend/app.py

# Access application
# Frontend: http://localhost:8501
# API Docs: http://localhost:8000/docs
```

## 🐛 Common Import Issues & Solutions

### Issue 1: ModuleNotFoundError: No module named 'backend'

**Solution A: Create proper package structure**
```bash
# Make sure all directories have __init__.py files
find . -type d -name "backend*" -exec touch {}/__init__.py \;
find . -type d -name "frontend*" -exec touch {}/__init__.py \;
```

**Solution B: Add to PYTHONPATH**
```bash
# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Or in Windows: set PYTHONPATH=%PYTHONPATH%;%cd%
```

**Solution C: Use absolute imports from project root**
```bash
# Always run Python commands from project root
python -m backend.api.main
```

### Issue 2: Import errors with dependencies

**Check if all dependencies are installed:**
```bash
pip list | grep -E "(fastapi|langchain|chromadb|streamlit)"
```

**If missing, reinstall:**
```bash
pip install -r requirements.txt --force-reinstall
```

This guide provides a solid foundation for your AI Tutor Bot. Each phase builds upon the previous one, allowing you to develop and test incrementally.
