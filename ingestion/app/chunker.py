# Chunking: split cleaned text into retrieval-sized pieces with overlap.
#
# Overlap preserves context across chunk boundaries for later retrieval.

def split_chunks(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Split whitespace-normalised text into word-bounded chunks.

    size    - target number of words per chunk
    overlap - words shared between consecutive chunks
    """
    words = text.split()
    if not words:
        return []

    step = max(size - overlap, 1)
    chunks = []
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks
