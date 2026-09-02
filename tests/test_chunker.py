import pytest

from app.ingestion.chunker import split_text


def test_split_text_returns_empty_for_blank_input():
    assert split_text("   ") == []


def test_split_text_creates_chunks():
    text = "First sentence. Second sentence. Third sentence."
    chunks = split_text(text, chunk_size=30, chunk_overlap=5)
    assert chunks
    assert all(chunk.strip() for chunk in chunks)


def test_split_text_rejects_invalid_overlap():
    with pytest.raises(ValueError, match="smaller than chunk_size"):
        split_text("hello", chunk_size=10, chunk_overlap=10)
