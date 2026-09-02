from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    filename: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(BaseModel):
    id: int
    filename: str
    created_at: datetime
    chunk_count: int

    model_config = ConfigDict(from_attributes=True)


class PaginatedDocumentResponse(BaseModel):
    items: list[DocumentResponse]
    page: int
    page_size: int
    total: int


class DocumentUploadResponse(BaseModel):
    message: str
    document_id: int
    filename: str