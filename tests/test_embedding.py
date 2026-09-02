from app.embeddings.service import EmbeddingService


def test_embedding_service_with_mocked_model():
    service = EmbeddingService()

    class FakeModel:
        def encode(self, text_or_texts, normalize_embeddings=True):
            assert normalize_embeddings is True
            if isinstance(text_or_texts, str):
                return [0.1, 0.2, 0.3]
            return [[0.1, 0.2, 0.3] for _ in text_or_texts]

    service._model = FakeModel()

    assert service.embed_text("hello") == [0.1, 0.2, 0.3]
    assert service.embed_texts(["a", "b"]) == [
        [0.1, 0.2, 0.3],
        [0.1, 0.2, 0.3],
    ]
