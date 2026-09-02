import asyncio

from app.database.session import AsyncSessionLocal
from app.embeddings.vector_store import vector_store
from app.llm.rag_service import answer_question


async def main():

    # Load persisted FAISS index
    vector_store.load()

    question = "What is this document about?"

    async with AsyncSessionLocal() as db:

        result = await answer_question(
            db=db,
            question=question,
            top_k=5,
        )

        print("\nAnswer:")
        print(result["answer"])

        print("\nSources:")

        for source in result["sources"]:

            print(
                f"Chunk ID: {source['chunk_id']} | "
                f"Document ID: {source['document_id']} | "
                f"Score: {source['score']:.4f}"
            )


if __name__ == "__main__":
    asyncio.run(main())