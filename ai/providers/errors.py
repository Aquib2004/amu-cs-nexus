# ai/providers/errors.py - shared provider error hierarchy.
#
# Both the Gemini and Groq clients raise these same types, so the caller
# (`app/services/chat.py`) applies one identical retry/degrade policy no matter
# which provider is configured.

class ProviderError(RuntimeError):
    """Base class for all model-provider failures raised by provider clients."""


class ProviderAuthError(ProviderError):
    """The API key is missing, invalid, or lacks permission (401/403)."""


class ProviderRateLimited(ProviderError):
    """The provider asked us to slow down (HTTP 429)."""


class ProviderUnavailable(ProviderError):
    """The provider failed server-side or was unreachable (5xx / network)."""