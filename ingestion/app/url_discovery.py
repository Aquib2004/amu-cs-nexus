# URL discovery: extract candidate URLs to crawl from an HTML page.
#
# Relative links are resolved against a base URL to produce absolute links.

from urllib.parse import urljoin

from bs4 import BeautifulSoup


def discover_links(base_url: str, html: str) -> list[str]:
    """Return de-duplicated absolute http(s) links found in the HTML."""
    soup = BeautifulSoup(html, "html.parser")
    urls: list[str] = []
    for tag in soup.find_all("a", href=True):
        absolute = urljoin(base_url, tag["href"].strip())
        if absolute.startswith(("http://", "https://")):
            urls.append(absolute)

    # Preserve order but remove duplicates.
    seen: set[str] = set()
    unique: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique
