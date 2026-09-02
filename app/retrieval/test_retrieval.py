import asyncio

from app.database.session import AsyncSessionLocal
from app.embeddings.indexer import build_vector_index
from app.retrieval.service import retrieve_chunks
from app.embeddings.vector_store import vector_store


async def main():

    # Build FAISS index

    vector_store.load()

    query = "What is this document about?"

    query = "What is this document about?"

    async with AsyncSessionLocal() as db:

        results = await retrieve_chunks(
            db=db,
            query=query,
            top_k=5,
        )

        print("\nRetrieved Chunks:\n")

        for result in results:

            print("=" * 80)

            print(f"Chunk ID: {result['chunk_id']}")
            print(f"Score: {result['score']:.4f}")
            print(f"Document ID: {result['document_id']}")
            print(f"Chunk Index: {result['chunk_index']}")

            print("\nContent:")
            print(result["content"])


if __name__ == "__main__":
    asyncio.run(main())