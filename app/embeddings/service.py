from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        return self._model

    def embed_text(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        if hasattr(embedding, "tolist"):
            return embedding.tolist()

        return list(embedding)

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        if hasattr(embeddings, "tolist"):
            return embeddings.tolist()

        return [list(embedding) for embedding in embeddings]


embedding_service = EmbeddingService()