# HTML parsing: convert HTML documents into plain text.
#
# BeautifulSoup parses the HTML and we drop script/style blocks before
# extracting text so boilerplate does not pollute the content.

from bs4 import BeautifulSoup


def extract_title(html: str) -> str | None:
    """Return the page <title>, trimmed, or None when absent."""
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return None


def html_to_text(html: str) -> str:
    """Convert HTML to plain text, removing script/style/noise blocks."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ")
