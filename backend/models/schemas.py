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