import re


def split_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:

    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    # Split into sentences
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    chunks = []
    current_chunk = ""

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        # If adding the sentence stays within the limit
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk = (
                f"{current_chunk} {sentence}"
            ).strip()

        else:
            if current_chunk:
                chunks.append(current_chunk)

            # Start the next chunk with overlap
            overlap_text = current_chunk[-chunk_overlap:]

            current_chunk = (
                f"{overlap_text} {sentence}"
            ).strip()

            # Prevent extremely long single sentences
            if len(current_chunk) > chunk_size:
                current_chunk = current_chunk[:chunk_size]

    if current_chunk:
        chunks.append(current_chunk)

    return chunks