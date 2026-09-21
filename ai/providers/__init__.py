# ai/providers/__init__.py - LLM provider clients behind one small, typed surface.
#
# Why a separate package? Answer *generation* (ai/rag) and *provider access*
# (ai/providers) change for different reasons: swapping the model vendor must
# not touch retrieval, and credentials must live in exactly one place.

from ai.providers.gemini import (
    GeminiClient,
    ProviderAuthError,
    ProviderError,
    ProviderRateLimited,
    ProviderUnavailable,
)

__all__ = [
    "GeminiClient",
    "ProviderError",
    "ProviderRateLimited",
    "ProviderAuthError",
    "ProviderUnavailable",
]
