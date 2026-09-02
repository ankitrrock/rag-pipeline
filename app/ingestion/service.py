from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import (
    create_document,
    create_document_chunks,
)
from app.ingestion.chunker import split_text
from app.ingestion.loader import extract_text_from_pdf


async def ingest_pdf(
    db: AsyncSession,
    file_path: str,
) -> int:

    path = Path(file_path)

    # 1. Extract PDF text
    text = extract_text_from_pdf(file_path)

    if not text.strip():
        raise ValueError(
            "No text could be extracted from the PDF."
        )

    # 2. Split text into chunks
    chunks = split_text(
        text,
        chunk_size=1000,
        chunk_overlap=200,
    )

    if not chunks:
        raise ValueError(
            "No chunks were generated."
        )

    try:
        # 3. Create document
        document = await create_document(
            db=db,
            filename=path.name,
        )

        # 4. Create chunks
        await create_document_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
        )

        # 5. Commit document + chunks
        await db.commit()

        return document.id

    except Exception:
        await db.rollback()
        raise