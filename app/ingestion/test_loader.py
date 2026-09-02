from app.ingestion.loader import extract_text_from_pdf


file_path = "data/sample.pdf"

text = extract_text_from_pdf(file_path)

print("Extracted characters:", len(text))
print()
print(text[:2000])