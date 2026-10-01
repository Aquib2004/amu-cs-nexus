# Crawler: fetch official source pages over HTTP.
#
# A client may be injected so tests can use httpx.MockTransport (no network).

import ssl

import httpx


def _tls_context() -> ssl.SSLContext:
    """Return the shared outbound TLS context.

    Imported lazily because this module is also used standalone (and by tests)
    where the backend package may not be importable yet. The AMU API omits its
    GlobalSign intermediate from the handshake, so the backend's platform trust
    store is required; if it cannot be imported we fall back to the Python
    default context, which still verifies certificates.
    """
    try:
        from app.core.tls import tls_context
    except Exception:
        return ssl.create_default_context()
    return tls_context()


def fetch_html(url: str, timeout: float = 15.0, client: httpx.Client | None = None) -> str:
    """Fetch a URL and return its HTML, raising on an error response."""
    if client is not None:
        response = client.get(url)
    else:
        # Platform trust store: the AMU API omits its GlobalSign intermediate.
        response = httpx.get(
            url, timeout=timeout, follow_redirects=True, verify=_tls_context()
        )
    response.raise_for_status()
    return response.text
