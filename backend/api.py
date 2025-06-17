import os, uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.chains import ConversationalRetrievalChain

load_dotenv()

# ─────────── Config ───────────
COLLECTION = os.getenv("QDRANT_COLLECTION", "company_policies")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

# ─────────── FastAPI app ───────────
app = FastAPI(title="Company RAG Chatbot")

# Enable CORS so frontend can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────── Request/Response models ───────────
class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    answer: str

# ─────────── Chain Initialization ───────────
def make_chain():
    # Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Qdrant client
    client = QdrantClient(url=QDRANT_URL)

    # Ensure collection exists
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )

    # LangChain vector store wrapper
    vectorstore = Qdrant(
        client=client,
        collection_name=COLLECTION,
        embeddings=embeddings,
    )

    # Chat LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

    # Retrieval-augmented chain
    return ConversationalRetrievalChain.from_llm(
        llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 6}),
        return_source_documents=False,
    )

chain = make_chain()
_sessions: dict[str, list[tuple[str, str]]] = {}

# ─────────── Chat endpoint ───────────
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    sid = req.session_id or str(uuid.uuid4())
    history = _sessions.setdefault(sid, [])

    try:
        result = chain({"question": req.message, "chat_history": history})
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    answer = result["answer"]
    history.append((req.message, answer))
    return ChatResponse(session_id=sid, answer=answer)
