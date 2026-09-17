# Metadata extraction for a document.
#
# The system preserves source metadata so every chunk can be traced back to
# an original source (see source-authority and document metadata in Phase 1
# architecture).

from datetime import datetime, timezone


def build_metadata(
    *,
    source_url: str,
    title: str | None = None,
    source_type: str = "web",
    document_type: str = "web_page",
) -> dict:
    """Return a metadata dict for a parsed document."""
    return {
        "source_url": source_url,
        "title": title,
        "source_type": source_type,
        "document_type": document_type,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    }
