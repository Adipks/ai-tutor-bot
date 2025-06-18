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