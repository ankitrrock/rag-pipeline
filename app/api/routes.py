from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.llm.rag_service import answer_question
from app.schemas.query import QueryRequest, QueryResponse


router = APIRouter(
    prefix="/api/v1",
    tags=["RAG"],
)


@router.post(
    "/query",
    response_model=QueryResponse,
)
async def query_documents(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
):

    try:

        result = await answer_question(
            db=db,
            question=request.question,
            top_k=request.top_k,
        )

        return result

    except RuntimeError as exc:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc