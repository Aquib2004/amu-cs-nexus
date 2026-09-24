# Provider tests for GroqClient (no network: httpx.MockTransport).

import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.providers import (  # noqa: E402
    GroqClient,
    ProviderAuthError,
    ProviderError,
    ProviderRateLimited,
    ProviderUnavailable,
)


def _client(status: int, payload: dict | None = None) -> GroqClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=payload or {})

    return GroqClient(
        api_key="gsk_test123",
        max_retries=0,
        temperature=0.0,
        transport=httpx.MockTransport(handler),
    )


def test_missing_key_raises() -> None:
    with pytest.raises(ProviderAuthError):
        GroqClient(api_key="")


def test_generate_returns_assistant_text() -> None:
    client = _client(
        200,
        {"choices": [{"message": {"content": "The MCA notice was published in 2024. [1]"}}]},
    )
    assert client.generate("sys", "usr") == "The MCA notice was published in 2024. [1]"


def test_generate_posts_bearer_header_and_messages() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["auth"] = request.headers.get("authorization")
        captured["body"] = request.content.decode()
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok [1]"}}]})

    client = GroqClient(api_key="gsk_abc123", max_retries=0,
                        transport=httpx.MockTransport(handler))
    client.generate("the system prompt", "the user question")
    assert captured["auth"] == "Bearer gsk_abc123"
    assert "the system prompt" in captured["body"]
    assert "the user question" in captured["body"]


def test_malformed_response_raises_unavailable() -> None:
    client = _client(200, {"choices": []})
    with pytest.raises(ProviderUnavailable):
        client.generate("s", "u")


def test_auth_error_maps_to_provider_auth() -> None:
    client = _client(401, {"error": {"message": "invalid key"}})
    with pytest.raises(ProviderAuthError):
        client.generate("s", "u")


def test_rate_limit_maps_to_provider_rate_limited() -> None:
    client = _client(429, {})
    with pytest.raises(ProviderRateLimited):
        client.generate("s", "u")


def test_model_not_found_maps_to_base_provider_error() -> None:
    client = _client(404, {"error": {"message": "model not found"}})
    with pytest.raises(ProviderError):
        client.generate("s", "u")