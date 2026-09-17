# Crawler: fetch official source pages over HTTP.
#
# A client may be injected so tests can use httpx.MockTransport (no network).

import httpx


def fetch_html(url: str, timeout: float = 15.0, client: httpx.Client | None = None) -> str:
    """Fetch a URL and return its HTML, raising on an error response."""
    if client is not None:
        response = client.get(url)
    else:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
    response.raise_for_status()
    return response.text
