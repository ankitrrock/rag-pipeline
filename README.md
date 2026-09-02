# RAG Pipeline API

A production-style Retrieval-Augmented Generation (RAG) backend built with **FastAPI, PostgreSQL, Redis, Celery, Sentence Transformers, FAISS, and OpenAI**.

The application accepts PDF documents, extracts and chunks their text, stores document metadata and chunks in PostgreSQL, generates semantic embeddings in a background Celery worker, stores vectors in FAISS, and answers natural-language questions using retrieved document context.

## Features

- PDF upload and text extraction with `pypdf`
- Sentence-based chunking with configurable overlap
- PostgreSQL persistence using SQLAlchemy AsyncIO
- Alembic database migrations
- Semantic embeddings with `all-MiniLM-L6-v2`
- Local FAISS vector index using cosine-style similarity via normalized inner product
- Redis as Celery broker/result backend
- Background document indexing with Celery
- RAG question answering with OpenAI
- Source/chunk metadata returned with every answer
- Paginated document listing
- Document deletion with vector cleanup
- Health-check scripts for Windows
- Pytest unit tests and GitHub Actions CI

## Architecture

```mermaid
flowchart TD
    Client[Client / Swagger / curl] --> API[FastAPI]

    API --> Upload[Document Upload API]
    API --> Query[Query API]
    API --> Docs[Document APIs]

    Upload --> PDF[PDF Text Extraction]
    PDF --> Chunk[Text Chunking]
    Chunk --> PG[(PostgreSQL)]
    Chunk --> Redis[(Redis)]
    Redis --> Celery[Celery Worker]
    Celery --> Embed[Sentence Transformer]
    Embed --> FAISS[(FAISS Vector Store)]

    Query --> EmbedQ[Query Embedding]
    EmbedQ --> FAISS
    FAISS --> Retrieve[Top-K Chunk Retrieval]
    Retrieve --> PG
    PG --> Context[Context Builder]
    Context --> LLM[OpenAI LLM]
    LLM --> Answer[Answer + Sources]
    Answer --> Client

    Docs --> PG
    Docs --> FAISS
```

## RAG Workflow

### Ingestion

```text
PDF upload
   ↓
Extract text
   ↓
Normalize and split into chunks
   ↓
Store document + chunks in PostgreSQL
   ↓
Queue Celery task
   ↓
Generate embeddings
   ↓
Store vectors + chunk IDs in FAISS
```

### Question answering

```text
User question
   ↓
Create query embedding
   ↓
FAISS similarity search
   ↓
Get top-K chunk IDs
   ↓
Load chunk/document metadata from PostgreSQL
   ↓
Build context
   ↓
Send context + question to OpenAI
   ↓
Return answer + source chunks
```

## Project Structure

```text
rag-pipeline/
├── .github/workflows/ci.yml
├── alembic/
│   └── versions/
├── app/
│   ├── api/
│   ├── database/
│   ├── embeddings/
│   ├── ingestion/
│   ├── llm/
│   ├── retrieval/
│   ├── schemas/
│   └── worker/
├── tests/
├── data/
│   ├── uploads/          # local runtime files, ignored by Git
│   └── vector_store/     # generated FAISS files, ignored by Git
├── .env.example
├── alembic.ini
├── check_project.bat
├── requirements.txt
├── start_project.bat
└── README.md
```

## Prerequisites

- Windows 10/11 or a compatible Linux/macOS environment
- Python 3.11 or 3.12 recommended
- PostgreSQL 18 (the included Windows script expects service `postgresql-x64-18`)
- Docker Desktop for Redis
- An OpenAI API key for `/api/v1/query`

## 1. Clone and create the environment

```bash
git clone https://github.com/ankitrrock/rag-pipeline.git
cd rag-pipeline

python -m venv env
env\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Configure environment variables

Copy `.env.example` to `.env` and set your real values.

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/rag_db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4o-mini
```

For backward compatibility, `DB_CONNECTION` is also accepted for the PostgreSQL connection string.

**Never commit `.env` or real API keys.**

## 3. PostgreSQL

Make sure PostgreSQL is installed and the database exists.

Windows service check:

```bat
sc query postgresql-x64-18
```

Start it if required:

```bat
net start postgresql-x64-18
```

Create the database if needed from `psql`:

```sql
CREATE DATABASE rag_db;
```

Run migrations:

