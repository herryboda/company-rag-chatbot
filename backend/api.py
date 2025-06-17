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

COLLECTION = os.getenv("QDRANT_COLLECTION", "company_policies")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

app = FastAPI(title="Company RAG Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    answer: str

SMALL_TALK = {
    "thanks": "You're welcome! 😊",
    "thank you": "You're welcome!",
    "makes sense": "Glad to hear that!",
    "cool": "😎",
    "okay": "👍",
    "ok": "👌",
    "got it": "Great!",
    "great": "Awesome!",
    "nice": "😄",
    "bye": "Goodbye! 👋",
    "hello": "Hi there! 👋",
    "hi": "Hey! 👋",
}

def make_chain():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    client = QdrantClient(url=QDRANT_URL)

    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )

    vectorstore = Qdrant(
        client=client,
        collection_name=COLLECTION,
        embeddings=embeddings,
    )

    llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

    return ConversationalRetrievalChain.from_llm(
        llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 6}),
        return_source_documents=False,
    )

chain = make_chain()
_sessions: dict[str, list[tuple[str, str]]] = {}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    sid = req.session_id or str(uuid.uuid4())
    history = _sessions.setdefault(sid, [])

    message_lower = req.message.strip().lower()
    if message_lower in SMALL_TALK:
        answer = SMALL_TALK[message_lower]
        history.append((req.message, answer))
        return ChatResponse(session_id=sid, answer=answer)

    try:
        result = chain({"question": req.message, "chat_history": history})
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    answer = result["answer"]
    history.append((req.message, answer))
    return ChatResponse(session_id=sid, answer=answer)
