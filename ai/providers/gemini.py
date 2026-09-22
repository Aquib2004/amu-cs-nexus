# ai/providers/gemini.py - Google Gemini client for the "yourobo" assistant.
#
# Why this file exists: the assistant needs one place that knows how to talk to
# the model vendor. Everything else (retrieval, prompts, API routes) stays
# vendor-agnostic, so swapping providers touches only this module.
#
# Verified contract (Google Generative Language REST API v1beta):
#   POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
#   Header: x-goog-api-key: <API_KEY>          <- key in a HEADER, never the URL
#   Body:   {"systemInstruction": {...}, "contents": [{...}], "generationConfig": {...}}
#   Reply:  candidates[0].content.parts[].text  (+ finishReason)
#
# The API key is passed in a header on purpose: query strings land in proxy and
# server logs, so a key in the URL is a key that leaks.

from __future__ import annotations

import logging
import random
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"

# Bounded retry policy. We only retry failures that can plausibly succeed on a
# second attempt (429 / 5xx / network). Retrying a 400 or 403 can never help and
# would just burn the user's quota, so those fail immediately.
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_BACKOFF_SECONDS = 8.0


class ProviderError(RuntimeError):
    """Base class for all model-provider failures raised by this module."""


class ProviderAuthError(ProviderError):
    """The API key is missing, invalid, or lacks permission (401/403)."""


class ProviderRateLimited(ProviderError):
    """The provider asked us to slow down (HTTP 429)."""


class ProviderUnavailable(ProviderError):
    """The provider failed server-side or was unreachable (5xx / network)."""


def _backoff_delay(attempt: int, retry_after: float | None) -> float:
    """Work out how long to wait before retry number `attempt` (0-based).

    We honour the server's `Retry-After` when it sends one, otherwise we use
    exponential backoff with jitter. Jitter matters: without it, many clients
    that were rate-limited together would retry in lockstep and get limited
    again. The wait is always capped so a hostile header cannot stall a request.
    """
    if retry_after is not None and retry_after >= 0:
        return min(retry_after, MAX_BACKOFF_SECONDS)
    # 0.5s, 1s, 2s, ... with up to 50% extra random jitter.
    base = 0.5 * (2**attempt)
    return min(base + random.uniform(0, base / 2), MAX_BACKOFF_SECONDS)


def _parse_retry_after(response: httpx.Response) -> float | None:
    """Read a numeric `Retry-After` header, ignoring the HTTP-date form."""
    raw = response.headers.get("retry-after")
    if not raw:
        return None
    try:
        return float(raw.strip())
    except ValueError:
        return None


def _extract_text(payload: dict[str, Any]) -> str | None:
    """Pull the first text part out of a generateContent response.

    Written defensively: a malformed or empty reply must produce `None`, not an
    exception, so the caller can degrade cleanly instead of returning a 500.
    """
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return None
    content = candidates[0].get("content")
    if not isinstance(content, dict):
        return None
    parts = content.get("parts")
    if not isinstance(parts, list):
        return None
    chunks = [p.get("text", "") for p in parts if isinstance(p, dict)]
    text = "".join(chunks).strip()
    return text or None

class GeminiClient:
    """Small, typed wrapper around Gemini's `generateContent` endpoint."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.6-flash",
        timeout: float = 20.0,
        max_retries: int = 2,
        transport: httpx.BaseTransport | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 512,
    ) -> None:
        if not api_key:
            raise ProviderAuthError("A Gemini API key is required")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        # `max_retries` counts *additional* attempts after the first one.
        self._max_retries = max(0, max_retries)
        # Injecting a transport is what lets tests exercise retries and error
        # mapping without ever making a real network call.
        self._transport = transport
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Send one prompt and return the model's text.

        Raises a `ProviderError` subclass on failure so callers can decide
        whether to retry, degrade, or surface the error.
        """
        url = f"{GEMINI_ENDPOINT}/{self._model}:generateContent"
        body: dict[str, Any] = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": self._temperature,
                "maxOutputTokens": self._max_output_tokens,
            },
        }
        # The key travels in a header; headers are not written to access logs
        # the way query strings commonly are.
        headers = {
            "x-goog-api-key": self._api_key,
            "content-type": "application/json",
        }

        attempts = self._max_retries + 1
        last_error: ProviderError | None = None

        for attempt in range(attempts):
            try:
                with httpx.Client(
                    timeout=self._timeout, transport=self._transport
                ) as client:
                    response = client.post(url, json=body, headers=headers)
            except httpx.HTTPError as exc:
                # Network-level failure (DNS, TLS, timeout). Retryable.
                last_error = ProviderUnavailable(f"Could not reach the provider: {exc}")
                if attempt < attempts - 1:
                    self._sleep(attempt, None)
                    continue
                raise last_error from exc

            if response.status_code == 200:
                text = _extract_text(response.json() if response.content else {})
                if text is None:
                    raise ProviderUnavailable(
                        "The provider returned an empty or malformed response"
                    )
                return text

            error = self._map_error(response)
            last_error = error

            # Only retry what can actually improve.
            if response.status_code not in RETRYABLE_STATUS_CODES:
                raise error
            if attempt < attempts - 1:
                self._sleep(attempt, _parse_retry_after(response))
                continue
            raise error

        # Defensive: the loop above always returns or raises.
        raise last_error or ProviderUnavailable("Provider request failed")

    def _sleep(self, attempt: int, retry_after: float | None) -> None:
        delay = _backoff_delay(attempt, retry_after)
        logger.warning("Provider retry %s in %.2fs", attempt + 1, delay)
        time.sleep(delay)

    def _map_error(self, response: httpx.Response) -> ProviderError:
        """Translate an HTTP status into a typed, user-safe error.

        Provider messages are quoted but truncated: enough to debug, short
        enough that we never echo a wall of vendor JSON to the browser.
        """
        detail = ""
        try:
            payload = response.json()
            if isinstance(payload, dict):
                message = payload.get("error", {})
                if isinstance(message, dict):
                    detail = str(message.get("message", ""))
                elif isinstance(message, str):
                    detail = message
        except ValueError:
            detail = (response.text or "")[:200]
        detail = detail[:300]

        status = response.status_code
        if status in (401, 403):
            return ProviderAuthError(f"Provider rejected the API key ({status})")
        if status == 429:
            return ProviderRateLimited(f"Provider rate limit reached (429): {detail}")
        if status == 404:
            return ProviderError(f"Model '{self._model}' was not found (404): {detail}")
        if status >= 500:
            return ProviderUnavailable(f"Provider error ({status}): {detail}")
        return ProviderError(f"Provider rejected the request ({status}): {detail}")
