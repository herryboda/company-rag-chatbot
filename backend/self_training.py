import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import structlog
from config import Config
from memory_manager import MemoryManager

logger = structlog.get_logger()

class SelfTrainingManager:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.training_data = []
        self.feedback_data = []
        self.quality_threshold = Config.MIN_CONFIDENCE_THRESHOLD
        
    def collect_training_data(self, days: int = 7) -> List[Dict[str, Any]]:
        """Collect training data from recent conversations"""
        try:
            training_data = self.memory_manager.get_training_data(days)
            self.training_data = training_data
            logger.info("Collected training data", count=len(training_data))
            return training_data
        except Exception as e:
            logger.error("Failed to collect training data", error=str(e))
            return []
    
    def collect_feedback_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """Collect feedback data for analysis"""
        try:
            feedback_data = self.memory_manager.get_feedback_data(days)
            self.feedback_data = feedback_data
            logger.info("Collected feedback data", count=len(feedback_data))
            return feedback_data
        except Exception as e:
            logger.error("Failed to collect feedback data", error=str(e))
            return []
    
    def analyze_conversation_patterns(self) -> Dict[str, Any]:
        """Analyze conversation patterns to identify improvement areas"""
        try:
            if not self.training_data:
                return {"error": "No training data available"}
            
            # Extract questions and answers
            questions = [item["user_message"] for item in self.training_data]
            answers = [item["bot_response"] for item in self.training_data]
            
            # Analyze question types
            question_types = self._categorize_questions(questions)
            
            # Analyze answer quality
            answer_quality = self._analyze_answer_quality(answers)
            
            # Find common patterns
            common_patterns = self._find_common_patterns(questions, answers)
            
            return {
                "total_conversations": len(self.training_data),
                "question_types": question_types,
                "answer_quality": answer_quality,
                "common_patterns": common_patterns,
                "analysis_date": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Failed to analyze conversation patterns", error=str(e))
            return {"error": str(e)}
    
    def _categorize_questions(self, questions: List[str]) -> Dict[str, int]:
        """Categorize questions by type"""
        categories = {
            "policy": 0,
            "procedure": 0,
            "general": 0,
            "clarification": 0,
            "complaint": 0
        }
        
        keywords = {
            "policy": ["policy", "policies", "rule", "rules", "regulation"],
            "procedure": ["procedure", "process", "step", "how to", "what is"],
            "clarification": ["clarify", "explain", "what do you mean", "can you explain"],
            "complaint": ["complaint", "issue", "problem", "wrong", "incorrect"]
        }
        
        for question in questions:
            question_lower = question.lower()
            categorized = False
            
            for category, words in keywords.items():
                if any(word in question_lower for word in words):
                    categories[category] += 1
                    categorized = True
                    break
            
            if not categorized:
                categories["general"] += 1
        
        return categories
    
    def _analyze_answer_quality(self, answers: List[str]) -> Dict[str, Any]:
        """Analyze the quality of answers"""
        total_answers = len(answers)
        if total_answers == 0:
            return {"error": "No answers to analyze"}
        
        # Length analysis
        lengths = [len(answer.split()) for answer in answers]
        avg_length = np.mean(lengths)
        
        # Specificity analysis
        specific_answers = 0
        generic_answers = 0
        
        generic_phrases = [
            "i don't know", "i'm not sure", "i cannot", "i don't have",
            "please check", "contact", "refer to"
        ]
        
        for answer in answers:
            answer_lower = answer.lower()
            if any(phrase in answer_lower for phrase in generic_phrases):
                generic_answers += 1
            else:
                specific_answers += 1
        
        return {
            "total_answers": total_answers,
            "average_length": avg_length,
            "specific_answers": specific_answers,
            "generic_answers": generic_answers,
            "specificity_ratio": specific_answers / total_answers
        }
    
    def _find_common_patterns(self, questions: List[str], answers: List[str]) -> List[Dict[str, Any]]:
        """Find common patterns in questions and answers"""
        try:
            # Vectorize questions
            question_vectors = self.vectorizer.fit_transform(questions)
            
            # Find similar questions
            patterns = []
            processed_indices = set()
            
            for i in range(len(questions)):
                if i in processed_indices:
                    continue
                
                # Find similar questions
                similarities = cosine_similarity(
                    question_vectors[i:i+1], question_vectors
                ).flatten()
                
                similar_indices = [j for j, sim in enumerate(similarities) if sim > 0.7 and j != i]
                
                if similar_indices:
                    pattern = {
                        "main_question": questions[i],
                        "main_answer": answers[i],
                        "similar_questions": [questions[j] for j in similar_indices],
                        "similar_answers": [answers[j] for j in similar_indices],
                        "frequency": len(similar_indices) + 1
                    }
                    patterns.append(pattern)
                    
                    # Mark as processed
                    processed_indices.add(i)
                    processed_indices.update(similar_indices)
            
            # Sort by frequency
            patterns.sort(key=lambda x: x["frequency"], reverse=True)
            return patterns[:10]  # Return top 10 patterns
            
        except Exception as e:
            logger.error("Failed to find common patterns", error=str(e))
            return []
    
    def generate_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Generate suggestions for improving the chatbot"""
        suggestions = []
        
        # Analyze patterns
        patterns = self.analyze_conversation_patterns()
        
        if "error" in patterns:
            return [{"type": "error", "message": patterns["error"]}]
        
        # Suggestion 1: Add more context for generic questions
        if patterns["answer_quality"]["specificity_ratio"] < 0.7:
            suggestions.append({
                "type": "context_improvement",
                "priority": "high",
                "message": "Many answers are generic. Consider adding more specific policy information.",
                "metric": f"Specificity ratio: {patterns['answer_quality']['specificity_ratio']:.2f}"
            })
        
        # Suggestion 2: Improve handling of common question types
        question_types = patterns["question_types"]
        most_common_type = max(question_types.items(), key=lambda x: x[1])
        if most_common_type[1] > len(self.training_data) * 0.3:
            suggestions.append({
                "type": "question_type_optimization",
                "priority": "medium",
                "message": f"Many questions are about {most_common_type[0]}. Consider improving responses for this category.",
                "metric": f"{most_common_type[0]}: {most_common_type[1]} questions"
            })
        
        # Suggestion 3: Based on feedback analysis
        if self.feedback_data:
            avg_feedback = np.mean([item["feedback_score"] for item in self.feedback_data])
            if avg_feedback < 4.0:  # Assuming 1-5 scale
                suggestions.append({
                    "type": "feedback_improvement",
                    "priority": "high",
                    "message": "User feedback scores are low. Review recent conversations for improvement opportunities.",
                    "metric": f"Average feedback score: {avg_feedback:.2f}"
                })
        
        return suggestions
    
    def create_training_examples(self) -> List[Dict[str, Any]]:
        """Create training examples from high-quality conversations"""
        training_examples = []
        
        for item in self.training_data:
            # Filter for high-quality conversations
            if len(item["bot_response"]) > 50:  # Not too short
                if not any(phrase in item["bot_response"].lower() for phrase in [
                    "i don't know", "i'm not sure", "i cannot"
                ]):
                    training_examples.append({
                        "question": item["user_message"],
                        "answer": item["bot_response"],
                        "quality_score": 1.0,
                        "timestamp": item["timestamp"]
                    })
        
        return training_examples
    
    def export_training_report(self) -> Dict[str, Any]:
        """Export a comprehensive training report"""
        return {
            "report_date": datetime.utcnow().isoformat(),
            "data_summary": {
                "training_data_count": len(self.training_data),
                "feedback_data_count": len(self.feedback_data),
                "analysis_period_days": 7
            },
            "conversation_analysis": self.analyze_conversation_patterns(),
            "improvement_suggestions": self.generate_improvement_suggestions(),
            "training_examples": self.create_training_examples(),
            "system_health": {
                "self_training_enabled": Config.ENABLE_SELF_TRAINING,
                "feedback_collection_enabled": Config.FEEDBACK_COLLECTION_ENABLED,
                "quality_threshold": self.quality_threshold
            }
        } 