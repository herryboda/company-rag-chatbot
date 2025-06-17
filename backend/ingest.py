import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

load_dotenv()

DATA_DIR = Path("data")
COLLECTION = os.getenv("QDRANT_COLLECTION", "company_policies")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

def load_docs() -> list:
    docs = []
    for path in DATA_DIR.rglob("*"):
        match path.suffix.lower():
            case ".pdf":
                docs.extend(PyPDFLoader(str(path)).load())
            case ".md" | ".markdown":
                docs.extend(UnstructuredMarkdownLoader(str(path)).load())
            case ".txt":
                docs.extend(TextLoader(str(path)).load())
    return docs

def main() -> None:
    docs = load_docs()
    print(f"Loaded {len(docs)} raw docs")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150, separators=["\n\n", "\n", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks")

    # --- Qdrant client -------------------------------------------------------
    client = QdrantClient(url=QDRANT_URL)

    # create collection if it doesn't exist
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )

    # --- LangChain VectorStore wrapper --------------------------------------
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    qdrant_store = Qdrant(
        client=client,
        collection_name=COLLECTION,
        embeddings=embeddings,
    )

    if chunks:
        qdrant_store.add_documents(chunks)
        print("✅ Vector store updated.")
    else:
        print("⚠️ No chunks to ingest (data folder empty).")

if __name__ == "__main__":
    main()
