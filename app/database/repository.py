from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Document, DocumentChunk


async def create_document(db: AsyncSession, filename: str) -> Document:
    document = Document(filename=filename)
    db.add(document)
    await db.flush()
    return document


async def create_document_chunks(
    db: AsyncSession,
    document_id: int,
    chunks: list[str],
) -> list[DocumentChunk]:
    document_chunks = [
        DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            content=content,
        )
        for index, content in enumerate(chunks)
    ]
    db.add_all(document_chunks)
    await db.flush()
    return document_chunks


async def get_document(db: AsyncSession, document_id: int) -> Document | None:
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    return result.scalar_one_or_none()


async def get_documents(db: AsyncSession) -> list[Document]:
    result = await db.execute(
        select(Document).order_by(Document.id.desc())
    )
    return list(result.scalars().all())


async def get_document_with_chunks(
    db: AsyncSession,
    document_id: int,
) -> Document | None:
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.chunks))
        .where(Document.id == document_id)
    )
    return result.scalar_one_or_none()


async def delete_document(db: AsyncSession, document_id: int) -> bool:
    document = await get_document(db=db, document_id=document_id)
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

    count_result = await db.execute(select(func.count(Document.id)))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Document)
        .order_by(Document.id.desc())
        .offset(offset)
        .limit(page_size)
    )
    return list(result.scalars().all()), total
