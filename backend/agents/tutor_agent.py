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