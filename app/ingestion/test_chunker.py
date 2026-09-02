from app.ingestion.loader import extract_text_from_pdf
from app.ingestion.chunker import split_text


text = extract_text_from_pdf("data/sample.pdf")

chunks = split_text(
    text,
    chunk_size=1000,
    chunk_overlap=200,
)

print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks[:3]):
    print("\n" + "=" * 60)
    print(f"CHUNK {index + 1}")
    print("=" * 60)
    print(chunk)