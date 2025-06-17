# Company AI Chatbot (RAG)

This project is a Retrieval-Augmented Generation (RAG) chatbot to answer employee questions about company policies, SOPs, and documentation.

## 🛠 Prerequisites

- Docker + Docker Compose
- OpenAI API key

## 📂 Structure

- `backend/` – FastAPI server for chat + document ingestion
- `frontend/` – React UI
- `data/` – Folder for policy PDFs/Markdown/TXT files

## 🚀 Setup Instructions

1. Clone the repo and enter the project directory:

```bash
git clone <REPO>
cd company-rag-chatbot
```

2. Drop documents (PDF, .txt, .md) into the `data/` folder.

3. Set your OpenAI API key in `backend/.env`:

```bash
cp backend/.env.example backend/.env
# Then edit and add your OpenAI API key
```

4. Run ingestion to embed company docs into Qdrant:

```bash
docker compose run --rm backend python ingest.py
```

5. Start the full stack:

```bash
docker compose up --build
```

6. Open your browser to: [http://localhost](http://localhost)

## ✅ Features

- RAG pipeline (LangChain + Qdrant + OpenAI)
- Supports PDF, Markdown, and Text
- Clean UI with Tailwind + React
- Session memory for multi-turn chats

---
