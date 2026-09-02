import asyncio

from app.database.session import AsyncSessionLocal
from app.ingestion.service import ingest_pdf


async def main():

    async with AsyncSessionLocal() as db:

        document_id = await ingest_pdf(
            db=db,
            file_path="data/sample.pdf",
        )

        print(
            f"Document inserted successfully. "
            f"ID = {document_id}"
        )


if __name__ == "__main__":
    asyncio.run(main())