from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.service import llm_service
from app.retrieval.service import retrieve_chunks


async def answer_question(
    db: AsyncSession,
    question: str,
    top_k: int = 5,
) -> dict:

    # 1. Retrieve relevant chunks
    chunks = await retrieve_chunks(
        db=db,
        query=question,
        top_k=top_k,
    )

    if not chunks:
        return {
            "answer": "I could not find relevant information in the documents.",
            "sources": [],
        }

    # 2. Build context for the LLM
    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"[Chunk {chunk['chunk_id']}]\n"
            f"{chunk['content']}"
        )

    context = "\n\n".join(context_parts)

    # 3. Generate answer
    answer = await llm_service.generate_answer(
        question=question,
        context=context,
    )

    # 4. Return answer + sources
    sources = [
    {
        "chunk_id": chunk["chunk_id"],
        "document_id": chunk["document_id"],
        "filename": chunk["filename"],
        "chunk_index": chunk["chunk_index"],
        "score": chunk["score"],
    }
    for chunk in chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
    }