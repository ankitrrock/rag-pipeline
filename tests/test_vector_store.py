import numpy as np

from app.embeddings.vector_store import VectorStore


def test_vector_store_add_and_search():
    store = VectorStore(dimension=3)
    store.add(
        embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        chunk_ids=[10, 20],
    )

    results = store.search([1.0, 0.0, 0.0], top_k=1)

    assert len(results) == 1
    assert results[0]["chunk_id"] == 10
    assert np.isclose(results[0]["score"], 1.0)


def test_vector_store_contains_ids():
    store = VectorStore(dimension=2)
    store.add([[1.0, 0.0]], [5])

    assert store.contains_chunk_ids([5]) is True
    assert store.contains_chunk_ids([99]) is False
