from app.embeddings.service import embedding_service
from app.embeddings.vector_store import VectorStore


texts = [
    "Python is a programming language.",
    "PostgreSQL is a relational database.",
    "FastAPI is a Python web framework.",
    "FAISS is used for vector similarity search.",
]

chunk_ids = [1, 2, 3, 4]


embeddings = embedding_service.embed_texts(texts)


vector_store = VectorStore(
    dimension=len(embeddings[0])
)


vector_store.add(
    embeddings=embeddings,
    chunk_ids=chunk_ids,
)


query = "What is used for vector similarity search?"

query_embedding = embedding_service.embed_text(
    query
)


results = vector_store.search(
    embedding=query_embedding,
    top_k=3,
)


print("\nSearch Results:")

for result in results:
    print(result)