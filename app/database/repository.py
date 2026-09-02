from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Document, DocumentChunk

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Document, DocumentChunk


async def create_document(
    db: AsyncSession,
    filename: str,
) -> Document:

    document = Document(
        filename=filename,
    )

    db.add(document)

    await db.flush()

    return document


async def create_document_chunks(
    db: AsyncSession,
    document_id: int,
    chunks: list[str],
) -> list[DocumentChunk]:

    document_chunks = []

    for index, content in enumerate(chunks):

        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            content=content,
        )

        db.add(chunk)
        document_chunks.append(chunk)

    return document_chunks


async def get_document(
    db: AsyncSession,
    document_id: int,
) -> Document | None:

    result = await db.execute(
        select(Document).where(
            Document.id == document_id
        )
    )

    return result.scalar_one_or_none()


async def get_documents(
    db: AsyncSession,
) -> list[Document]:
    result = await db.execute(
        select(Document).order_by(Document.id.desc())
    )
    return list(result.scalars().all())


async def get_document_with_chunks(
    db: AsyncSession,
    document_id: int,
) -> Document | None:
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    return result.scalar_one_or_none()


async def delete_document(
    db: AsyncSession,
    document_id: int,
) -> bool:
    document = await get_document(
        db=db,
        document_id=document_id,
    )

    if document is None:
        return False

    await db.delete(document)
    await db.commit()

    return True
async def get_documents_paginated(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Document], int]:

    offset = (page - 1) * page_size

    # Get total document count
    count_result = await db.execute(
        select(func.count(Document.id))
    )

    total = count_result.scalar_one()

    # Get documents for current page
    result = await db.execute(
        select(Document)
        .order_by(Document.id.desc())
        .offset(offset)
        .limit(page_size)
    )

    documents = list(result.scalars().all())

    return documents, total