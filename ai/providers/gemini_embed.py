# Gemini text embeddings via the public Generative Language API.
#
# Security invariant (same as the chat provider): the API key travels ONLY in
# the x-goog-api-key header, never in the URL or query string.
#
# Default model: text-embedding-004 (free tier, 768 dims). "gemini-embedding-001"
# is a recent alternative; both accept the same REST contract.

import logging
from typing import Any

import httpx

from ai.providers import ProviderError

logger = logging.getLogger(__name__)

EMBED_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"
# Default model: verified live on the free tier (ListModels returned
# gemini-embedding-001 / gemini-embedding-2 / gemini-embedding-2-preview as
# embedContent-capable for this project).
DEFAULT_MODEL = "gemini-embedding-2"
_DIMS = 768


def _raise_for_status(response: httpx.Response) -> None:
    if 200 <= response.status_code < 300:
        return
    try:
        payload = response.json()
        error = (payload.get("error") or {}).get("message") or "unknown error"
    except Exception:
        error = response.text[:200]
    if response.status_code == 400 or response.status_code == 404:
        raise ProviderError(f"Embedding provider rejected the request: {error}")
    if response.status_code == 401 or response.status_code == 403:
        raise ProviderError(f"Embedding provider authentication failed: {error}")
    if response.status_code == 429:
        raise ProviderError("Embedding provider rate limit exceeded")
    raise ProviderError(f"Embedding provider unavailable ({response.status_code}): {error}")


class GeminiEmbedder:
    """Small, typed wrapper around Gemini's embedContent/batchEmbedContents.

    Injectable `transport` lets tests stub network calls; without one we use a
    real httpx.Client (SSL verification off so the sandbox can reach Google).
    """

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        timeout: float = 30.0,
        max_retries: int = 2,
        transport: Any | None = None,
    ) -> None:
        if not api_key:
            raise ProviderError("Embedding provider requires an API key")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._max_retries = max_retries
        self._transport = transport
        self.dimensions = _DIMS

    def _client(self) -> httpx.Client:
        if self._transport is not None:
            return httpx.Client(transport=self._transport)
        return httpx.Client(verify=False)

    def _post(self, url: str, body: dict) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                with self._client() as client:
                    response = client.post(
                        url,
                        json=body,
                        headers={"x-goog-api-key": self._api_key},
                        timeout=self._timeout,
                    )
                _raise_for_status(response)
                return response
            except httpx.RequestError as exc:
                last_error = exc
                logger.warning("embedding network failure (attempt %d): %s", attempt + 1, exc)
            if attempt < self._max_retries:
                import time

                time.sleep(0.5 * (2**attempt))
        raise ProviderError(f"Embedding provider unreachable: {last_error}")

    def embed(self, text: str) -> list[float]:
        """Embed one text string -> vector."""
        response = self._post(
            f"{EMBED_ENDPOINT}/{self._model}:embedContent",
            {"model": f"models/{self._model}", "content": {"parts": [{"text": text}]}},
        )
        try:
            values = response.json()["embedding"]["values"]
        except (KeyError, TypeError) as exc:
            raise ProviderError(f"Unexpected embedding response: {response.text[:200]}") from exc
        return [float(v) for v in values]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of strings in one call (limit 100)."""
        if not texts:
            return []
        payload = {
            "model": f"models/{self._model}",
            "requests": [{"model": f"models/{self._model}", "content": {"parts": [{"text": t}]}} for t in texts],
        }
        response = self._post(f"{EMBED_ENDPOINT}/{self._model}:batchEmbedContents", payload)
        try:
            rows = response.json()["embeddings"]
        except (KeyError, TypeError) as exc:
            raise ProviderError(f"Unexpected batch embedding response: {response.text[:200]}") from exc
        return [[float(v) for v in row["values"]] for row in rows]