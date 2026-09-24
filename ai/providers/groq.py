# ai/providers/groq.py - Groq (OpenAI-compatible chat completions) provider.
#
# Why: free-tier Groq gives an extremely fast, high-quality hosted model
# (default: llama-3.3-70b-versatile) through the OpenAI-compatible endpoint.
#
# Security invariant (same as Gemini): the API key travels ONLY in the
# Authorization header, never in the URL or query string.
#
# Contract: `GroqClient.generate(system_prompt, user_prompt) -> str`, raising
# the same typed `ProviderError` subclasses as the Gemini client so the caller
# (`app/services/chat.py`) applies identical retry/degrade logic.

import json
import time
from typing import Any

import httpx

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# Statuses where retrying can actually help (transient overload / mid-flight).
_RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}

_log = __import__("logging").getLogger(__name__)


def _extract_choices(payload: dict) -> str | None:
    """Pull the assistant text out of a chat.completions response."""
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None
    if isinstance(content, str) and content.strip():
        return content.strip()
    return None


# Shared, typed provider errors (same classes as Gemini so `app/services/chat.py`
# applies one identical degrade policy regardless of provider).
from ai.providers.errors import (  # noqa: F401
    ProviderAuthError,
    ProviderError,
    ProviderRateLimited,
    ProviderUnavailable,
)
class GroqClient:
    """Small, typed wrapper around Groq's /chat/completions endpoint."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        timeout: float = 30.0,
        max_retries: int = 2,
        transport: httpx.BaseTransport | None = None,
        temperature: float = 0.3,
        max_output_tokens: int = 700,
    ) -> None:
        if not api_key:
            raise ProviderAuthError("A Groq API key is required")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        # `max_retries` counts *additional* attempts after the first one.
        self._max_retries = max(0, max_retries)
        self._transport = transport
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Send one chat completion and return the model's text.

        Raises a `ProviderError` subclass on failure so callers can decide
        whether to retry, degrade, or surface the error.
        """
        body: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self._temperature,
            "max_tokens": self._max_output_tokens,
            "stream": False,
        }
        # Key lives in the header, never the URL/query string.
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "content-type": "application/json",
        }

        attempts = self._max_retries + 1
        last_error: ProviderError | None = None

        for attempt in range(attempts):
            try:
                with httpx.Client(
                    timeout=self._timeout, transport=self._transport
                ) as client:
                    response = client.post(GROQ_ENDPOINT, json=body, headers=headers)
            except httpx.HTTPError as exc:
                # Network-level failure (DNS, TLS, timeout). Retryable.
                last_error = ProviderUnavailable(f"Could not reach the provider: {exc}")
                if attempt < attempts - 1:
                    self._sleep(attempt)
                    continue
                raise last_error from exc

            if response.status_code == 200:
                try:
                    payload = response.json()
                except json.JSONDecodeError as exc:
                    raise ProviderUnavailable(
                        "The provider returned a malformed response"
                    ) from exc
                text = _extract_choices(payload)
                if text is None:
                    raise ProviderUnavailable(
                        "The provider returned an empty or malformed response"
                    )
                return text

            error = self._map_error(response)
            last_error = error
            if response.status_code not in _RETRYABLE_STATUS_CODES:
                raise error
            if attempt < attempts - 1:
                self._sleep(attempt)
                continue
            raise error

        raise last_error or ProviderUnavailable("Provider request failed")

    def _sleep(self, attempt: int) -> None:
        delay = min(0.5 * (2 ** attempt), 4.0)
        _log.warning("Groq provider retry %s in %.2fs", attempt + 1, delay)
        time.sleep(delay)

    def _map_error(self, response: httpx.Response) -> ProviderError:
        """Translate an HTTP status into a typed, user-safe error."""
        detail = ""
        try:
            payload = response.json()
            if isinstance(payload, dict):
                error = payload.get("error")
                if isinstance(error, dict):
                    detail = str(error.get("message") or "")
                elif isinstance(error, str):
                    detail = error
        except json.JSONDecodeError:
            detail = response.text[:200]
        detail = detail[:300]
        code = response.status_code
        if code in (401, 403):
            return ProviderAuthError(f"Groq rejected the API key: {detail}".strip())
        if code == 429:
            return ProviderRateLimited("Groq free-tier rate limit exceeded")
        if code in (400, 404, 422):
            return ProviderError(f"Groq rejected the request (model or payload): {detail}".strip())
        return ProviderUnavailable(f"Groq unavailable ({code}): {detail}".strip())