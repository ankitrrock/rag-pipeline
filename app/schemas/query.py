from pydantic import BaseModel, Field


class QueryRequest(BaseModel):

    question: str = Field(
        min_length=1,
        description="Question to ask about the documents",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of relevant chunks to retrieve",
    )


class Source(BaseModel):
    chunk_id: int
    document_id: int
    filename: str
    chunk_index: int
    score: float


class QueryResponse(BaseModel):

    answer: str
    sources: list[Source]