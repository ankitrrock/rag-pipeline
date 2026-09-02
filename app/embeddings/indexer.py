from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import DocumentChunk
from app.database.session import AsyncSessionLocal
from app.embeddings.service import embedding_service
from app.embeddings.vector_store import vector_store


async def index_document_chunks(
    db: AsyncSession,
    document_id: int,
):
    result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    )

    chunks = result.scalars().all()

    if not chunks:
        print(f"No chunks found for document {document_id}.")
        return

    # Only index chunks that are not already in FAISS
    new_chunks = [
        chunk
        for chunk in chunks
        if not vector_store.contains_chunk_ids([chunk.id])
    ]

    if not new_chunks:
        print(
            f"Document {document_id} is already indexed."
        )
        return

    texts = [chunk.content for chunk in new_chunks]
    chunk_ids = [chunk.id for chunk in new_chunks]

    print(
        f"Generating embeddings for {len(texts)} chunks..."
    )

    embeddings = embedding_service.embed_texts(texts)

    vector_store.add(
        embeddings=embeddings,
        chunk_ids=chunk_ids,
    )

    vector_store.save()

    print(
        f"Document {document_id} indexed successfully. "
        f"Added {len(chunk_ids)} vectors."
    )


async def build_vector_index():
    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(DocumentChunk)
            .order_by(DocumentChunk.id)
        )

        chunks = result.scalars().all()

        if not chunks:
            print("No chunks found in database.")
            return

        # Only index chunks missing from FAISS
        new_chunks = [
            chunk
            for chunk in chunks
            if not vector_store.contains_chunk_ids([chunk.id])
        ]

        if not new_chunks:
            print("All document chunks are already indexed.")
            return

        texts = [chunk.content for chunk in new_chunks]
        chunk_ids = [chunk.id for chunk in new_chunks]

        print(
            f"Generating embeddings for {len(texts)} chunks..."
        )

        embeddings = embedding_service.embed_texts(texts)

        vector_store.add(
            embeddings=embeddings,
            chunk_ids=chunk_ids,
        )

        vector_store.save()

        print(
            f"Indexed {len(chunk_ids)} chunks successfully."
        )