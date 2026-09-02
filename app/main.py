from fastapi import FastAPI

from app.api.document_routes import router as document_router
from app.api.routes import router as rag_router
from app.embeddings.vector_store import vector_store


app = FastAPI(
    title="RAG Pipeline API",
    description="Document-based Retrieval-Augmented Generation API",
    version="1.0.0",
)


app.include_router(rag_router)
app.include_router(document_router)


@app.on_event("startup")
async def startup_event():

    vector_store.load()


@app.get("/")
async def root():

    return {
        "message": "RAG Pipeline API is running"
    }


@app.get("/health")
async def health_check():

    return {
        "status": "healthy"
    }