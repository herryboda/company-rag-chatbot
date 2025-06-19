import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Vector Store Configuration
    QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "company_policies")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # RAG Configuration - More strict threshold to prioritize company docs
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "6"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.8"))  # Increased from 0.7 to 0.8
    
    # Conversation Configuration
    MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", "10"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Training Configuration
    ENABLE_SELF_TRAINING = os.getenv("ENABLE_SELF_TRAINING", "true").lower() == "true"
    FEEDBACK_COLLECTION_ENABLED = os.getenv("FEEDBACK_COLLECTION_ENABLED", "true").lower() == "true"
    MIN_CONFIDENCE_THRESHOLD = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.8"))
    
    # Redis Configuration (for session management)
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # Data Directory
    DATA_DIR = os.getenv("DATA_DIR", "/app/data")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_rag_config(cls) -> Dict[str, Any]:
        return {
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "top_k": cls.TOP_K_RETRIEVAL,
            "similarity_threshold": cls.SIMILARITY_THRESHOLD,
        }
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        return {
            "model": cls.OPENAI_MODEL,
            "temperature": cls.TEMPERATURE,
            "embedding_model": cls.OPENAI_EMBEDDING_MODEL,
        } 