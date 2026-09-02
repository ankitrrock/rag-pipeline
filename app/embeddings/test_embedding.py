from app.embeddings.service import embedding_service


text = "Python is a programming language."

embedding = embedding_service.embed_text(text)

print("Embedding dimension:", len(embedding))
print("First 10 values:", embedding[:10])