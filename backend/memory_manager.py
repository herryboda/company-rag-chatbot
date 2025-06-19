import json
import redis
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog
from config import Config

logger = structlog.get_logger()

class MemoryManager:
    def __init__(self):
        self.redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
        self.session_ttl = 3600  # 1 hour
        
    def store_conversation(self, session_id: str, user_message: str, bot_response: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store a conversation turn in Redis"""
        try:
            conversation_data = {
                "user_message": user_message,
                "bot_response": bot_response,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # Store in session history
            key = f"session:{session_id}"
            self.redis_client.lpush(key, json.dumps(conversation_data))
            self.redis_client.ltrim(key, 0, Config.MAX_HISTORY_LENGTH - 1)
            self.redis_client.expire(key, self.session_ttl)
            
            # Store for training data collection
            if Config.FEEDBACK_COLLECTION_ENABLED:
                training_key = f"training_data:{datetime.utcnow().strftime('%Y-%m-%d')}"
                self.redis_client.lpush(training_key, json.dumps(conversation_data))
                self.redis_client.expire(training_key, 86400 * 7)  # Keep for 7 days
            
            return True
        except Exception as e:
            logger.error("Failed to store conversation", error=str(e), session_id=session_id)
            return False
    
    def get_conversation_history(self, session_id: str) -> List[Tuple[str, str]]:
        """Retrieve conversation history for a session"""
        try:
            key = f"session:{session_id}"
            history_data = self.redis_client.lrange(key, 0, -1)
            
            history = []
            for data in reversed(history_data):  # Reverse to get chronological order
                conv_data = json.loads(data)
                history.append((conv_data["user_message"], conv_data["bot_response"]))
            
            return history
        except Exception as e:
            logger.error("Failed to retrieve conversation history", error=str(e), session_id=session_id)
            return []
    
    def store_feedback(self, session_id: str, user_message: str, bot_response: str, 
                      feedback_score: int, feedback_text: Optional[str] = None) -> bool:
        """Store user feedback for training"""
        try:
            feedback_data = {
                "session_id": session_id,
                "user_message": user_message,
                "bot_response": bot_response,
                "feedback_score": feedback_score,
                "feedback_text": feedback_text,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            feedback_key = f"feedback:{datetime.utcnow().strftime('%Y-%m-%d')}"
            self.redis_client.lpush(feedback_key, json.dumps(feedback_data))
            self.redis_client.expire(feedback_key, 86400 * 30)  # Keep for 30 days
            
            return True
        except Exception as e:
            logger.error("Failed to store feedback", error=str(e), session_id=session_id)
            return False
    
    def get_training_data(self, days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve training data for model improvement"""
        try:
            training_data = []
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
                key = f"training_data:{date}"
                data = self.redis_client.lrange(key, 0, -1)
                
                for item in data:
                    training_data.append(json.loads(item))
            
            return training_data
        except Exception as e:
            logger.error("Failed to retrieve training data", error=str(e))
            return []
    
    def get_feedback_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """Retrieve feedback data for analysis"""
        try:
            feedback_data = []
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
                key = f"feedback:{date}"
                data = self.redis_client.lrange(key, 0, -1)
                
                for item in data:
                    feedback_data.append(json.loads(item))
            
            return feedback_data
        except Exception as e:
            logger.error("Failed to retrieve feedback data", error=str(e))
            return []
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session"""
        try:
            key = f"session:{session_id}"
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error("Failed to clear session", error=str(e), session_id=session_id)
            return False 