```bash
alembic upgrade head
```

Check migration state:

```bash
alembic current
alembic history
```

## 4. Redis

This project uses Redis through Docker.

Start a Redis container:

```bash
docker run -d --name redis -p 6379:6379 redis
```

If the container already exists:

```bash
docker start redis
```

Verify Redis:

```bash
docker exec redis redis-cli ping
```

Expected:

```text
PONG
```

## 5. Celery worker

From the project root with the virtual environment activated:

```bash
python -m celery -A app.worker.celery_app.celery_app worker --loglevel=info --pool=solo
```

A successful worker should show:

```text
[tasks]
  . process_document

celery@... ready.
```

## 6. FastAPI

Start the API:

```bash
python -m uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

## 7. Start everything on Windows

The included script checks PostgreSQL, starts/checks the Redis Docker container, then opens Celery and FastAPI in separate terminals.

```bat
start_project.bat
```

Run the full local health check with:

```bat
check_project.bat
```

## API Reference

### Upload a PDF

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload" ^
  -H "accept: application/json" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@data/sample.pdf"
```

The endpoint stores the document/chunks and queues `process_document` for embedding and FAISS indexing.

Example response:

```json
{
  "message": "Document uploaded successfully. Processing started.",
  "document_id": 1,
  "filename": "sample.pdf"
}
```

### List documents

```bash
curl "http://127.0.0.1:8000/api/v1/documents?page=1&page_size=10"
```

### Get a document

```bash
curl "http://127.0.0.1:8000/api/v1/documents/1"
```

### Delete a document

```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/documents/1"
```

The delete operation removes both PostgreSQL document/chunk records and their corresponding FAISS vectors.

### Ask a RAG question

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What is this document about?\",\"top_k\":5}"
```

Example response shape:

```json
{
  "answer": "...",
  "sources": [
    {
      "chunk_id": 9,
      "document_id": 1,
      "filename": "sample.pdf",
      "chunk_index": 0,
      "score": 0.82
    }
  ]
}
```

## Error handling

The LLM layer converts common OpenAI failures into application-level `RuntimeError` messages. The query API maps those failures to HTTP `503 Service Unavailable`, including quota exhaustion, so an upstream OpenAI 429 does not become an uninformative internal server error.

A real API key with available quota is still required to generate an LLM answer.

## Vector Store

FAISS uses a 384-dimensional `IndexFlatIP` index because `all-MiniLM-L6-v2` produces 384-dimensional embeddings. Embeddings are normalized before indexing, so inner-product similarity behaves like cosine similarity.

The generated files are intentionally ignored by Git:

```text
data/vector_store/index.faiss
data/vector_store/chunk_ids.npy
```

They are local runtime artifacts and can be rebuilt from PostgreSQL with the indexer.

## Rebuild the FAISS index

```bash
python -c "import asyncio; from app.embeddings.indexer import build_vector_index; asyncio.run(build_vector_index())"
```

## Tests

Install the development dependencies from `requirements.txt`, then run:

```bash
pytest
```

Coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

The tests focus on deterministic application logic and mock external services such as OpenAI, Sentence Transformers, PostgreSQL, Redis, and FAISS where appropriate.

## CI/CD

GitHub Actions runs on pushes and pull requests. The workflow:

1. Sets up Python
2. Installs dependencies
3. Compiles the application to catch syntax errors
4. Runs pytest with coverage

Workflow file:

```text
.github/workflows/ci.yml
```

## Technology Stack

| Layer | Technology |
|---|---|
| API | FastAPI, Uvicorn |
| Validation | Pydantic |
| Database | PostgreSQL, SQLAlchemy AsyncIO |
| Migrations | Alembic |
| PDF | pypdf |
| Embeddings | Sentence Transformers |
| Vector Search | FAISS |
| Queue | Celery |
| Broker | Redis |
| LLM | OpenAI API |
| Testing | Pytest, pytest-asyncio, pytest-cov |
| CI | GitHub Actions |

## Future Improvements

- Replace the single local FAISS index with a distributed vector database for multi-instance deployments
- Add authentication and authorization
- Add document processing status tracking
- Add rate limiting and request IDs
- Add structured logging and metrics
- Add Docker Compose for the complete local stack
- Add streaming LLM responses
- Add hybrid keyword + semantic retrieval

## License

This project is provided for learning, portfolio, and demonstration purposes.
