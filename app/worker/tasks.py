import asyncio

from app.worker.celery_app import celery_app
from app.database.session import AsyncSessionLocal
from app.embeddings.indexer import index_document_chunks


@celery_app.task(
    bind=True,
    name="process_document",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_document(
    self,
    document_id: int,
):
    """
    Background task for generating embeddings
    and indexing document chunks in FAISS.
    """

    return asyncio.run(
        _process_document(document_id)
    )


async def _process_document(
    document_id: int,
):
    async with AsyncSessionLocal() as db:

        await index_document_chunks(
            db=db,
            document_id=document_id,
        )

        return {
            "document_id": document_id,
            "status": "indexed",
        }