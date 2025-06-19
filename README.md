# Enhanced Company RAG Chatbot
A sophisticated Retrieval-Augmented Generation (RAG) chatbot designed for company policy assistance with advanced self-training capabilities, human-like responses, and comprehensive monitoring.

## 🚀 Key Features

### Enhanced RAG System
- **Advanced Context Management**: Intelligent document chunking and retrieval
- **Confidence Scoring**: Real-time confidence assessment for responses
- **Source Tracking**: Detailed source attribution for all answers
- **Multi-format Support**: PDF, TXT, MD, CSV, DOCX, DOC files

### Self-Training Capabilities
- **Conversation Learning**: Automatically learns from user interactions
- **Feedback Integration**: User feedback drives continuous improvement
- **Pattern Analysis**: Identifies common question types and response patterns
- **Quality Assessment**: Analyzes response quality and suggests improvements

### Human-like Responses
- **Enhanced Prompts**: Custom prompts for more natural conversations
- **Contextual Awareness**: Maintains conversation context across sessions
- **Emotional Intelligence**: Appropriate use of emojis and friendly language
- **Professional Tone**: Balances friendliness with professionalism

### Advanced Monitoring
- **Real-time Analytics**: Comprehensive dashboard with system metrics
- **Training Reports**: Detailed analysis of conversation patterns
- **Improvement Suggestions**: AI-powered recommendations for system enhancement
- **Health Monitoring**: System status and component health tracking

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Data Layer    │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Qdrant)      │
│                 │    │                 │    │   (Redis)       │
│ • Enhanced Chat │    │ • Enhanced RAG  │    │                 │
│ • Admin Dashboard│   │ • Self Training │    │                 │
│ • Feedback UI   │    │ • Memory Mgmt   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons
- **Backend**: FastAPI, Python 3.11
- **AI/ML**: LangChain, OpenAI GPT-4, OpenAI Embeddings
- **Vector Database**: Qdrant
- **Session Management**: Redis
- **Document Processing**: PyPDF, Unstructured
- **Analytics**: scikit-learn, numpy, pandas

## 📋 Prerequisites

- Docker and Docker Compose
- OpenAI API key
- At least 4GB RAM available

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd company-rag-chatbot
```

### 2. Set Up Environment Variables
Create a `.env` file in the `backend` directory:
```bash
cd backend
cp .env.example .env
```

Edit the `.env` file with your configuration:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=company_policies
REDIS_URL=redis://redis:6379
ENABLE_SELF_TRAINING=true
FEEDBACK_COLLECTION_ENABLED=true
TEMPERATURE=0.7
MIN_CONFIDENCE_THRESHOLD=0.8
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
TOP_K_RETRIEVAL=6
SIMILARITY_THRESHOLD=0.7
MAX_HISTORY_LENGTH=10
LOG_LEVEL=INFO
```

### 3. Add Your Documents
Place your company policy documents in the `data/` directory:
```bash
# Supported formats: PDF, TXT, MD, CSV, DOCX, DOC
cp your_policies/* data/
```

### 4. Start the Application
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 5. Access the Application
- **Chat Interface**: http://localhost
- **Admin Dashboard**: http://localhost (click "Admin" tab)
- **API Documentation**: http://localhost:8000/docs

## 📚 Usage Guide

### For End Users

1. **Start a Conversation**: Ask questions about company policies
2. **View Confidence**: Check the confidence score for each response
3. **Review Sources**: See which documents were used for the answer
4. **Provide Feedback**: Rate responses to help improve the system

### For Administrators

1. **Monitor System Health**: Check the Overview tab for system status
2. **Review Training Data**: Analyze conversation patterns and quality metrics
3. **View Suggestions**: Get AI-powered improvement recommendations
4. **Export Data**: Download training reports and feedback data

## 🔧 Configuration Options

