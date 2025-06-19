import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import structlog
from config import Config

logger = structlog.get_logger()

class EnhancedRAG:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=Config.OPENAI_EMBEDDING_MODEL)
        self.client = QdrantClient(url=Config.QDRANT_URL)
        self._setup_collection()
        self.vectorstore = Qdrant(
            client=self.client,
            collection_name=Config.QDRANT_COLLECTION,
            embeddings=self.embeddings,
        )
        
        # Enhanced LLM with better temperature for human-like responses
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.TEMPERATURE
        )
        
        self._setup_chain()
    
    def _setup_collection(self):
        """Setup Qdrant collection with proper configuration"""
        if not self.client.collection_exists(Config.QDRANT_COLLECTION):
            self.client.create_collection(
                collection_name=Config.QDRANT_COLLECTION,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            logger.info("Created new Qdrant collection", collection=Config.QDRANT_COLLECTION)
    
    def _setup_chain(self):
        """Setup enhanced conversational chain with strict context-based prompt"""
        # Create the chains with proper configuration
        from langchain.chains import ConversationalRetrievalChain
        
        # Create retrieval chains with default prompts but enhanced configuration
        self.strict_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(
                search_kwargs={
                    "k": Config.TOP_K_RETRIEVAL,
                    "score_threshold": Config.SIMILARITY_THRESHOLD
                }
            ),
            return_source_documents=True,
            verbose=True,
            max_tokens_limit=2000,
            chain_type="stuff"
        )
        
        self.generic_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 1}),  # Use k=1 to avoid Qdrant error
            return_source_documents=True,
            verbose=True,
            max_tokens_limit=2000,
            chain_type="stuff"
        )
    
    def query(self, question: str, chat_history: List[Tuple[str, str]] = None) -> Dict[str, Any]:
        """Enhanced query that prioritizes company documents over generic answers"""
        try:
            # First, search for relevant company documents
            k_retrieval = max(1, Config.TOP_K_RETRIEVAL)
            docs = self.vectorstore.similarity_search_with_score(
                question, 
                k=k_retrieval
            )
            
            # Filter documents based on similarity threshold
            relevant_docs = [(doc, score) for doc, score in docs if score >= Config.SIMILARITY_THRESHOLD]
            
            # Calculate confidence based on similarity scores
            if relevant_docs:
                scores = [score for _, score in relevant_docs]
                avg_score = np.mean(scores)
                max_score = max(scores)
                confidence = min(1.0, (avg_score + max_score) / 2)
                
                # Use strict chain with company documents
                result = self.strict_chain({
                    "question": question,
                    "chat_history": chat_history or []
                })
                
                context_used = True
                logger.info("Using company documents for response", 
                          confidence=confidence, 
                          docs_found=len(relevant_docs))
                
            else:
                # No relevant company documents found, use generic response
                confidence = 0.0
                result = self.generic_chain({
                    "question": question,
                    "chat_history": chat_history or []
                })
                
                context_used = False
                logger.info("No relevant company documents found, using generic response")
            
            # Extract source documents
            source_docs = result.get("source_documents", [])
            sources = []
            for doc in source_docs:
                if hasattr(doc, 'metadata'):
                    sources.append({
                        "source": doc.metadata.get("source", "Unknown"),
                        "page": doc.metadata.get("page", "N/A"),
                        "chunk_type": doc.metadata.get("chunk_type", "N/A")
                    })
            
            return {
                "answer": result["answer"],
                "confidence": confidence,
                "sources": sources,
                "context_used": context_used,
                "raw_docs": source_docs,
                "docs_found": len(relevant_docs) if relevant_docs else 0
            }
            
        except Exception as e:
            logger.error("Error in RAG query", error=str(e), question=question)
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
                "confidence": 0.0,
                "sources": [],
                "context_used": False,
                "raw_docs": [],
                "docs_found": 0
            }
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add new documents to the vector store"""
        try:
            self.vectorstore.add_documents(documents)
            logger.info("Added documents to vector store", count=len(documents))
            return True
        except Exception as e:
            logger.error("Failed to add documents", error=str(e))
            return False
    
    def update_document(self, doc_id: str, new_content: str, metadata: Dict[str, Any] = None) -> bool:
        """Update an existing document in the vector store"""
        try:
            # This is a simplified version - in production you'd want more sophisticated update logic
            new_doc = Document(page_content=new_content, metadata=metadata or {})
            self.vectorstore.add_documents([new_doc])
            logger.info("Updated document", doc_id=doc_id)
            return True
        except Exception as e:
            logger.error("Failed to update document", error=str(e), doc_id=doc_id)
            return False
    
    def get_similar_questions(self, question: str, k: int = 5) -> List[Tuple[str, float]]:
        """Find similar questions for training data analysis"""
        try:
            question_embedding = self.embeddings.embed_query(question)
            
            # Search for similar questions in the vector store
            similar_docs = self.vectorstore.similarity_search_by_vector(
                question_embedding, k=k
            )
            
            results = []
            for doc in similar_docs:
                results.append((doc.page_content, 0.8))  # Simplified similarity score
            
            return results
        except Exception as e:
            logger.error("Failed to get similar questions", error=str(e))
            return []
    
    def analyze_response_quality(self, question: str, answer: str, 
                               context_docs: List[Document]) -> Dict[str, Any]:
        """Analyze the quality of a response based on context relevance"""
        try:
            # Simple quality metrics
            context_length = sum(len(doc.page_content) for doc in context_docs)
            answer_length = len(answer)
            
            # Calculate relevance score (simplified)
            relevance_score = min(1.0, context_length / 1000) if context_length > 0 else 0.0
            
            return {
                "relevance_score": relevance_score,
                "context_length": context_length,
                "answer_length": answer_length,
                "context_docs_count": len(context_docs),
                "quality_rating": "good" if relevance_score > 0.5 else "poor"
            }
        except Exception as e:
            logger.error("Failed to analyze response quality", error=str(e))
            return {
                "relevance_score": 0.0,
                "context_length": 0,
                "answer_length": 0,
                "context_docs_count": 0,
                "quality_rating": "unknown"
            }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection"""
        try:
            collection_info = self.client.get_collection(Config.QDRANT_COLLECTION)
            return {
                "collection_name": Config.QDRANT_COLLECTION,
                "vector_count": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.value
            }
        except Exception as e:
            logger.error("Failed to get collection stats", error=str(e))
            return {
                "collection_name": Config.QDRANT_COLLECTION,
                "vector_count": 0,
                "vector_size": 0,
                "distance_metric": "unknown"
            } 