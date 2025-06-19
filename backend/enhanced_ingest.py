import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import structlog

from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, UnstructuredMarkdownLoader,
    UnstructuredFileLoader, CSVLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import Config
from enhanced_rag import EnhancedRAG

logger = structlog.get_logger()

class EnhancedDocumentProcessor:
    def __init__(self):
        self.rag_system = EnhancedRAG()
        self.supported_extensions = {
            '.pdf': PyPDFLoader,
            '.txt': TextLoader,
            '.md': UnstructuredMarkdownLoader,
            '.markdown': UnstructuredMarkdownLoader,
            '.csv': CSVLoader,
            '.docx': UnstructuredFileLoader,
            '.doc': UnstructuredFileLoader,
        }
        
    def load_documents(self, data_dir: Path) -> List[Document]:
        """Load documents from the data directory with enhanced processing"""
        documents = []
        
        for file_path in data_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    logger.info("Processing file", file_path=str(file_path))
                    
                    # Load document based on file type
                    loader_class = self.supported_extensions[file_path.suffix.lower()]
                    loader = loader_class(str(file_path))
                    docs = loader.load()
                    
                    # Enhance documents with metadata
                    for doc in docs:
                        doc.metadata.update({
                            "source": file_path.name,
                            "file_path": str(file_path),
                            "file_type": file_path.suffix.lower(),
                            "file_size": file_path.stat().st_size,
                            "ingestion_date": datetime.utcnow().isoformat(),
                            "document_id": self._generate_document_id(doc.page_content, file_path.name)
                        })
                    
                    documents.extend(docs)
                    logger.info("Successfully loaded document", 
                              file_path=str(file_path), 
                              pages=len(docs))
                    
                except Exception as e:
                    logger.error("Failed to load document", 
                               file_path=str(file_path), 
                               error=str(e))
        
        return documents
    
    def _generate_document_id(self, content: str, filename: str) -> str:
        """Generate a unique document ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{filename}_{content_hash[:8]}"
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents with enhanced chunking strategy"""
        # Create different splitters for different content types
        splitters = {
            "default": RecursiveCharacterTextSplitter(
                chunk_size=Config.CHUNK_SIZE,
                chunk_overlap=Config.CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", " ", ""]
            ),
            "policy": RecursiveCharacterTextSplitter(
                chunk_size=1500,  # Larger chunks for policy documents
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " ", ""]
            ),
            "procedure": RecursiveCharacterTextSplitter(
                chunk_size=1200,  # Medium chunks for procedures
                chunk_overlap=150,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
        }
        
        all_chunks = []
        
        for doc in documents:
            # Determine splitter based on content and file type
            splitter = self._select_splitter(doc, splitters)
            
            try:
                chunks = splitter.split_documents([doc])
                
                # Add chunk metadata
                for i, chunk in enumerate(chunks):
                    chunk.metadata.update({
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "chunk_type": self._determine_chunk_type(chunk.page_content),
                        "word_count": len(chunk.page_content.split()),
                        "splitter_used": "policy" if splitter == splitters["policy"] else 
                                       "procedure" if splitter == splitters["procedure"] else "default"
                    })
                
                all_chunks.extend(chunks)
                logger.info("Split document", 
                          source=doc.metadata.get("source"),
                          chunks=len(chunks))
                
            except Exception as e:
                logger.error("Failed to split document", 
                           source=doc.metadata.get("source"), 
                           error=str(e))
        
        return all_chunks
    
    def _select_splitter(self, doc: Document, splitters: Dict[str, Any]) -> Any:
        """Select appropriate splitter based on document content and type"""
        content_lower = doc.page_content.lower()
        file_type = doc.metadata.get("file_type", "")
        
        # Policy documents
        if any(keyword in content_lower for keyword in ["policy", "policies", "regulation", "rule"]):
            return splitters["policy"]
        
        # Procedure documents
        if any(keyword in content_lower for keyword in ["procedure", "process", "step", "guideline"]):
            return splitters["procedure"]
        
        # Default splitter
        return splitters["default"]
    
    def _determine_chunk_type(self, content: str) -> str:
        """Determine the type of content in a chunk"""
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ["policy", "policies", "regulation"]):
            return "policy"
        elif any(keyword in content_lower for keyword in ["procedure", "process", "step"]):
            return "procedure"
        elif any(keyword in content_lower for keyword in ["contact", "email", "phone"]):
            return "contact_info"
        elif any(keyword in content_lower for keyword in ["table", "list", "item"]):
            return "structured_data"
        else:
            return "general"
    
    def validate_chunks(self, chunks: List[Document]) -> List[Document]:
        """Validate and filter chunks based on quality criteria"""
        valid_chunks = []
        
        for chunk in chunks:
            # Skip chunks that are too short
            if len(chunk.page_content.strip()) < 50:
                continue
            
            # Skip chunks that are mostly whitespace or special characters
            if len(chunk.page_content.strip()) / len(chunk.page_content) < 0.8:
                continue
            
            # Skip chunks that are mostly numbers or symbols
            alpha_ratio = sum(c.isalpha() for c in chunk.page_content) / len(chunk.page_content)
            if alpha_ratio < 0.3:
                continue
            
            valid_chunks.append(chunk)
        
        logger.info("Chunk validation", 
                   total_chunks=len(chunks), 
                   valid_chunks=len(valid_chunks))
        
        return valid_chunks
    
    def ingest_documents(self, data_dir: Path) -> bool:
        """Complete document ingestion pipeline"""
        try:
            logger.info("Starting document ingestion", data_dir=str(data_dir))
            
            # Load documents
            documents = self.load_documents(data_dir)
            if not documents:
                logger.warning("No documents found to ingest")
                return False
            
            logger.info("Loaded documents", count=len(documents))
            
            # Split documents
            chunks = self.split_documents(documents)
            logger.info("Split documents into chunks", count=len(chunks))
            
            # Validate chunks
            valid_chunks = self.validate_chunks(chunks)
            logger.info("Validated chunks", count=len(valid_chunks))
            
            # Add to vector store
            if valid_chunks:
                success = self.rag_system.add_documents(valid_chunks)
                if success:
                    logger.info("Successfully ingested documents", 
                              total_chunks=len(valid_chunks))
                    return True
                else:
                    logger.error("Failed to add documents to vector store")
                    return False
            else:
                logger.warning("No valid chunks to ingest")
                return False
                
        except Exception as e:
            logger.error("Document ingestion failed", error=str(e))
            return False

def main():
    """Main ingestion function"""
    data_dir = Path(Config.DATA_DIR)
    
    if not data_dir.exists():
        logger.error("Data directory does not exist", data_dir=str(data_dir))
        return
    
    processor = EnhancedDocumentProcessor()
    success = processor.ingest_documents(data_dir)
    
    if success:
        logger.info("✅ Document ingestion completed successfully")
    else:
        logger.error("❌ Document ingestion failed")

if __name__ == "__main__":
    main() 