### RAG Configuration
- `CHUNK_SIZE`: Size of document chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 150)
- `TOP_K_RETRIEVAL`: Number of relevant documents to retrieve (default: 6)
- `SIMILARITY_THRESHOLD`: Minimum similarity score (default: 0.7)

### Training Configuration
- `ENABLE_SELF_TRAINING`: Enable/disable self-training (default: true)
- `FEEDBACK_COLLECTION_ENABLED`: Enable/disable feedback collection (default: true)
- `MIN_CONFIDENCE_THRESHOLD`: Minimum confidence for high-quality responses (default: 0.8)

### Conversation Configuration
- `TEMPERATURE`: LLM creativity level (default: 0.7)
- `MAX_HISTORY_LENGTH`: Maximum conversation history length (default: 10)

## 📊 API Endpoints

### Chat Endpoints
- `POST /chat` - Send a message and get response
- `POST /feedback` - Submit user feedback

### Training Endpoints
- `GET /training/report` - Get comprehensive training report
- `GET /training/suggestions` - Get improvement suggestions
- `GET /training/examples` - Get high-quality training examples

### System Endpoints
- `GET /health` - System health status
- `DELETE /session/{session_id}` - Clear specific session

## 🔍 Monitoring and Analytics

### System Health
- Component status monitoring
- Performance metrics
- Error tracking and logging

### Training Analytics
- Conversation pattern analysis
- Question type categorization
- Answer quality assessment
- Feedback score analysis

### Improvement Suggestions
- Context improvement recommendations
- Question type optimization
- Feedback-based improvements

## 🚀 Advanced Features

### Self-Training Pipeline
1. **Data Collection**: Automatically collects conversation data
2. **Pattern Analysis**: Identifies common questions and response patterns
3. **Quality Assessment**: Evaluates response quality and specificity
4. **Improvement Suggestions**: Generates actionable recommendations

### Enhanced Document Processing
- **Smart Chunking**: Different strategies for different document types
- **Metadata Extraction**: Rich metadata for better context
- **Quality Validation**: Filters out low-quality chunks
- **Multi-format Support**: Handles various document formats

### Memory Management
- **Session Persistence**: Maintains conversation context
- **Redis Integration**: Scalable session storage
- **Automatic Cleanup**: Manages memory efficiently

## 🛡️ Security Considerations

- API key management through environment variables
- CORS configuration for frontend-backend communication
- Input validation and sanitization
- Error handling without exposing sensitive information

## 🔧 Development

### Local Development Setup
```bash
# Backend development
cd backend
pip install -r requirements.txt
python enhanced_api.py

# Frontend development
cd frontend
npm install
npm run dev
```

### Adding New Features
1. **Backend**: Add new endpoints in `enhanced_api.py`
2. **Frontend**: Create new components in `src/components/`
3. **RAG**: Extend `EnhancedRAG` class for new capabilities
4. **Training**: Add new analysis methods in `SelfTrainingManager`

## 📈 Performance Optimization

### Vector Database
- Optimized chunk sizes for different content types
- Efficient similarity search with score thresholds
- Proper indexing for fast retrieval

### Memory Management
- Redis for session storage
- Automatic cleanup of old sessions
- Efficient conversation history management

### Response Quality
- Confidence scoring for response reliability
- Context validation before generating responses
- Fallback mechanisms for error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the documentation
2. Review the admin dashboard for system status
3. Check the logs for error details
4. Open an issue on GitHub

## 🔄 Updates and Maintenance

### Regular Maintenance
- Monitor system health through admin dashboard
- Review training reports for improvement opportunities
- Update documents in the data directory as needed
- Check for new dependencies and security updates

### Scaling Considerations
- Increase Redis memory for high-traffic scenarios
- Scale Qdrant resources for large document collections
- Consider load balancing for multiple backend instances
- Monitor API rate limits for OpenAI services

---

**Enhanced Company RAG Chatbot v2.0** - Making company policy assistance intelligent, human-like, and continuously improving! 🚀
