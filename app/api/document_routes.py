from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import (
    delete_document,
    get_document_with_chunks,
    get_documents_paginated,
)
from app.database.session import get_db
from app.ingestion.service import ingest_pdf
from app.schemas.document import (
    DocumentDetailResponse,
    DocumentResponse,
    PaginatedDocumentResponse,
    DocumentUploadResponse,
)
from app.embeddings.vector_store import vector_store
from app.worker.tasks import process_document



router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    file_path = (
        UPLOAD_DIR
        / f"{uuid4()}_{file.filename}"
    )

    try:
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        file_path.write_bytes(content)

        # 1. Extract PDF text
        # 2. Create chunks
        # 3. Store document + chunks in PostgreSQL
        document_id = await ingest_pdf(
            db=db,
            file_path=str(file_path),
        )

        # Queue embedding generation + FAISS indexing
        process_document.delay(document_id)

        return {
            "message": "Document uploaded successfully. Processing started.",
            "document_id": document_id,
            "filename": file.filename,
        }


    except HTTPException:
        raise

    except ValueError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to process the document.",
        ) from exc


@router.get(
    "",
    response_model=PaginatedDocumentResponse,
)
async def list_documents(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of documents per page",
    ),
    db: AsyncSession = Depends(get_db),
):
    documents, total = await get_documents_paginated(
        db=db,
        page=page,
        page_size=page_size,
    )

    return {
        "items": documents,
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
)
async def get_document_details(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    document = await get_document_with_chunks(
        db=db,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "created_at": document.created_at,
        "chunk_count": len(document.chunks),
    }


@router.delete(
    "/{document_id}",
)
async def remove_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    document = await get_document_with_chunks(
        db=db,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    chunk_ids = [
        chunk.id
        for chunk in document.chunks
    ]

    # Remove vectors from FAISS
    vector_store.remove_chunk_ids(chunk_ids)

    # Remove document and chunks from PostgreSQL
    deleted = await delete_document(
        db=db,
        document_id=document_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document.",
        )

    return {
        "message": "Document and its vectors deleted successfully.",
        "document_id": document_id,
        "deleted_chunks": len(chunk_ids),
    }