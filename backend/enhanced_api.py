import os
import uuid
import structlog
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from config import Config
from enhanced_rag import EnhancedRAG
from memory_manager import MemoryManager
from self_training import SelfTrainingManager

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="Enhanced Company RAG Chatbot",
    description="Advanced RAG chatbot with self-training capabilities",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
rag_system = EnhancedRAG()
memory_manager = MemoryManager()
training_manager = SelfTrainingManager(memory_manager)

# Pydantic models
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    confidence: float
    sources: List[Dict[str, str]]
    context_used: bool
    docs_found: int = 0  # Number of relevant documents found
    response_type: str = "company_docs"  # "company_docs" or "generic"

class FeedbackRequest(BaseModel):
    session_id: str
    user_message: str
    bot_response: str
    feedback_score: int  # 1-5 scale
    feedback_text: Optional[str] = None

class TrainingReportResponse(BaseModel):
    report: Dict[str, Any]
    status: str

class SystemHealthResponse(BaseModel):
    status: str
    components: Dict[str, str]
    metrics: Dict[str, Any]

# Enhanced small talk with more human-like responses
ENHANCED_SMALL_TALK = {
    "thanks": "You're very welcome! 😊 I'm here to help with any company policy questions you might have.",
    "thank you": "You're welcome! Feel free to ask if you need anything else about our policies.",
    "makes sense": "Great! I'm glad that was helpful. Is there anything else you'd like to know?",
    "cool": "Awesome! 😎 What else can I help you with today?",
    "okay": "Perfect! 👍 Let me know if you have any other questions.",
    "ok": "Got it! 👌 Anything else on your mind?",
    "got it": "Excellent! I'm here whenever you need help with company policies.",
    "great": "Fantastic! I love helping out with policy questions. What's next?",
    "nice": "Thanks! 😄 I try my best to be helpful. Any other questions?",
    "bye": "Goodbye! 👋 Have a great day, and don't hesitate to reach out if you need help with policies later!",
    "hello": "Hi there! 👋 I'm your company policy assistant. How can I help you today?",
    "hi": "Hey! 👋 Ready to help with any company policy questions you have!",
    "goodbye": "Take care! 👋 Feel free to come back anytime for policy help!",
    "see you": "See you later! 👋 I'll be here when you need policy assistance!",
}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Enhanced chat endpoint with confidence scoring and source tracking"""
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get conversation history
    history = memory_manager.get_conversation_history(session_id)
    
    # Check for small talk first
    message_lower = request.message.strip().lower()
    if message_lower in ENHANCED_SMALL_TALK:
        answer = ENHANCED_SMALL_TALK[message_lower]
        memory_manager.store_conversation(session_id, request.message, answer)
        return ChatResponse(
            session_id=session_id,
            answer=answer,
            confidence=1.0,
            sources=[],
            context_used=False,
            docs_found=0,
            response_type="small_talk"
        )
    
    try:
        # Get enhanced response from RAG system
        result = rag_system.query(request.message, history)
        
        # Determine response type
        response_type = "company_docs" if result["context_used"] else "generic"
        
        # Store conversation for training
        memory_manager.store_conversation(
            session_id, 
            request.message, 
            result["answer"],
            metadata={
                "confidence": result["confidence"],
                "context_used": result["context_used"],
                "sources_count": len(result["sources"]),
                "docs_found": result["docs_found"],
                "response_type": response_type
            }
        )
        
        # Log the interaction
        logger.info(
            "Chat interaction",
            session_id=session_id,
            message_length=len(request.message),
            confidence=result["confidence"],
            context_used=result["context_used"],
            sources_count=len(result["sources"]),
            docs_found=result["docs_found"],
            response_type=response_type
        )
        
        return ChatResponse(
            session_id=session_id,
            answer=result["answer"],
            confidence=result["confidence"],
            sources=result["sources"],
            context_used=result["context_used"],
            docs_found=result["docs_found"],
            response_type=response_type
        )
        
    except Exception as e:
        logger.error("Error in chat endpoint", error=str(e), session_id=session_id)
        return ChatResponse(
            session_id=session_id,
            answer="I apologize, but I encountered an error while processing your question. Please try again.",
            confidence=0.0,
            sources=[],
            context_used=False,
            docs_found=0,
            response_type="error"
        )

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for training"""
    try:
        success = memory_manager.store_feedback(
            request.session_id,
            request.user_message,
            request.bot_response,
            request.feedback_score,
            request.feedback_text
        )
        
        if success:
            logger.info(
                "Feedback received",
                session_id=request.session_id,
                score=request.feedback_score
            )
            return {"status": "success", "message": "Feedback recorded successfully"}
        else:
            raise HTTPException(500, "Failed to store feedback")
            
    except Exception as e:
        logger.error("Feedback error", error=str(e))
        raise HTTPException(500, f"Feedback error: {e}")

@app.get("/training/report", response_model=TrainingReportResponse)
async def get_training_report(background_tasks: BackgroundTasks):
    """Get comprehensive training report"""
    try:
        # Collect data in background
        background_tasks.add_task(training_manager.collect_training_data)
        background_tasks.add_task(training_manager.collect_feedback_data)
        
        # Generate report
        report = training_manager.export_training_report()
        
        return TrainingReportResponse(
            report=report,
            status="success"
        )
        
    except Exception as e:
        logger.error("Training report error", error=str(e))
        raise HTTPException(500, f"Report generation error: {e}")

@app.get("/health", response_model=SystemHealthResponse)
async def system_health():
    """Get system health status"""
    try:
        # Check components
        components = {
            "rag_system": "healthy",
            "memory_manager": "healthy",
            "training_manager": "healthy"
        }
        
        # Basic metrics
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "self_training_enabled": Config.ENABLE_SELF_TRAINING,
            "feedback_collection_enabled": Config.FEEDBACK_COLLECTION_ENABLED,
            "quality_threshold": Config.MIN_CONFIDENCE_THRESHOLD
        }
        
        return SystemHealthResponse(
            status="healthy",
            components=components,
            metrics=metrics
        )
        
    except Exception as e:
        logger.error("Health check error", error=str(e))
        return SystemHealthResponse(
            status="unhealthy",
            components={"error": str(e)},
            metrics={}
        )

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session"""
    try:
        success = memory_manager.clear_session(session_id)
        if success:
            return {"status": "success", "message": f"Session {session_id} cleared"}
        else:
            raise HTTPException(500, "Failed to clear session")
    except Exception as e:
        logger.error("Session clear error", error=str(e), session_id=session_id)
        raise HTTPException(500, f"Session clear error: {e}")

@app.get("/training/suggestions")
async def get_improvement_suggestions():
    """Get improvement suggestions based on training data"""
    try:
        # Collect recent data
        training_manager.collect_training_data()
        training_manager.collect_feedback_data()
        
        suggestions = training_manager.generate_improvement_suggestions()
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error("Suggestions error", error=str(e))
        raise HTTPException(500, f"Suggestions error: {e}")

@app.get("/training/examples")
async def get_training_examples():
    """Get high-quality training examples"""
    try:
        training_manager.collect_training_data()
        examples = training_manager.create_training_examples()
        return {"examples": examples}
        
    except Exception as e:
        logger.error("Training examples error", error=str(e))
        raise HTTPException(500, f"Training examples error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 