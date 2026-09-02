from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import DocumentChunk,Document
from app.embeddings.service import embedding_service
from app.embeddings.vector_store import vector_store


async def retrieve_chunks(
    db: AsyncSession,
    query: str,
    top_k: int = 5,
) -> list[dict]:

    query_embedding = embedding_service.embed_text(query)

    search_results = vector_store.search(
        embedding=query_embedding,
        top_k=top_k,
    )

    if not search_results:
        return []

    chunk_ids = [
        result["chunk_id"]
        for result in search_results
    ]

    result = await db.execute(
        select(DocumentChunk, Document)
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(DocumentChunk.id.in_(chunk_ids))
    )

    rows = result.all()

    chunk_map = {
        chunk.id: (chunk, document)
        for chunk, document in rows
    }

    retrieved_chunks = []

    for search_result in search_results:

        chunk_id = search_result["chunk_id"]

        item = chunk_map.get(chunk_id)

        if item is None:
            continue

        chunk, document = item

        retrieved_chunks.append({
            "chunk_id": chunk.id,
            "content": chunk.content,
            "score": search_result["score"],
            "document_id": chunk.document_id,
            "filename": document.filename,
            "chunk_index": chunk.chunk_index,
        })

    return retrieved_chunks