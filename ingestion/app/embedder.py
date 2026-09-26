# Embeddings: turn text/chunks into fixed-size numeric vectors.

import math
import zlib
from abc import ABC, abstractmethod


class Embedder(ABC):
    """Common interface for embedding providers."""

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Return a vector of length self.dimensions."""
        raise NotImplementedError

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


class HashEmbedder(Embedder):
    """Deterministic, offline embedder for dev/tests.
    Hashes tokens into coordinates. NOT for production ranking."""

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.split():
            h = zlib.crc32(token.encode("utf-8")) & 0x7FFFFFFF
            vector[h % self.dimensions] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class ProviderEmbedder(Embedder):
    """Real provider adapter is implemented in `ai/providers/gemini_embed.py`.

    This legacy interface remains a placeholder for callers that still construct
    an ingestion-local embedder; production ingestion uses the shared provider.
    """

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError(
            "Provider embedding requires provider wiring + credentials"
        )
